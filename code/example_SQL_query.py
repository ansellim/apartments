# Ansel Lim
# 28 November 2021

# Minimal reproducible code (incorporated into views.py) for querying the database and returning an object that is rendered by the mapping application.

import sqlite3 as sql
import numpy as np
import pandas as pd

min_price_per_sq_m = 0
max_price_per_sq_m = 10000000000

districts = [20, 25, 26, 27, 28, 19]

if len(districts) == 1:
    district_value = districts[0]
    district_str = f"""district == '{district_value}'"""
else:
    district_value = tuple(districts)
    district_str = f"""district in {district_value}"""

# Simulate user's weights for features (amenities / places of interest) with quality & quantity scores
weight_num_primary_school = np.random.randint(0, 100) / 100.0
weight_quality_primary_school = np.random.randint(0, 100) / 100.0
weight_num_secondary_school = np.random.randint(0, 100) / 100.0
weight_quality_secondary_school = np.random.randint(0, 100) / 100.0
weight_num_hawker_center = np.random.randint(0, 100) / 100.0
weight_quality_hawker_center = np.random.randint(0, 100) / 100.0
weight_num_clinic = np.random.randint(0, 100) / 100.0
weight_quality_clinic = np.random.randint(0, 100) / 100.0
weight_other_public_sports_facility = np.random.randint(0, 100) / 100.0
weight_quality_other_public_sports_facility = np.random.randint(0, 100) / 100.0
weight_num_gym = np.random.randint(0, 100) / 100.0
weight_quality_gym = np.random.randint(0, 100) / 100.0
weight_num_community_center = np.random.randint(0, 100) / 100.0
weight_quality_community_center = np.random.randint(0, 100) / 100.0
weight_num_park = np.random.randint(0, 100) / 100.0
weight_quality_park = np.random.randint(0, 100) / 100.0
weight_num_mall = np.random.randint(0, 100) / 100.0
weight_quality_mall = np.random.randint(0, 100) / 100.0
weight_num_supermarket = np.random.randint(0, 100) / 100.0
weight_quality_supermarket = np.random.randint(0, 100) / 100.0

# Simulate user's weights for features (amenities / places of interest) with quantity scores ONLY. These amenities do not have quality scores.
weight_num_eating_establishment = np.random.randint(0, 100) / 100.0
weight_num_mrt = np.random.randint(0, 100) / 100.0
weight_num_carpark = np.random.randint(0, 100) / 100.0
weight_num_bus_stop = np.random.randint(0, 100) / 100.0
weight_num_taxi_stand = np.random.randint(0, 100) / 100.0

############################################################################################################
############################################################################################################
############################################################################################################
########## BELOW CODE MAY BE USED IN views.py AT THE APPROPRIATE PART OF THE CODE ##########################
############################################################################################################
############################################################################################################
############################################################################################################

query = f"""
                         SELECT project_id, project, project_type, lat, long, price_per_sqm, district, feature_ids_clinic, feature_ids_community_center, feature_ids_gym, feature_ids_hawker_center, feature_ids_mall, feature_ids_other_public_sports_facility, feature_ids_park, feature_ids_primary_school, feature_ids_secondary_school, feature_ids_supermarket, feature_ids_bus_stop, feature_ids_carpark, feature_ids_mrt, feature_ids_eating_establishment, feature_ids_taxi_stand, raw_num_bus_stop, raw_num_carpark, raw_num_clinic, raw_num_community_center, raw_num_eating_establishment, raw_num_gym, raw_num_hawker_center, raw_num_mall, raw_num_mrt, raw_num_other_public_sports_facility, raw_num_park, raw_num_primary_school, raw_num_secondary_school, raw_num_supermarket, raw_num_taxi_stand, raw_quality_clinic, raw_quality_community_center, raw_quality_gym, raw_quality_hawker_center, raw_quality_mall, raw_quality_other_public_sports_facility, raw_quality_park, raw_quality_primary_school, raw_quality_secondary_school, raw_quality_supermarket,
                                -- calculate overall score per property, given user weights
                                num_primary_school * {weight_num_primary_school}
                                + quality_primary_school * {weight_quality_primary_school}
                                + num_secondary_school * {weight_num_secondary_school}
                                + quality_secondary_school * {weight_quality_secondary_school}
                                + num_hawker_center * {weight_num_hawker_center}
                                + quality_hawker_center * {weight_quality_hawker_center}
                                + num_clinic * {weight_num_clinic}
                                + quality_clinic * {weight_quality_clinic}
                                + num_other_public_sports_facility * {weight_other_public_sports_facility}
                                + quality_other_public_sports_facility * {weight_quality_other_public_sports_facility}
                                + num_gym * {weight_num_gym}
                                + quality_gym * {weight_quality_gym}
                                + num_community_center * {weight_num_community_center}
                                + quality_community_center * {weight_quality_community_center}
                                + num_park * {weight_num_park}
                                + quality_park * {weight_quality_park}
                                + num_mall * {weight_num_mall}
                                + quality_mall * {weight_quality_mall}
                                + num_supermarket * {weight_num_supermarket}
                                + quality_supermarket * {weight_quality_supermarket}
                                + num_mrt * {weight_num_mrt}
                                + num_eating_establishment * {weight_num_eating_establishment}
                                + num_carpark * {weight_num_carpark}
                                + num_bus_stop* {weight_num_bus_stop}
                                + num_taxi_stand * {weight_num_taxi_stand}
                                as overall_score
                         FROM properties
                         WHERE price_per_sqm>={min_price_per_sq_m} and price_per_sqm<={max_price_per_sq_m}
                         AND """ + district_str + """
                         ORDER BY overall_score desc, price_per_sqm desc
                         LIMIT 10
                """

conn = sql.connect('../data/database.db')
matches = pd.read_sql_query(query, conn)

colnames_to_drop = []
for colname in matches.columns:
    if 'raw_' in colname:
        matches.loc[:, colname.lstrip("raw_")] = matches.loc[:, colname]
        colnames_to_drop.append(colname)
matches.drop(columns=colnames_to_drop, inplace=True)


# Function to get feature information from the `features` table, given a set of feature_ids.
def get_feature_information(feature_ids):
    '''
    @param feature_ids: a set of feature_ids
    @return feature information as a JSON string
    '''

    if len(feature_ids) == 0:
        return np.nan
    elif len(feature_ids) == 1:
        (elem,) = feature_ids
        feature_ids_str = f"""feature_id = {elem}"""
    else:
        feature_ids_str = f"""feature_id in {tuple(feature_ids)}"""

    query2 = f"""
                        SELECT name,num_ratings,avg_rating,lat,long,feature_type,address
                        FROM features
                        WHERE """ + feature_ids_str + """
                    """

    features = pd.read_sql_query(query2, conn)

    json = features.to_json(orient='records')

    return json


# Get the necessary amenities information for each amenities type, and place it inside a new column.
colnames_to_drop = []
for colname in matches.columns:
    if 'feature_ids_' in colname:
        new_colname = str(colname[12:])
        matches[new_colname] = matches.apply(lambda x: get_feature_information(eval(x[colname])), axis=1)
        colnames_to_drop.append(colname)
matches.drop(columns=colnames_to_drop, inplace=True)

####### save files ############

matches.to_csv("../data/processed/example_query.csv")

data = pd.read_csv("../data/processed/example_query.csv")