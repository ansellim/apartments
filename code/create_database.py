'''

Ansel Lim, 27 November 2021.

Create database from csv files.

Inputs:

1. features.csv: a dataframe of 32,695 amenities (features).
2. df_with_features.csv: a dataframe of 10,614 properties. Each property has quality and quantity scores for various amenities (features) within a 1 kilometer radius.
3. df_with_features_binned.csv: the same data as df_with_features.csv, but with the quality and quantity scores binned into quartiles (encoding of quartile information: first quartile/Q1 --> 0.25, second quartile --> 0.50, third quartile --> 0.75, fourth quartile --> 1.00)

'''

import pandas as pd
import sqlite3
import os

os.chdir("../data/")

features = pd.read_csv("./processed/features.csv")
df_with_features = pd.read_csv("./processed/df_with_features.csv", low_memory=False)
df_with_features_binned = pd.read_csv("./processed/df_with_features_binned.csv")

if 'Unnamed: 0' in df_with_features.columns:
    df_with_features.drop(columns = ['Unnamed: 0'],inplace=True)

if 'Unnamed: 0' in df_with_features_binned.columns:
    df_with_features_binned.drop(columns = ['Unnamed: 0'],inplace=True)

df_with_features.drop(columns = ['deprecated_num_malls',
       'deprecated_num_taxi_stands', 'deprecated_num_primary_schools',
       'deprecated_num_mrt', 'deprecated_num_hawker',
       'deprecated_num_carparks', 'deprecated_num_bus_stops',
       'deprecated_num_chas_clinics', 'deprecated_num_sports_facilities',
       'deprecated_num_community_centers', 'deprecated_num_supermarkets',
       'deprecated_num_secondary_schools',
       'deprecated_num_eating_establishments', 'deprecated_num_parks',
       'apartment_type'], inplace=True)

feature_scores_colnames = ['num_clinic','quality_clinic','num_community_center','quality_community_center','num_gym','quality_gym','num_hawker_center','quality_hawker_center', 'num_mall','quality_mall',
         'num_other_public_sports_facility','quality_other_public_sports_facility','num_park','quality_park','num_primary_school','quality_primary_school','num_secondary_school', 'quality_secondary_school', 'num_supermarket','quality_supermarket','num_bus_stop','num_carpark', 'num_mrt', 'num_eating_establishment','num_taxi_stand',]
feature_ids_colnames = ['feature_ids_clinic','feature_ids_community_center','feature_ids_gym','feature_ids_hawker_center','feature_ids_mall','feature_ids_other_public_sports_facility','feature_ids_park',
'feature_ids_primary_school','feature_ids_secondary_school','feature_ids_supermarket','feature_ids_bus_stop','feature_ids_carpark','feature_ids_mrt','feature_ids_eating_establishment', 'feature_ids_taxi_stand'
       ]

df_with_features.drop(columns = feature_ids_colnames,inplace=True)

mapping = {column_name : 'raw_'+column_name for column_name in feature_scores_colnames}

df_with_features.rename(columns=mapping, inplace=True)

df_with_features_binned.drop(columns=['apartment_type'], inplace=True)

columns = list(df_with_features.columns.difference(df_with_features_binned.columns))
columns.append('project_id')

properties = df_with_features_binned.merge(right=df_with_features[columns], on='project_id', how='inner')

if 'Unnamed: 0.1' in properties.columns:
    properties.drop(columns=['Unnamed: 0.1'], inplace=True)

if 'Unnamed: 0' in features.columns:
    features.drop(columns=['Unnamed: 0'], inplace=True)

conn = sqlite3.connect('database.db')
conn.execute("DROP TABLE IF EXISTS properties;")
conn.execute("DROP TABLE IF EXISTS features;")
properties.to_sql('properties', conn)
features.to_sql('features', conn)

conn.close()
