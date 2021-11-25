
############################################################################################################
############################################################################################################
#################Only the scoring part of add_quality_data (no API calls here)##############################
############################################################################################################
############################################################################################################

import numpy as np
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import re
from geopy.distance import geodesic
import time
from sklearn.preprocessing import MinMaxScaler

# import warnings
# warnings.filterwarnings("ignore")

# Load API Key
load_dotenv()
GOOGLE_API_KEY = str(os.environ.get("GOOGLE_API_KEY"))

# Function to get information from Google Places API
def get_information(name):
    '''
    :param name: a string, e.g. 'Nanyang Primary School'
    :return: Google Places API place ID, number of ratings, and average rating (maximum is 5 stars)
    '''
    matches = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json",
                           params={'input': name, 'inputtype': 'textquery',
                                   'fields': 'name,place_id,rating,user_ratings_total', 'language': 'en',
                                   'locationbias': 'rectangle:1.3057418,103.9082193|1.427759, 104.045392',
                                   'key': GOOGLE_API_KEY})
    top_match = matches.json()['candidates']
    if len(top_match)<1:
        return np.nan,np.nan,np.nan
    else:
        top_match = top_match[0]
        place_id = top_match.get('place_id')
        num_ratings = top_match.get('user_ratings_total')
        avg_rating = top_match.get('rating')
        return place_id,num_ratings,avg_rating

def remove_postal_code(address):
    postal_code = re.findall(pattern=r'[S][(][0-9]{6}[)]', string=address)[:1]
    if len(postal_code)>0:
        postal_code = postal_code[0]
        return address.rstrip(postal_code).rstrip(", ")
    else:
        return address

def get_postal_code(address):
    matches = requests.get(
        "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            address)).json()['results']
    try:
        first_match = matches[0]
        return first_match['POSTAL']
    except IndexError:
        return np.nan

############################
############################
############################
print("Start of script",time.time())
print("Start work to create combined dataframe of properties and features",time.time())

df_condo = pd.read_csv('../data/processed/df.csv')
df_hdb = pd.read_csv('../data/processed/df_hdb.csv')

df_condo.drop(columns = ['num_eating_establishments'], inplace=True)
df_condo = df_condo[['street', 'project', 'marketSegment', 'lat', 'long', 'avg_price_per_sqm', 'district',
                     'commonest_tenure', 'num_malls', 'num_taxi_stands','num_primary_schools',
                     'num_mrt', 'num_hawker', 'num_carparks','num_bus_stops', 'num_chas_clinics',
                     'num_sports_facilities', 'num_community_centers', 'num_supermarkets', 'num_secondary_schools',
                     'num_eating_establishments_', 'num_parks']]
df_condo.rename(columns = {'num_eating_establishments_':'num_eating_establishments'},inplace=True)
df_condo.rename(columns = {'street':'condo_street', 'marketSegment':'condo_market_segment', 'commonest_tenure': 'condo_commonest_tenure'},inplace=True)

df_condo['apartment_type'] = 'condominium'

df_hdb = df_hdb[['block', 'floor_area_sqm', 'resale_price', 'price_per_sqm', 'lat', 'long',
                'num_malls', 'num_taxi_stands', 'num_primary_schools', 'num_mrt',
                'num_hawker', 'num_carparks', 'num_bus_stops', 'num_chas_clinics',
                'num_sports_facilities', 'num_community_centers', 'num_supermarkets',
                'num_secondary_schools', 'num_eating_establishments', 'num_parks']]
df_hdb['apartment_type'] = 'hdb'

df_condo.rename(columns={'avg_price_per_sqm':'price_per_sqm'},inplace=True)
df_hdb.rename(columns={'block': 'project', 'floor_area_sqm':'hdb_avg_floor_area_sqm', 'resale_price':'hdb_avg_resale_price'},inplace=True)

# Add postal code to HDB blocks
def get_postal_code(address):
    matches = requests.get(
        "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            address)).json()['results']
    try:
        first_match = matches[0]
        return first_match['POSTAL']
    except IndexError:
        return np.nan

print("Add postal code to HDB blocks",time.time())

df_hdb['hdb_postal_code'] = df_hdb.apply(lambda x: get_postal_code(x['project']),axis=1)

df_hdb = df_hdb[df_hdb['hdb_postal_code']!='NIL']
df_hdb.dropna(subset=['hdb_postal_code'],inplace=True)

print("Finished adding postal code to HDB blocks",time.time())

# Generate district information from HDB postal codes
postal_code_mapping = pd.read_csv("../data/raw/postal_codes_mapping.csv", header=0, names=['district', 'postal_sectors', 'locations'])
mapping = {}
for i in range(postal_code_mapping.shape[0]):
    postal_sectors = postal_code_mapping.loc[i,'postal_sectors']
    district = postal_code_mapping.loc[i,'district']
    sectors = str(postal_sectors).split(",")
    sectors = [sector.lstrip().rstrip() for sector in sectors]
    for sector in sectors:
        mapping[sector] = district

def convert_postal_code_to_district(postal_code, mapping=mapping):
    first_two_digits = postal_code[:2]
    return mapping[first_two_digits]

df_hdb['district'] = df_hdb.apply(lambda x: str(convert_postal_code_to_district(x['hdb_postal_code'])),axis=1)

# Create combined dataframe of condominium and HDB data

print([col for col in df_condo.columns if col not in df_hdb.columns])
print([col for col in df_hdb.columns if col not in df_condo.columns])

df_combined = pd.concat([df_condo, df_hdb], axis=0, join='outer', ignore_index=True).reset_index()
df_combined.rename(columns = {'index': 'project_id'}, inplace=True)

###### Create combined dataframe of features (places of interest), including places with quality scores (such as clinics, community centers, primary schools) and places without quality scores (such as bus stops, taxi stands, etc.) ####

print("Start working on features w quality scores",time.time())

clinics = pd.read_csv("../data/with_quality_scores/clinics.csv")[['modified_name','google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating', 'lat', 'long', 'address']].rename(columns={'modified_name':'name'})
community_centers = pd.read_csv("../data/with_quality_scores/community_centers.csv")[['address', 'lat', 'long', 'modified_name', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating']].rename(columns={'modified_name':'name'})
gyms = pd.read_csv("../data/with_quality_scores/gyms.csv")[['address', 'lat', 'long', 'modified_name', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating']].rename(columns={'modified_name':'name'})
hawker_centers = pd.read_csv("../data/with_quality_scores/hawker_centers.csv")[['Name','lat','long','W','weighted_rating','avg_rating','num_ratings']].rename(columns = {'Name':'name'})
malls = pd.read_csv("../data/with_quality_scores/malls.csv")[['Name','lat','long','W','weighted_rating','avg_rating','num_ratings']].rename(columns = {'Name':'name'})
other_public_sports_facilities = pd.read_csv("../data/with_quality_scores/other_public_sports_facilities.csv")[['address', 'lat', 'long', 'modified_name', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating']].rename(columns={'modified_name':'name'})
parks = pd.read_csv("../data/with_quality_scores/parks.csv")[['lat','long','park_name','google_place_id', 'num_ratings', 'avg_rating', 'W','weighted_rating']].rename(columns = {'park_name':'name'})
primary_schools = pd.read_csv("../data/with_quality_scores/primary_schools.csv")[['Name','long', 'lat', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating']].rename(columns = {'Name':'name'})
secondary_schools = pd.read_csv("../data/with_quality_scores/secondary_schools.csv")[['school_name','lat','long','address','google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating']].rename(columns={'school_name':'name'})
supermarkets = pd.read_csv("../data/with_quality_scores/supermarkets.csv")[['lat', 'long', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating', 'modified_name']].rename(columns={'modified_name':'name'})

features_with_quality_scores =  [clinics,community_centers,gyms,hawker_centers,malls,other_public_sports_facilities,parks,primary_schools,secondary_schools,supermarkets]
feature_names_with_quality_scores = ["clinic","community_center","gym","hawker_center","mall","other_public_sports_facility","park","primary_school","secondary_school","supermarket"]

for i in range(len(features_with_quality_scores)):
    feature = features_with_quality_scores[i]
    feature['feature_type'] = feature_names_with_quality_scores[i]

print("finish working on features w quality scores",time.time())

# Add in addresses (may take very long time -- can comment out if it takes too long)

def get_address(search_string):
    matches = requests.get(
        "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            search_string)).json()['results']
    try:
        first_match = matches[0]
        return first_match['ADDRESS']
    except IndexError:
        return np.nan

print("Add in addresses to features with quality scores",time.time())

for feat in features_with_quality_scores:
    if 'address' not in feat.columns:
        print(feat.loc[0,'feature_type'])
        feat['address'] = feat.apply(lambda x: get_address(x['name']),axis=1)

print("Finished adding in addresses to features with quality scores",time.time())

# Add features without quality data

print("Add features w/o quality data",time.time())

bus_stops = pd.read_csv("../data/raw/bus_stops.csv")[['RoadName','Description','Latitude','Longitude']]
bus_stops['name'] = bus_stops['Description'] + ' ,' + bus_stops['RoadName']
bus_stops.rename(columns={'Latitude':'lat','Longitude':'long'},inplace=True)
bus_stops.drop(columns=['Description','RoadName'],inplace=True)
carparks = pd.read_csv("../data/raw/carparks.csv")[['Location','latitude', 'longitude']].rename(columns = {'Location':'name','latitude':'lat','longitude':'long'})
mrt = pd.read_csv("../data/raw/data_MRT.csv")[['Name','Coordinates']].rename(columns={'Name':'name'})
mrt[['long','lat']] = mrt['Coordinates'].str.split(',',1,expand=True)
mrt.drop(columns=['Coordinates'],inplace=True)
eating_establishments = pd.read_csv("../data/raw/eating_establishments.csv")[['Description','lat','long']].rename(columns = {'Description':'name'})

def get_business_name(html_text):
    matches = re.findall(r'<th>BUSINESS_NAME<\/th>[ 0-9a-zA-Z\/<>]*<\/td>',html_text)
    if len(matches)>0:
        return matches[0].lstrip("<th>BUSINESS_NAME</th>").rstrip("</td>").lstrip().rstrip().lstrip("<td>")
    else:
        return np.nan

eating_establishments['name'] = eating_establishments.apply(lambda x: get_business_name(x['name']),axis = 1)
eating_establishments.dropna(subset=['name','lat','long'],how='any',inplace=True) # 34378 --> 28359

taxi_stands = pd.read_csv("../data/raw/taxi_stands.csv")[["Latitude","Longitude","Name"]].rename(columns = {'Name':'name','Latitude':'lat','Longitude':'long'})

features_without_quality_scores = [bus_stops, carparks, mrt, eating_establishments, taxi_stands]
feature_names_without_quality_scores = ['bus_stop','carpark','mrt','eating_establishment','taxi_stand']

for i in range(len(features_without_quality_scores)):
    feature = features_without_quality_scores[i]
    feature['feature_type'] = feature_names_without_quality_scores[i]

features = pd.concat(features_with_quality_scores + features_without_quality_scores, ignore_index = True).reset_index()
features.rename(columns = {'index':'feature_id'},inplace=True)

features.to_csv("../data/processed/features.csv")

print("finished adding featuress w/o quality data",time.time())

print("Finished creating combined dataframe of properties and features",time.time())

###### END OF Create combined dataframe of features (places of interest), including places with quality scores (such as clinics, community centers, primary schools) and places without quality scores (such as bus stops, taxi stands, etc.) ####

################### Add quality data, as well as track which objects are within the radius ####################

print("Start to do pairwise comparison",time.time())

start = time.time()

radius = 1.0 # only consider objects within 1km radius

features = pd.read_csv("../data/processed/features.csv")[['feature_id', 'name', 'google_place_id', 'num_ratings',
       'avg_rating', 'W', 'weighted_rating', 'lat', 'long', 'address',
       'feature_type']]

added_numeric_columns = []

for feature_type in list(features.feature_type.unique()):
    loop_start = time.time()
    print("Considering feature type {}".format(feature_type))
    places = features[features['feature_type'] == feature_type].reset_index()
    for i in range(df_combined.shape[0]):

        colname_num_features = "recomputed_" + "num_" + feature_type
        colname_feature_ids = "feature_ids_" + feature_type
        colname_feature_scores = "median_weighted_score_" + feature_type
        added_numeric_columns.extend([colname_num_features,colname_feature_scores])
        feature_ids = []
        scores = []
        counter = 0

        try:
            lat1 = float(df_combined.loc[i,"lat"])
            long1 = float(df_combined.loc[i,"long"])
            origin = (lat1,long1)
        except ValueError:
            continue

        for j in range(places.shape[0]):
            try:
                lat2 = float(places.loc[j, "lat"])
                long2 = float(places.loc[j, "long"])
                dest = (lat2, long2)
                dist = geodesic(origin, dest).km
                if dist <= radius:
                    counter += 1
                    feature_ids.append(places.loc[j,"feature_id"])
                    scores.append(places.loc[j,"weighted_rating"])
            except ValueError:
                continue

        df_combined.loc[i, colname_num_features] = counter
        df_combined.loc[i, colname_feature_ids] = str(feature_ids)
        df_combined.loc[i, colname_feature_scores] = np.median(scores)
    loop_end=time.time()
    print("Completed feature type {}, took {} seconds".format(feature_type,loop_end-loop_start))
    df_combined.to_csv("../data/processed/df_with_features.csv")
    print("Checkpointing df_with_features.csv after completion of pairwise comparison for feature {}".format(str(feature_type)))

scaler = MinMaxScaler()

added_numeric_columns_only = df_combined.loc[:,[col for col in added_numeric_columns if col in df_combined.columns]]
other_columns_only= df_combined.loc[:,[col for col in df_combined.columns if col not in added_numeric_columns]]

scaled_numeric = pd.DataFrame(scaler.fit_transform(added_numeric_columns_only))

df_scaled = pd.concat([other_columns_only,scaled_numeric],axis=1)

df_scaled.to_csv("../data/processed/df_with_features_scaled.csv")

end = time.time()

print("Pairwise comparison took {} seconds".format(end-start))

print("End of script",time.time())