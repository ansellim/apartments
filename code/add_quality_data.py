# Ansel Lim, ansel@gatech.edu
# 24/25 - 28 Nov 2021

'''
add_quality_data.py

This code was run after scoring_condo and scoring_hdb calculated, for each property project, the number of places of interest (in various categories of place of interest) within a one-kilometer radius.
The objective of this code is to:
    0. filter out missing/corrupted data, harmonize the dataset to make it more streamlined and consistent
    1. add quality score (weighted rating on Google Places API)
    2. recompute quantity scores
    3. for each property, store the ID's of nearby places of interest, so that some of these places of interest may be displayed downstream.
    4. process the property and feature information into two well-organized relations so that the resulting dataframes may be fed into a relational database (SQLite).
'''

###########################################################################################
###############################Part 0: Dependencies########################################
###########################################################################################

# A flag to indicate whether we are only doing prototyping of the code. If prototyping, we only load small amounts of the data into the code to test out the code.
prototype = False

import copy
import os
import re
import time
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from geopy.distance import geodesic
from sklearn.preprocessing import MinMaxScaler


# A utility function to print the UTC time.
def print_time():
    return datetime.utcnow().isoformat(timespec='seconds')


print("Start of the script", print_time())

warnings.filterwarnings("ignore")

# If prototyping, then set the prototype flag to True at the top of the script.
# Prototyping helps to avoid unnecessary API calls that will incur additional costs.
if prototype:
    print("Prototype flag is set to TRUE")
    MAX_ROWS = 200
    print("Max rows value is {}".format(MAX_ROWS))
else:
    print("Prototype flag is set to FALSE")
    MAX_ROWS = None

###########################################################################################
###########################################################################################
#######################Part 1: Get ratings from Google Maps API############################
###################for features we want to compute quality scores on#######################
###########################################################################################
###########################################################################################

'''
Note that a 'feature' is a place of interest (you could also call it a neighborhood amenity), for example, a shopping mall, park, or primary school.

We only compute quality scores for the following amenity types:
1. Primary schools
2. Secondary schools
3. Parks
4. Supermarkets
5. Malls
6. CHAS Clinics
7. Gyms
8. Community Centers.
9. Other Public Sports Facilities (most are swimming pools)
10. Hawker centers.

The raw Google Places ratings for hawker centers & malls were scraped manually by Daosheng. We'll get the other feature types' ratings from Google Places API using our script.

'''

print(
    "Part 1: Started working on getting ratings from Google Maps API for features we want to compute quality scores on",
    print_time())

# Load API Key
load_dotenv()
GOOGLE_API_KEY = str(os.environ.get("GOOGLE_API_KEY"))
print("API key loaded")


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
    try:
        top_match = matches.json()['candidates']
        if len(top_match) < 1:
            return np.nan, np.nan, np.nan
        else:
            top_match = top_match[0]
            place_id = top_match.get('place_id')
            num_ratings = top_match.get('user_ratings_total')
            avg_rating = top_match.get('rating')
            return place_id, num_ratings, avg_rating
    except:
        return np.nan, np.nan, np.nan


# Primary schools
print("Getting ratings data from Google Places API for Primary Schools", print_time())
primary_schools = pd.read_csv("../data/raw/data_prischools.csv", nrows=MAX_ROWS)

primary_schools = primary_schools.dropna(subset=['Name', 'coordinates'], how='any')
primary_schools[['long', 'lat']] = primary_schools['coordinates'].str.split(',', 1, expand=True)
primary_schools[['google_place_id', 'num_ratings', 'avg_rating']] = primary_schools.apply(
    lambda x: get_information(x['Name']), axis=1, result_type='expand')

primary_schools = primary_schools.dropna(subset=['google_place_id', 'num_ratings', 'avg_rating'], how='any')

primary_schools['W'] = primary_schools['num_ratings'] / (primary_schools['num_ratings'].max())
r0 = primary_schools['avg_rating'].mean()
primary_schools['weighted_rating'] = primary_schools['W'] * primary_schools['avg_rating'] + (
        1 - primary_schools['W']) * r0

primary_schools.to_csv("../data/with_quality_scores/data_prischools.csv")

# Secondary schools
print("Getting ratings data from Google Places API for Secondary Schools", print_time())
secondary_schools = pd.read_csv("../data/raw/secondary_schools.csv", nrows=MAX_ROWS)
secondary_schools = secondary_schools.dropna(subset=['lat', 'long', 'school_name'], how='any')
secondary_schools[['google_place_id', 'num_ratings', 'avg_rating']] = secondary_schools.apply(
    lambda x: get_information(x['school_name']), axis=1, result_type='expand')

secondary_schools = secondary_schools.dropna(subset=['google_place_id', 'num_ratings', 'avg_rating'], how='any')

secondary_schools['W'] = secondary_schools['num_ratings'] / (secondary_schools['num_ratings'].max())
r0 = secondary_schools['avg_rating'].mean()
secondary_schools['weighted_rating'] = secondary_schools['W'] * secondary_schools['avg_rating'] + (
        1 - secondary_schools['W']) * r0
secondary_schools.to_csv("../data/with_quality_scores/secondary_schools.csv")

# Parks
print("Getting ratings data from Google Places API for Parks", print_time())
parks = pd.read_csv("../data/raw/parks.csv", nrows=MAX_ROWS)
parks = parks.dropna(subset=['lat', 'long', 'park_name'], how='any')

parks.rename(columns={'park_name': 'name'}, inplace=True)

parks[['google_place_id', 'num_ratings', 'avg_rating']] = parks.apply(lambda x: get_information(x['name']), axis=1,
                                                                      result_type='expand')

parks = parks.dropna(subset=['google_place_id', 'num_ratings', 'avg_rating'], how='any')

parks['W'] = parks['num_ratings'] / (parks['num_ratings'].max())
r0 = parks['avg_rating'].mean()
parks['weighted_rating'] = parks['W'] * parks['avg_rating'] + (1 - parks['W']) * r0

parks.to_csv("../data/with_quality_scores/parks.csv")

# Supermarkets
print("Getting ratings data from Google Places API for Supermarkets", print_time())
supermarkets = pd.read_csv("../data/raw/supermarkets.csv", nrows=MAX_ROWS)
supermarkets = supermarkets.dropna(subset=['lat', 'long', 'business_name', 'premise_address'], how='any')


def remove_postal_code(address):
    try:
        postal_code = re.findall(pattern=r'[S][(][0-9]{6}[)]', string=address)[:1]
        if len(postal_code) > 0:
            postal_code = postal_code[0]
            return address.rstrip(postal_code).rstrip(", ")
        else:
            return address
    except:
        return np.nan


supermarkets['location'] = supermarkets.apply(lambda x: remove_postal_code(str(x['premise_address'])), axis=1)
supermarkets.dropna(subset=['location'], inplace=True)

supermarkets['name'] = supermarkets['business_name'] + ' ' + supermarkets['location']
supermarkets.dropna(subset=['name'], inplace=True)
supermarkets.drop(columns=['business_name', 'location'], inplace=True)

supermarkets[['google_place_id', 'num_ratings', 'avg_rating']] = supermarkets.apply(
    lambda x: get_information(x['name']), axis=1, result_type='expand')

supermarkets = supermarkets.dropna(subset=['google_place_id', 'num_ratings', 'avg_rating'], how='any')

supermarkets['W'] = supermarkets['num_ratings'] / (supermarkets['num_ratings'].max())
r0 = supermarkets['avg_rating'].mean()
supermarkets['weighted_rating'] = supermarkets['W'] * supermarkets['avg_rating'] + (1 - supermarkets['W']) * r0
supermarkets.to_csv("../data/with_quality_scores/supermarkets.csv")

# Malls
# Daosheng already did scraping of ratings and number of ratings for malls, so we'll just calculate the scores rather than obtain them from Google Places API.

print("Calculating scores for malls", print_time())
malls = pd.read_csv("../data/raw/data_malls.csv", nrows=MAX_ROWS)
malls = malls.dropna(subset=['Name', 'long', 'lat', 'rating', 'user_ratings_total'])
malls.rename(columns={'rating': 'avg_rating', 'user_ratings_total': 'num_ratings'}, inplace=True)

malls['W'] = malls['num_ratings'] / (malls['num_ratings'].max())
r0 = malls['avg_rating'].mean()
malls['weighted_rating'] = malls['W'] * malls['avg_rating'] + (1 - malls['W']) * r0

malls.to_csv("../data/with_quality_scores/malls.csv")

# Other amenities - CHAS Clinics, Gyms, Community Centers.
'''
Since we have 1167 CHAS Clinics, 160 gyms, 120 community centers, and fewer numbers of other facility types, we'll focus on CHAS Clinics, gyms, and community centers.
The remaining 34 are mostly swimming complexes +/- sports halls / tennis courts / et cetera.
'''

print(
    "Getting ratings data from Google Places API for Amenities (CHAS clinics, gyms, community centers, other sports facilities)",
    print_time())

amenities = pd.read_csv("../data/raw/amenities.csv", nrows=MAX_ROWS)
amenities.dropna(subset=['facility_name', 'lat', 'long'], how='any', inplace=True)
for i in range(amenities.shape[0]):
    amenities.loc[i, 'modified_name'] = amenities.loc[i, 'facility_name'] + ' ' + str(amenities.loc[i, 'address'])[:-7]

amenities[['google_place_id', 'num_ratings', 'avg_rating']] = amenities.apply(
    lambda x: get_information(x['modified_name']), axis=1, result_type='expand')
amenities = amenities.dropna(subset=['google_place_id', 'num_ratings', 'avg_rating'], how='any')

clinics = amenities[amenities['facility_type'] == 'CHAS Clinic']
gyms = amenities[amenities['facility_type'] == 'Gym']
community_centers = amenities[amenities['facility_type'] == 'Community Centre']
other_public_sports_facilities = amenities[~amenities['facility_type'].isin(['CHAS Clinic', 'Gym', 'Community Centre'])]

clinics['W'] = clinics['num_ratings'] / (clinics['num_ratings'].max())
r0 = clinics['avg_rating'].mean()
clinics['weighted_rating'] = clinics['W'] * clinics['avg_rating'] + (1 - clinics['W']) * r0
clinics.to_csv("../data/with_quality_scores/clinics.csv")

gyms['W'] = gyms['num_ratings'] / (gyms['num_ratings'].max())
r0 = gyms['avg_rating'].mean()
gyms['weighted_rating'] = gyms['W'] * gyms['avg_rating'] + (1 - gyms['W']) * r0
gyms.to_csv("../data/with_quality_scores/gyms.csv")

community_centers['W'] = community_centers['num_ratings'] / (community_centers['num_ratings'].max())
r0 = community_centers['avg_rating'].mean()
community_centers['weighted_rating'] = community_centers['W'] * community_centers['avg_rating'] + (
        1 - community_centers['W']) * r0
community_centers.to_csv("../data/with_quality_scores/community_centers.csv")

other_public_sports_facilities['W'] = other_public_sports_facilities['num_ratings'] / (
    other_public_sports_facilities['num_ratings'].max())
r0 = other_public_sports_facilities['avg_rating'].mean()
other_public_sports_facilities['weighted_rating'] = other_public_sports_facilities['W'] * \
                                                    other_public_sports_facilities['avg_rating'] + (
                                                            1 - other_public_sports_facilities['W']) * r0
other_public_sports_facilities.to_csv("../data/with_quality_scores/other_public_sports_facilities.csv")

# Hawker centers
# Daosheng already did manual scraping of ratings and number of ratings for hawker centers, so we'll just calculate the scores rather than obtain them from Google Places API.

print("Calculating scores for hawker centers", print_time())
hawker_centers = pd.read_csv("../data/raw/data_hawker.csv", nrows=MAX_ROWS)
hawker_centers.dropna(subset=['Coordinates', 'Name', 'rating', 'user_ratings_total'], how='any', inplace=True)
hawker_centers[['long', 'lat']] = hawker_centers['Coordinates'].str.split(',', 1, expand=True)
hawker_centers.rename(columns={'rating': 'avg_rating', 'user_ratings_total': 'num_ratings'}, inplace=True)
hawker_centers[['lat', 'temp']] = hawker_centers['lat'].str.split(',', 1, expand=True)
hawker_centers.drop(columns=['temp'], inplace=True)
hawker_centers['W'] = hawker_centers['num_ratings'] / (hawker_centers['num_ratings'].max())
r0 = hawker_centers['avg_rating'].mean()
hawker_centers['weighted_rating'] = hawker_centers['W'] * hawker_centers['avg_rating'] + (1 - hawker_centers['W']) * r0

hawker_centers.to_csv("../data/with_quality_scores/hawker_centers.csv")

print("Finished working on getting ratings from Google Maps API for features we want to compute quality scores on",
      print_time())

###########################################################################################
###########################################################################################
#######################Part 2: Combine condo and HDB dataframes############################
###########################################################################################
###########################################################################################

print("Part 2: Started combining condo and hdb dataframes", print_time())

df_condo = pd.read_csv('../data/processed/df.csv', nrows=MAX_ROWS)
df_hdb = pd.read_csv('../data/processed/df_hdb.csv', nrows=MAX_ROWS)

df_condo.drop(columns=['num_eating_establishments'], inplace=True)
df_condo = df_condo[['street', 'project', 'marketSegment', 'lat', 'long', 'avg_price_per_sqm', 'district',
                     'commonest_tenure', 'num_malls', 'num_taxi_stands', 'num_primary_schools',
                     'num_mrt', 'num_hawker', 'num_carparks', 'num_bus_stops', 'num_chas_clinics',
                     'num_sports_facilities', 'num_community_centers', 'num_supermarkets', 'num_secondary_schools',
                     'num_eating_establishments_', 'num_parks']]
df_condo.rename(columns={'num_eating_establishments_': 'num_eating_establishments'}, inplace=True)
df_condo.rename(columns={'street': 'condo_street', 'marketSegment': 'condo_market_segment',
                         'commonest_tenure': 'condo_commonest_tenure'}, inplace=True)

df_condo['apartment_type'] = 'condominium'

df_hdb = df_hdb[['block', 'floor_area_sqm', 'resale_price', 'price_per_sqm', 'lat', 'long',
                 'num_malls', 'num_taxi_stands', 'num_primary_schools', 'num_mrt',
                 'num_hawker', 'num_carparks', 'num_bus_stops', 'num_chas_clinics',
                 'num_sports_facilities', 'num_community_centers', 'num_supermarkets',
                 'num_secondary_schools', 'num_eating_establishments', 'num_parks']]
df_hdb['apartment_type'] = 'hdb'

df_condo.rename(columns={'avg_price_per_sqm': 'price_per_sqm'}, inplace=True)
df_hdb.rename(
    columns={'block': 'project', 'floor_area_sqm': 'hdb_avg_floor_area_sqm', 'resale_price': 'hdb_avg_resale_price'},
    inplace=True)


# Add postal code to HDB blocks
def get_postal_code(address):
    try:
        matches = requests.get(
            "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
                address)).json()['results']
    except:
        return np.nan
    try:
        first_match = matches[0]
        return first_match['POSTAL']
    except IndexError:
        return np.nan


print("Add postal code to HDB blocks", print_time())

df_hdb['hdb_postal_code'] = df_hdb.apply(lambda x: get_postal_code(x['project']), axis=1)

df_hdb = df_hdb[df_hdb['hdb_postal_code'] != 'NIL']
df_hdb.dropna(subset=['hdb_postal_code'], inplace=True)

print("Finished adding postal code to HDB blocks", print_time())

# Generate district information from HDB postal codes
print("Started adding district information to HDB blocks", print_time())
postal_code_mapping = pd.read_csv("../data/raw/postal_codes_mapping.csv", header=0,
                                  names=['district', 'postal_sectors', 'locations'])
mapping = {}
for i in range(postal_code_mapping.shape[0]):
    postal_sectors = postal_code_mapping.loc[i, 'postal_sectors']
    district = postal_code_mapping.loc[i, 'district']
    sectors = str(postal_sectors).split(",")
    sectors = [sector.lstrip().rstrip() for sector in sectors]
    for sector in sectors:
        mapping[sector] = district

print("Finished adding district information to HDB blocks", print_time())


def convert_postal_code_to_district(postal_code, mapping=mapping):
    try:
        first_two_digits = postal_code[:2]
        return mapping[first_two_digits]
    except:
        return np.nan


df_hdb['district'] = df_hdb.apply(lambda x: str(convert_postal_code_to_district(x['hdb_postal_code'])), axis=1)
df_hdb.dropna(subset=['district'], inplace=True)

# Create combined dataframe of condominium and HDB data

# print([col for col in df_condo.columns if col not in df_hdb.columns])
# print([col for col in df_hdb.columns if col not in df_condo.columns])

df_hdb['project_type'] = 'hdb'
df_condo['project_type'] = 'condo'

df_combined = pd.concat([df_condo, df_hdb], axis=0, join='outer', ignore_index=True).reset_index()
df_combined.rename(columns={'index': 'project_id'}, inplace=True)

print("Finished combining condo and hdb dataframes", print_time())

###########################################################################################
#######################Part 3: Process features with quality scores########################
###########################################################################################

print("Part 3: Start working on features with quality scores", print_time())

clinics = pd.read_csv("../data/with_quality_scores/clinics.csv")[
    ['modified_name', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating', 'lat', 'long',
     'address']].rename(columns={'modified_name': 'name'})
community_centers = pd.read_csv("../data/with_quality_scores/community_centers.csv")[
    ['address', 'lat', 'long', 'modified_name', 'google_place_id', 'num_ratings', 'avg_rating', 'W',
     'weighted_rating']].rename(columns={'modified_name': 'name'})
gyms = pd.read_csv("../data/with_quality_scores/gyms.csv")[
    ['address', 'lat', 'long', 'modified_name', 'google_place_id', 'num_ratings', 'avg_rating', 'W',
     'weighted_rating']].rename(columns={'modified_name': 'name'})
hawker_centers = pd.read_csv("../data/with_quality_scores/hawker_centers.csv")[
    ['Name', 'lat', 'long', 'W', 'weighted_rating', 'avg_rating', 'num_ratings']].rename(columns={'Name': 'name'})
malls = pd.read_csv("../data/with_quality_scores/malls.csv")[
    ['Name', 'lat', 'long', 'W', 'weighted_rating', 'avg_rating', 'num_ratings']].rename(columns={'Name': 'name'})
other_public_sports_facilities = pd.read_csv("../data/with_quality_scores/other_public_sports_facilities.csv")[
    ['address', 'lat', 'long', 'modified_name', 'google_place_id', 'num_ratings', 'avg_rating', 'W',
     'weighted_rating']].rename(columns={'modified_name': 'name'})
parks = pd.read_csv("../data/with_quality_scores/parks.csv")[
    ['name', 'lat', 'long', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating']]
primary_schools = pd.read_csv("../data/with_quality_scores/primary_schools.csv")[
    ['Name', 'long', 'lat', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating']].rename(
    columns={'Name': 'name'})
secondary_schools = pd.read_csv("../data/with_quality_scores/secondary_schools.csv")[
    ['school_name', 'lat', 'long', 'address', 'google_place_id', 'num_ratings', 'avg_rating', 'W',
     'weighted_rating']].rename(columns={'school_name': 'name'})
supermarkets = pd.read_csv("../data/with_quality_scores/supermarkets.csv")[
    ['name', 'lat', 'long', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating']]

features_with_quality_scores = [clinics, community_centers, gyms, hawker_centers, malls, other_public_sports_facilities,
                                parks, primary_schools, secondary_schools, supermarkets]
feature_names_with_quality_scores = ["clinic", "community_center", "gym", "hawker_center", "mall",
                                     "other_public_sports_facility", "park", "primary_school", "secondary_school",
                                     "supermarket"]


# Add in addresses for features with quality scores

def get_address(search_string):
    try:
        matches = requests.get(
            "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
                search_string)).json()['results']
    except:
        return np.nan
    try:
        first_match = matches[0]
        return first_match['ADDRESS']
    except IndexError:
        return np.nan


print("Add in addresses to features with quality scores", print_time())

for i in range(len(features_with_quality_scores)):
    feat = features_with_quality_scores[i]
    print(feature_names_with_quality_scores[i])
    if 'address' not in feat.columns:
        feat['address'] = feat.apply(lambda x: get_address(x['name']), axis=1)

for i in range(len(features_with_quality_scores)):
    feature = features_with_quality_scores[i]
    feature['feature_type'] = feature_names_with_quality_scores[i]

print("Finished adding in addresses to features with quality scores", print_time())

print("Finished working on features with quality scores", print_time())

##############################################################################################
#######################Part 4: Process features without quality scores########################
##############################################################################################

print("Part 4: Started working on features without quality scores", print_time())

bus_stops = pd.read_csv("../data/raw/bus_stops.csv", nrows=MAX_ROWS)[
    ['RoadName', 'Description', 'Latitude', 'Longitude']]
bus_stops['name'] = bus_stops['Description'] + ' ,' + bus_stops['RoadName']
bus_stops.rename(columns={'Latitude': 'lat', 'Longitude': 'long'}, inplace=True)
bus_stops.drop(columns=['Description', 'RoadName'], inplace=True)
carparks = pd.read_csv("../data/raw/carparks.csv", nrows=MAX_ROWS)[['Location', 'latitude', 'longitude']].rename(
    columns={'Location': 'name', 'latitude': 'lat', 'longitude': 'long'})
mrt = pd.read_csv("../data/raw/data_MRT.csv", nrows=MAX_ROWS)[['Name', 'Coordinates']].rename(columns={'Name': 'name'})
mrt[['long', 'lat']] = mrt['Coordinates'].str.split(',', 1, expand=True)
mrt.drop(columns=['Coordinates'], inplace=True)
eating_establishments = pd.read_csv("../data/raw/eating_establishments.csv", nrows=MAX_ROWS)[
    ['Description', 'lat', 'long']].rename(columns={'Description': 'name'})


def get_business_name(html_text):
    matches = re.findall(r'<th>BUSINESS_NAME<\/th>[ 0-9a-zA-Z\/<>]*<\/td>', html_text)
    if len(matches) > 0:
        return matches[0].lstrip("<th>BUSINESS_NAME</th>").rstrip("</td>").lstrip().rstrip().lstrip("<td>")
    else:
        return np.nan


eating_establishments['name'] = eating_establishments.apply(lambda x: get_business_name(x['name']), axis=1)
eating_establishments.dropna(subset=['name', 'lat', 'long'], how='any', inplace=True)  # 34378 --> 28359

taxi_stands = pd.read_csv("../data/raw/taxi_stands.csv", nrows=MAX_ROWS)[["Latitude", "Longitude", "Name"]].rename(
    columns={'Name': 'name', 'Latitude': 'lat', 'Longitude': 'long'})

features_without_quality_scores = [bus_stops, carparks, mrt, eating_establishments, taxi_stands]
feature_names_without_quality_scores = ['bus_stop', 'carpark', 'mrt', 'eating_establishment', 'taxi_stand']

for i in range(len(features_without_quality_scores)):
    feature = features_without_quality_scores[i]
    feature['feature_type'] = feature_names_without_quality_scores[i]

print("Finished working on features without quality scores", print_time())

##############################################################################################
#######################Part 5: Create a combined "feature" dataframe #########################
#################### incorporating features with and without quality scores ##################
##############################################################################################
'''
Create combined dataframe of features (places of interest), including places with quality scores (such as clinics, community centers, primary schools), as well as places without quality scores (such as bus stops, taxi stands, etc.)
'''

print("Part 5: Create a combined feature dataframe incorporating features with and without quality scores ",
      print_time())

features = pd.concat(features_with_quality_scores + features_without_quality_scores, ignore_index=True).reset_index()
features.rename(columns={'index': 'feature_id'}, inplace=True)
features.to_csv("../data/processed/features.csv")

##############################################################################################
##############################################################################################
############Part 6: Create a combined dataframe of properties and features ###################
##############################################################################################
##############################################################################################

print("Part 6: Create a combined dataframe of properties and features (pairwise computation)", print_time())

'''
For each property, add quantitative and quality scores, as well as track which places of interest (features) are within a 1km radius of each property.

The purpose of this part of the code is to produce df_with_features_scaled, which contains (for each property) a quantitative +/- a quality score for each type of nearby place of interest.

DESCRIPTION OF THE OUTCOME OF THE CODE IN THIS PART (df_with_features_scaled.csv)

- A dataframe of property projects (a 'project' is an HDB block or a condo project), with quantity and *median* quality scores for each feature type. Since a feature is a place of interest, such as 'Bukit Timah Hawker Center' or 'Clementi MRT', it follows that a feature type is a type of place of interest, for example a community center or CHAS clinic. For each property, we look at a one-kilometer radius calculated based on latitude and longitude. 

- For each property, therefore, we count the number of features (within each feature type) within a one-kilometer radius, as well as compute the median `quality` score of features (within each feature type), again within that one-kilometer radius. The 'quality' score of a feature is a rating (out of a maximum of 5 stars) extracted from the Google Places API, normalized/weighted by the number of reviews that feature received compared to other features of the same feature type.

- To be clear, given a property, for each feature type, the number of features within a 1-kilometer radius is the quantity score, and the median of the quality scores of features within that same 1-kilometer radius is the quality score. Since different features may have different ranges of scores (this is more of an issue for quantity score, since quality score is on a Likert scale), the quality and quantity scores are scaled according to min-max scaling.

'''

### Rename old column names in combined dataframe of properties  ###

old_metrics = ['num_malls', 'num_taxi_stands', 'num_primary_schools', 'num_mrt',
               'num_hawker', 'num_carparks', 'num_bus_stops', 'num_chas_clinics',
               'num_sports_facilities', 'num_community_centers', 'num_supermarkets',
               'num_secondary_schools', 'num_eating_establishments', 'num_parks']

old_to_new_metrics_mapping = {}

renamed_old_metrics = []

for metric in old_metrics:
    if metric in df_combined.columns:
        old_to_new_metrics_mapping[metric] = "deprecated_" + metric
        renamed_old_metrics.append("deprecated_" + metric)

df_combined.rename(columns=old_to_new_metrics_mapping, inplace=True)

### Pairwise comparison; adding quality & quantity scores to the properties dataframe. ###

print("Started pairwise comparison", print_time())
start_pairwise = time.time()

radius = 1.0  # only consider objects within 1km radius

features = pd.read_csv("../data/processed/features.csv")[
    ['feature_id', 'name', 'google_place_id', 'num_ratings', 'avg_rating', 'W', 'weighted_rating', 'lat', 'long',
     'address', 'feature_type']]

added_numeric_columns = []

print(features)

print(features.feature_type)

for feature_type in list(features.feature_type.unique()):
    loop_start = time.time()
    if type(feature_type) != str:
        continue
    print("Considering feature type {}".format(feature_type))
    places = features[features['feature_type'] == feature_type].reset_index()
    print("Number of features in feature type {}: {}".format(feature_type, places.shape[0]))
    colname_num_features = "num_" + feature_type
    colname_feature_ids = "feature_ids_" + feature_type
    if feature_type in feature_names_with_quality_scores:
        colname_feature_scores = "quality_" + feature_type
        added_numeric_columns.extend([colname_num_features, colname_feature_scores])
    else:
        added_numeric_columns.append(colname_num_features)
    for i in range(df_combined.shape[0]):
        counter = 0
        feature_ids = set()
        scores = []
        try:
            lat1 = float(df_combined.loc[i, "lat"])
            long1 = float(df_combined.loc[i, "long"])
            origin = (lat1, long1)
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
                    feature_ids.add(places.loc[j, "feature_id"])
                    if feature_type in feature_names_with_quality_scores:
                        scores.append(places.loc[j, "weighted_rating"])
            except ValueError:
                continue

        df_combined.loc[i, colname_num_features] = counter
        df_combined.loc[i, colname_feature_ids] = str(feature_ids)
        if feature_type in feature_names_with_quality_scores:
            df_combined.loc[i, colname_feature_scores] = np.median(scores)
    loop_end = time.time()
    print("Completed feature type {}, took {} seconds. Time now: {}".format(feature_type, loop_end - loop_start,
                                                                            print_time()))
    df_combined.to_csv("../data/processed/df_with_features.csv")
    print("Checkpointing df_with_features.csv after completion of pairwise comparison for feature {}".format(
        str(feature_type)))

end_pairwise = time.time()
print("Finished pairwise comparison. Pairwise comparison took {} seconds".format(end_pairwise - start_pairwise))
print("Finished pairwise comparison", print_time())

# Save file, just to be extra sure
df_combined.to_csv("../data/processed/df_with_features.csv")

### Perform min-max scaling for numeric columns of number of features & median quality score. ###

print(
    "Started performing min-max scaling for num_features (quantity score) and median weighted ratings (quality score)",
    print_time())

scaler = MinMaxScaler()
added_numeric_columns_only = df_combined.loc[:, added_numeric_columns]
other_columns_only = df_combined.loc[:, [col for col in df_combined.columns if col not in added_numeric_columns]]

scaled_numeric = pd.DataFrame(scaler.fit_transform(added_numeric_columns_only), columns=added_numeric_columns)

df_scaled = pd.concat([other_columns_only, scaled_numeric], axis=1)

df_scaled.to_csv("../data/processed/df_with_features_scaled_with_deprecated.csv")

df_scaled = df_scaled.drop(columns=[column for column in renamed_old_metrics if column in df_scaled.columns])

df_scaled.to_csv("../data/processed/df_with_features_scaled.csv")

# Bin the quality and quantity scores into quartiles (Q1 -> 0.25, Q2 -> 0.50, Q3 -> 0.75, Q4 -> 1.00)

df_with_features_binned = copy.deepcopy(df_combined)

for colname in added_numeric_columns:
    q25 = np.percentile(df_with_features_binned.loc[:, colname], 25)
    q50 = np.percentile(df_with_features_binned.loc[:, colname], 50)
    q75 = np.percentile(df_with_features_binned.loc[:, colname], 25)
    for i in range(df_with_features_binned.shape[0]):
        val = df_with_features_binned.loc[i, colname]
        if val == np.nan:
            pass
        elif val == 0:
            df_with_features_binned.loc[i, colname] = 0
        elif val <= q25:
            df_with_features_binned.loc[i, colname] = 0.25
        elif val <= q50:
            df_with_features_binned.loc[i, colname] = 0.50
        elif val <= q75:
            df_with_features_binned.loc[i, colname] = 0.75
        else:
            df_with_features_binned.loc[i, colname] = 1.00

df_with_features_binned.to_csv("../data/processed/df_with_features_binned.csv")

print("End of Part 6 and end of script", print_time())
