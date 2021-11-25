# Ansel Lim, ansel@gatech.edu
# 31 Oct - 25 Nov 2021
# Collected code for obtaining/preprocessing data.
# Part of this code was previously run on notebooks in Google Colab, but I have put together the code here for easier reference.

import pandas as pd
import numpy as np
import requests
import os
import re
import fiona
import geopandas as gpd
import datetime
import json
import pickle
import time
import urllib.request
from dotenv import load_dotenv
from SVY21 import SVY21
from collections import Counter

os.chdir("../data/raw")

#################################################################################################
#################################################################################################
###### Part 1: Get private condominium data from Urban Redevelopment Authority's API ############
#################################################################################################
#################################################################################################

class DataLoader:
    def __init__(self, ura_api_key, lta_api_key, regenerate_ura_token=True):
        self.ura_api_key = ura_api_key
        self.ura_token = None
        self.lta_api_key = lta_api_key
        self.ura_data = None
        self.bus_stops = None
        self.geospatial = {}
        self.taxi_availability = None
        self.taxi_stands = None
        self.carpark_availability = None
        self.bicycle_parking = None
        self.timestamp = str(datetime.datetime.now())

        if regenerate_ura_token:
            ura_token = self.get_ura_token()
            self.ura_token = ura_token
            print("Initialized a DataLoader object. A new token for URA API was generated during initialization.")
        else:
            ura_token = input("Enter token for URA API")
            self.ura_token = ura_token
            print("Initialized a DataLoader object. Used a specified old token for URA API.")
        return None

    # get token from URA API
    def get_ura_token(self):
        req = urllib.request.Request("https://www.ura.gov.sg/uraDataService/insertNewToken.action",
                                     headers={"AccessKey": self.ura_api_key})
        with urllib.request.urlopen(req) as response:
            res = response.read()
            res = json.loads(res)
            token = res['Result']
            response.close()
        print(
            "Generated a new token for URA API (pls record this somewhere; it will not be written to a file):\n{}".format(
                token))
        return token

    def sleep(self, duration=60):
        print("Sleeping for {} seconds".format(duration))
        time.sleep(duration)

    # get property transaction data from URA API
    def load_ura_transactions(self):
        print("Starting to load URA transactions")
        start = time.time()
        data = {}
        data[1],data[2],data[3],data[4] = None,None,None,None
        for i in range(1, 5):
            # Batch 3 is giving problems, so skip it
            if i==3:
                print("Skipping batch 3")
                continue

            print("Loading batch {} of 4 for URA transaction data".format(i))
            url = "https://www.ura.gov.sg/uraDataService/invokeUraDS"
            params = {"service": "PMI_Resi_Transaction",
                      "batch": str(i)}
            headers = {"Token": self.ura_token,
                       "AccessKey": self.ura_api_key,
                       "User-Agent": "PostmanRuntime/7.26.8",  # for some weird reason, need to pretend we are Postman
                       "Connection":"keep-alive",
                       "Accept":"*/*",
                       "Accept-Encoding":"gzip, deflate, br"
                       }
            response = requests.get(url, params=params, headers=headers)
            res = response.json()
            data[i] = res
            response.close()
            self.sleep(30)
        self.ura_data = data
        end = time.time()
        print("Completed loading URA transaction data: took {} seconds".format(end - start))
        return data

    def load_bus_stops(self):
        print("Starting to load bus stop data")
        start = time.time()
        url = "http://datamall2.mytransport.sg/ltaodataservice/BusStops"
        headers = {"AccountKey": self.lta_api_key}
        response = requests.get(url, headers=headers)
        res = response.json()
        self.bus_stops = res
        end = time.time()
        response.close()
        print("Completed loading bus stop data: took {} seconds".format(end - start))
        return response

    def load_taxi_availability(self):
        print("Starting to load taxi availability data")
        start = time.time()
        url = "http://datamall2.mytransport.sg/ltaodataservice/Taxi-Availability"
        headers = {"AccountKey": self.lta_api_key}
        response = requests.get(url, headers=headers)
        res = response.json()
        self.taxi_availability = res
        end = time.time()
        response.close()
        print("Completed loading taxi availability data: took {} seconds".format(end - start))
        return response

    def load_taxi_stands(self):
        print("Starting to load taxi stand data")
        start = time.time()
        url = "http://datamall2.mytransport.sg/ltaodataservice/TaxiStands"
        headers = {"AccountKey": self.lta_api_key}
        response = requests.get(url, headers=headers)
        res = response.json()
        self.taxi_stands = res
        end = time.time()
        response.close()
        print("Completed loading taxi stand data: took {} seconds".format(end - start))
        return response

    def load_carpark_availability(self):
        print("Starting to load carpark availability data")
        start = time.time()
        url = "http://datamall2.mytransport.sg/ltaodataservice/CarParkAvailabilityv2"
        headers = {"AccountKey": self.lta_api_key}
        response = requests.get(url, headers=headers)
        res = response.json()
        self.carpark_availability = res
        end = time.time()
        response.close()
        print("Completed loading carpark availability data: took {} seconds".format(end - start))
        return response

    # This API endpoint doesn't seem to exist, even though it's in the documentation.
    # def load_bicycle_parking(self):
    #     print("Starting to load bicycle parking data")
    #     start = time.time()
    #     url = "http://datamall2.mytransport.sg/ltaodataservice/BicycleParkingv2"
    #     headers = {"AccountKey": self.lta_api_key}
    #     response = requests.get(url, headers=headers).json()
    #     self.bicycle_parking = response
    #     end=time.time()
    #     print("Completed loading bicycle parking data: took {} seconds".format(end - start))
    #     return response

    def load_geospatial(self, geospatial_layer_id=None):
        if not geospatial_layer_id:
            raise ValueError("'geospatial_layer_id' cannot be None; pls specify a geospatial layer")
        print("Starting to load bicycle parking data for the geospatial layer {}".format(geospatial_layer_id))
        start = time.time()
        url = "http://datamall2.mytransport.sg/ltaodataservice/GeospatialWholeIsland"
        headers = {"AccountKey": self.lta_api_key}
        params = {"ID": geospatial_layer_id}
        response = requests.get(url, headers=headers, params=params)
        res = response.json()
        if not self.geospatial:
            self.geospatial = {}
        self.geospatial[geospatial_layer_id] = res
        end = time.time()
        response.close()
        print("Completed loading geospatial layer {}: took {} seconds".format(geospatial_layer_id, end - start))
        return response

    def save_data(self, dest="cached_data"):
        with open(dest, "wb") as file:
            data = self.__dict__
            for item in ["ura_api_key", "ura_token", "lta_api_key"]:
                del data[item]
            pickle.dump(data, file)
            file.close()

# API keys
load_dotenv()
URA_API_KEY = str(os.environ.get("URA_API_KEY"))
LTA_API_KEY = str(os.environ.get("LTA_API_KEY"))

# download data
loader = DataLoader(URA_API_KEY, LTA_API_KEY, regenerate_ura_token=True)
loader.sleep(30)  # need some time before generated URA token may be used in API calls.
loader.load_ura_transactions()
loader.load_bus_stops()
loader.load_taxi_availability()
loader.load_taxi_stands()
loader.load_carpark_availability()
# loader.load_bicycle_parking() # bicycle parking API doesn't exist (404 error)
items = ["TrainStation", "BusStopLocation",
         "TaxiStand",
         "TrainStationExit"
         # "ERPGantry",
         "SchoolZone", "SilverZone", "CyclingPath", "CoveredLinkWay", "Footpath",
         # "PedestrainOverheadbridge_UnderPass",
         ]
for item in items:
    loader.load_geospatial(item)

# save data (pickle the object and save to disk)
loader.save_data(dest="cached_data")

#####################################################################################################
#####################################################################################################
###### Part 2: Process private condominium data from Urban Redevelopment Authority's API ############
#####################################################################################################
#####################################################################################################

class DataProcessor:
    def __init__(self, pickled_loader="./data/cached_data"):
        self.pickled_loader = pickled_loader
        self.data = None

    def load(self):
        cls = pickle.load(open(self.pickled_loader, "rb"))
        self.data = cls
        return cls

class DataProcessor:
    def __init__(self, pickled_loader="./data/cached_data"):
        self.pickled_loader = pickled_loader
        self.data = None

    def load(self):
        cls = pickle.load(open(self.pickled_loader, "rb"))
        self.data = cls
        return cls

# create a data processor object to load and process the data
data_processor = DataProcessor('./data/cached_data')
data_processor.load()

# example: to view bus stops data
bus_stops = data_processor.data['bus_stops']
# print(bus_stops)

# process data --> csv
ura_data_1 = data_processor.data["ura_data"][1]["Result"]
ura_data_2 = data_processor.data["ura_data"][2]["Result"]
# ura_data_3 = data_processor.data["ura_data"][3]["Result"]   # FOR SOME REASON, BATCH 3 IS GIVING PROBLEMS. Comment it out...
ura_data_4 = data_processor.data["ura_data"][4]["Result"]
ura_1 = pd.DataFrame.from_dict(ura_data_1)
ura_2 = pd.DataFrame.from_dict(ura_data_2)
# ura_3 = pd.DataFrame.from_dict(ura_data_3)                  # FOR SOME REASON, BATCH 3 IS GIVING PROBLEMS. Comment it out...
ura_4 = pd.DataFrame.from_dict(ura_data_4)
ura = pd.concat([ura_1,ura_2,
                 #ura_3,                                     # FOR SOME REASON, BATCH 3 IS GIVING PROBLEMS. Comment it out...
                 ura_4])
ura.to_csv("ura_unconverted.csv")

# process data other than the URA private residential property transaction data

bus_stops = data_processor.data['bus_stops']['value']
taxi_stands=data_processor.data['taxi_stands']['value']
carparks=data_processor.data['carpark_availability']['value']
# train_stations=data_processor.data['geospatial']['TrainStation']
# cycling_paths=data_processor.data['geospatial']['CyclingPath']
# train_station_exits=data_processor.data['geospatial']['TrainStationExit']
# school_zones=data_processor.data['geospatial']['SchoolZone']

df_bus_stops = pd.DataFrame.from_dict(bus_stops)
df_taxi_stands = pd.DataFrame.from_dict(taxi_stands)
df_carparks = pd.DataFrame.from_dict(carparks)
df_carparks[['latitude', 'longitude']] = df_carparks['Location'].str.split(' ', 1, expand=True)

df_bus_stops.to_csv("./data/bus_stops.csv")
df_taxi_stands.to_csv("./data/taxi_stands.csv")
df_carparks.to_csv("./data/carparks.csv")

#############################################################################################################
###############################Part 3: manually process URA condo data#######################################
################################process_manually_obtained_URA_data.py########################################
#############################################################################################################
#############################################################################################################

# https://stackoverflow.com/questions/1518522/find-the-most-common-element-in-a-list
def most_common(lst):
    data = Counter(lst)
    return data.most_common(1)[0][0]

#######################

batch1_json = open("../data/raw/batch1.json", 'r')
batch1 = json.load(batch1_json)

batch2_json = open("../data/raw/batch2.json", 'r')
batch2 = json.load(batch2_json)

#batch3_json = open("./ura_data/batch2.json",'r') ## Batch 3 is the problematic batch
#batch3 = json.load(batch3_json) ## Batch 3 is the problematic batch

batch4_json = open("../data/raw/batch4.json", 'r')
batch4 = json.load(batch4_json)

data = batch1['Result']+batch2['Result']+batch4['Result'] #+batch3['Result'] ## Batch 3 is the problematic batch

print('Number of properties',len(data)) #________

properties_with_SVY21_coordinates = [property for property in data if 'x' in property.keys() and 'y' in property.keys()]

print('Number of properties with coordinates',len(properties_with_SVY21_coordinates)) #________

coordinate_transformer = SVY21()

for property in properties_with_SVY21_coordinates:

    # Convert SVY21 coordinates into latitude and longitude
    x,y = float(property['x']),float(property['y'])
    lat,long = coordinate_transformer.computeLatLon(x, y)
    del property['x']
    del property['y']
    property['lat']=lat
    property['long']=long

    # Calculate avg price per sqm
    transactions = property['transaction']
    num_transactions = len(transactions)
    price_per_sqm = list(map(lambda transac: float(transac['price']) / float(transac['area']), transactions))
    avg_price_per_sqm = sum(price_per_sqm)/len(price_per_sqm)
    property['avg_price_per_sqm'] = avg_price_per_sqm

    # Get district
    district_list = map(lambda transac:transac['district'],transactions)
    district = most_common(district_list)
    property['district'] = district

    # Get commonest tenure
    tenure_list = map(lambda transac: transac['tenure'], transactions)
    tenure = most_common(tenure_list)
    property['commonest_tenure'] = tenure

    del property['transaction']

df = pd.DataFrame.from_dict(properties_with_SVY21_coordinates)
df.to_csv("./data/ura.csv")


#####################################################################################################
#####################################################################################################
##################################Part 4: Get other datasets#########################################
#####################################################################################################
#####################################################################################################

###### Get public housing (HDB) data from https://data.gov.sg/dataset/resale-flat-prices. Calculate average price per square meter. Add latitude and longitude information based on property address by making API calls to OneMap. #######

hdb = pd.read_csv("resale-flat-prices-based-on-registration-date-from-jan-2017-onwards.csv")
hdb["block"] = hdb["block"] + " " + hdb["street_name"]
hdb['price_per_sqm'] = hdb['resale_price'] / hdb['floor_area_sqm']
hdb_aggregated = hdb.groupby('block').mean()[['floor_area_sqm', 'resale_price', 'price_per_sqm']].reset_index()

# Function to get latitude and longitude based on an HDB block's address
def getLatLong_HDB(x):
    address = x["block"]
    matches = requests.get(
        "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            address)).json()['results']
    try:
        first_match = matches[0]
        lat, long = first_match['LATITUDE'], first_match['LONGITUDE']
        isLatLongAvailable = 'True'
        return (lat, long, isLatLongAvailable)
    except IndexError:
        isLatLongAvailable = 'False'
        return ("unknown", "unknown", isLatLongAvailable)


hdb_aggregated_with_lat_long = pd.concat(
    [hdb_aggregated, hdb_aggregated.apply(getLatLong_HDB, axis=1, result_type="expand")], axis=1)
hdb_aggregated_with_lat_long = hdb_aggregated_with_lat_long.rename(
    columns={0: "lat", 1: "long", 2: "isLatLongAvailable"})

hdb_aggregated_with_lat_long.to_csv("./hdb_aggregated.csv")

###### Get secondary school data. Add latitude and longitude information. #######

schools = pd.read_csv("./general-information-of-schools.csv")
primary = schools[schools['mainlevel_code'] == 'PRIMARY']
secondary = schools[schools['mainlevel_code'] == 'SECONDARY']


def getLatLong_Schools(x):
    postal_code = x['postal_code']
    matches = requests.get(
        "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            postal_code)).json()['results']
    if len(matches) >= 1:
        first_match = matches[0]
        lat, long = first_match['LATITUDE'], first_match['LONGITUDE']
        isLatLongAvailable = 'True'
        return (lat, long, isLatLongAvailable)
    else:
        return ("NA", "NA", "False")


secondary = pd.concat([secondary, secondary.apply(getLatLong_Schools, axis=1, result_type='expand').rename(
    mapper={0: 'lat', 1: 'long', 2: 'isLatLongAvailable'}, axis=1)], axis=1)

secondary[secondary['isLatLongAvailable'] == 'True'].to_csv("./secondary_schools.csv")

###### Process supermarket data from https://data.gov.sg/dataset/listing-of-licensed-supermarkets. Add latitude and longitude information. #######

supermarkets = pd.read_csv("./listing-of-supermarkets.csv")

def getLatLong_Supermarkets(x):
    address = x['premise_address']
    postal_code = re.findall(r'S[(][0-9]{6}[)]', address)[0].lstrip("S(").rstrip(")")
    matches = requests.get(
        "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            postal_code)).json()['results']
    try:
        first_match = matches[0]
        lat, long = first_match['LATITUDE'], first_match['LONGITUDE']
        isLatLongAvailable = 'True'
        return (lat, long, isLatLongAvailable)
    except IndexError:
        isLatLongAvailable = 'False'
        return ("unknown", "unknown", isLatLongAvailable)


supermarkets = pd.concat([supermarkets, supermarkets.apply(getLatLong, axis=1, result_type='expand').rename(
    mapper={0: 'lat', 1: 'long', 2: 'isLatLongAvailable'}, axis=1)], axis=1)

supermarkets = supermarkets.reset_index()

supermarkets.to_csv("./supermarkets.csv")

##### Process over 34,000 rows of F&B establishments ('eating establishments') from https://data.gov.sg/dataset/eating-establishments #####

gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
df = gpd.read_file('eating-establishments.kml', driver='KML')
df['long'] = df['geometry'].x
df['lat'] = df['geometry'].y


def getBusinessName(x):
    match = re.findall(r'<th>BUSINESS_NAME</th> <td>[a-z0-9A-Z]*</td>', x['Description'])
    if len(match) >= 1:
        return match[0].lstrip('<th>BUSINESS_NAME</th> <td>').rstrip('</td>')
    else:
        return "Unknown business name"


df['business_name'] = df.apply(getBusinessName, axis=1)

df.to_csv('./eating_establishments.csv')

##### Process a dataset of parks in Singapore from https://data.gov.sg/dataset/parks #####

gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
df = gpd.read_file('parks-kml.kml', driver='KML')
df['long'] = df['geometry'].x
df['lat'] = df['geometry'].y


def getParkName(x):
    match = re.findall(r'<th>NAME<\/th> <td>[a-z0-9A-Z ]*<\/td>', x['Description'])
    if len(match) >= 1:
        return match[0].lstrip("<th>NAME</th> <td>").rstrip("</td>")
    else:
        return "Unknown park name"


df.loc[:, 'park_name'] = df.apply(getParkName, axis=1)

df.to_csv('./parks.csv')






