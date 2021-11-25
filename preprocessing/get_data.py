# Last updated: 30 October 2021
# Script to collect data from the sources.
# Author(s): Ansel Lim.

import datetime
import json
import os
import pickle
import time
import urllib.request
import pandas as pd
import requests
from dotenv import load_dotenv

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