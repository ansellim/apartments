from app import app
from flask import render_template, request, redirect, url_for
from flask import jsonify # Added by Keith #
import json
import pandas as pd
import sqlite3 as sql
import os
import numpy as np

DB_FILEPATH = os.getcwd() + '/data/database.db'
geojson_list = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        req = request.form

        # Get user's input regarding minimum and maximum price per square meter. Since apartments have different square area (square footage), price per square per meter is a fairer metric.
        min_price_per_sq_m = request.form.get("minPricePerSqM").replace(',', '')
        max_price_per_sq_m = request.form.get("maxPricePerSqM").replace(',', '')
        if min_price_per_sq_m == '':
            min_price_per_sq_m = 0
        if max_price_per_sq_m == '':
            # no filter on max price per square meter is required
            # set to 10 billion (an arbitrarily large number) - there are probably no apartments exceeding this price
            max_price_per_sq_m = 10000000000

        # Get user's input regarding the districts (postal districts - these are different regions of the city) he wants to filter by.
        districts = []
        for k, v in req.items():
            if k[:7] == 'check_D':
                districts.append(k[7:])

        # Handle edge case where there is only 1 district selected by the user
        if len(districts) == 1:
            district_value = districts[0]
            district_str = f"""district == '{district_value}'"""
        else:
            district_value = tuple(districts)
            district_str = f"""district in {district_value}"""

        # Get user's weights for features (amenities / places of interest) with quality & quantity scores.
        weight_num_primary_school = int(request.form.get("num_primary_schools_slider"))/100.0
        weight_quality_primary_school = int(request.form.get("qlt_primary_schools_slider"))/100.0
        weight_num_secondary_school = int(request.form.get("num_secondary_schools_slider"))/100.0
        weight_quality_secondary_school = int(request.form.get("qlt_secondary_schools_slider"))/100.0
        weight_num_hawker_center = int(request.form.get("num_hawker_slider"))/100.0
        weight_quality_hawker_center = int(request.form.get("qlt_hawker_slider"))/100.0
        weight_num_clinic = int(request.form.get("num_clinic_slider"))/100.0
        weight_quality_clinic = int(request.form.get("qlt_clinic_slider"))/100.0
        weight_other_public_sports_facility = int(request.form.get("num_sports_facilities_slider"))/100.0
        weight_quality_other_public_sports_facility = int(request.form.get("qlt_sports_facilities_slider"))/100.0
        weight_num_gym = int(request.form.get("num_gym_slider"))/100.0
        weight_quality_gym = int(request.form.get("qlt_gym_slider"))/100.0
        weight_num_community_center = int(request.form.get("num_community_centers_slider"))/100.0
        weight_quality_community_center = int(request.form.get("qlt_community_centers_slider"))/100.0
        weight_num_park = int(request.form.get("num_parks_slider"))/100.0
        weight_quality_park = int(request.form.get("qlt_parks_slider"))/100.0
        weight_num_mall = int(request.form.get("num_malls_slider"))/100.0
        weight_quality_mall = int(request.form.get("qlt_malls_slider"))/100.0
        weight_num_supermarket = int(request.form.get("num_supermarkets_slider"))/100.0
        weight_quality_supermarket = int(request.form.get("qlt_supermarkets_slider"))/100.0

        # Get user's weights for features (amenities / places of interest) with quantity scores ONLY. These amenities do not have quality scores.
        weight_num_eating_establishment = int(request.form.get("num_eating_establishments_slider")) / 100.0
        weight_num_mrt = int(request.form.get("num_mrt_slider")) / 100.0
        weight_num_carpark = int(request.form.get("num_carparks_slider")) / 100.0
        weight_num_taxi_stand = int(request.form.get("num_taxi_stands_slider")) / 100.0

        query = f"""
                         SELECT project_id, project, project_type, lat, long, price_per_sqm, district, feature_ids_clinic, feature_ids_community_center, feature_ids_gym, feature_ids_hawker_center, feature_ids_mall, feature_ids_other_public_sports_facility, feature_ids_park, feature_ids_primary_school, feature_ids_secondary_school, feature_ids_supermarket, feature_ids_carpark, feature_ids_mrt, feature_ids_eating_establishment, feature_ids_taxi_stand, raw_num_carpark, raw_num_clinic, raw_num_community_center, raw_num_eating_establishment, raw_num_gym, raw_num_hawker_center, raw_num_mall, raw_num_mrt, raw_num_other_public_sports_facility, raw_num_park, raw_num_primary_school, raw_num_secondary_school, raw_num_supermarket, raw_num_taxi_stand, raw_quality_clinic, raw_quality_community_center, raw_quality_gym, raw_quality_hawker_center, raw_quality_mall, raw_quality_other_public_sports_facility, raw_quality_park, raw_quality_primary_school, raw_quality_secondary_school, raw_quality_supermarket,
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
                                + num_taxi_stand * {weight_num_taxi_stand}
                                as overall_score
                         FROM properties
                         WHERE price_per_sqm>={min_price_per_sq_m} and price_per_sqm<={max_price_per_sq_m}
                         AND """ + district_str + """
                         ORDER BY overall_score desc, price_per_sqm desc
                         LIMIT 5
                """
        conn = sql.connect(DB_FILEPATH)
        matches = pd.read_sql_query(query, conn)

        if matches.empty:
            return render_template("no_results.html")
            # raise ValueError("Oops! There are no available housing projects for this selection. Please try again.")

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

        #function that takes in one amenity for a given feature and return GeoJson format
        def get_amenity_geojson(amenity, index, description):
            feature = {'type':'Feature',
                       'properties':{},
                       'geometry':{'type':'Point',
                                   'coordinates':[]}}
            feature['geometry']['coordinates'] = [float(amenity["long"]),float(amenity["lat"])]
            feature['properties']['item'] = index + 1
            feature['properties']['description'] = description
            feature['properties']['name'] = amenity['name']
            return feature

        #Convert dataframe to GeoJson format
        #geojson_list = []
        for index, row in matches.iterrows():
            #Add property to geojson list
            feature = {'type':'Feature',
                       'properties':{},
                       'geometry':{'type':'Point',
                                   'coordinates':[]}}
            feature['geometry']['coordinates'] = [row["long"],row["lat"]]
            feature['properties']['item'] = index + 1
            feature['properties']['description'] = 'Property'
            feature['properties']['name'] = row['project']
            feature['properties']['price_per_sqm'] = row['price_per_sqm']
            feature['properties']['overall_score'] = row['overall_score']
            geojson_list.append(feature)

            #For given property, add amenity to geojson list
            if not pd.isna(row.clinic):
                for amenity in json.loads(row.clinic):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Clinic')
                    geojson_list.append(feature)

            if not pd.isna(row.community_center):
                for amenity in json.loads(row.community_center):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Community Center')
                    geojson_list.append(feature)

            if not pd.isna(row.gym):
                for amenity in json.loads(row.gym):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Gym')
                    geojson_list.append(feature)

            if not pd.isna(row.hawker_center):
                for amenity in json.loads(row.hawker_center):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Hawker Center')
                    geojson_list.append(feature)

            if not pd.isna(row.mall):
                for amenity in json.loads(row.mall):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Mall')
                    geojson_list.append(feature)

            if not pd.isna(row.other_public_sports_facility):
                for amenity in json.loads(row.other_public_sports_facility):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Sport')
                    geojson_list.append(feature)

            if not pd.isna(row.park):
                for amenity in json.loads(row.park):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Park')
                    geojson_list.append(feature)

            if not pd.isna(row.primary_school):
                for amenity in json.loads(row.primary_school):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Primary School')
                    geojson_list.append(feature)

            if not pd.isna(row.secondary_school):
                for amenity in json.loads(row.secondary_school):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Secondary School')
                    geojson_list.append(feature)

            if not pd.isna(row.supermarket):
                for amenity in json.loads(row.supermarket):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Supermarket')
                    geojson_list.append(feature)

            if not pd.isna(row.carpark):
                for amenity in json.loads(row.carpark):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Carpark')
                    geojson_list.append(feature)

            if not pd.isna(row.mrt):
                for amenity in json.loads(row.mrt):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Mrt')
                    geojson_list.append(feature)

            if not pd.isna(row.eating_establishment):
                for amenity in json.loads(row.eating_establishment):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Eating')
                    geojson_list.append(feature)

            if not pd.isna(row.taxi_stand):
                for amenity in json.loads(row.taxi_stand):
                    feature = get_amenity_geojson(amenity=amenity, index=index, description='Taxi Stand')
                    geojson_list.append(feature)

        #print(geojson_list)
        return redirect(url_for('map', geojson_response = jsonify(geojson_list)))       #Pass matches in geojson format to map() function that renders map.html
    return render_template("index.html")


@app.route("/map")
def map():
    geojson_response_str = request.args['geojson_response']
    geojson_response = jsonify(geojson_response_str)
    return render_template("map.html", geojson_response = geojson_response)     #pass matches in geojson format to map.html


@app.route("/GeoJSon_properties")
def create_GeoJSon():
    return jsonify(geojson_list)


######################################
# Added by Keith for testing purpose #
######################################

@app.route("/GeoJSon_testing")
def create_GeoJSon_object():

    GeoJSon_samples = [
    #1 Property details #
    {
        "type": "Feature",
        "properties": {
            "item": 1,
            "description": "Property",
            "name": "119 ANG MO KIO AVE 3",
            "price_per_sqm": 4451.222288,
            "overall_score": 11.145,
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.8446989, 1.369563443]
        }
    },

    {
        "type": "Feature",
        "properties": {
            "item": 1,
            "description": "School",
            "name": "TECK GHEE PRIMARY SCHOOL",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.851009800453, 1.36565018546903]
        }
    },

    {
        "type": "Feature",
        "properties": {
            "item": 1,
            "description": "Mall",
            "name": "AMK Hub",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.8484398, 1.36953]
        }
    },

    {
        "type": "Feature",
        "properties": {
            "item": 1,
            "description": "Supermarket",
            "name": "SHENG SIONG SUPERMARKET",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.843413231524, 1.37018860668947]
        }
    },

    #2 Property details #
    {
        "type": "Feature",
        "properties": {
            "item": 2,
            "description": "Property",
            "name": "120 ANG MO KIO AVE 3",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.8445948, 1.370047397]
        }
    },

    {
        "type": "Feature",
        "properties": {
            "item": 2,
            "description": "School",
            "name": "TECK GHEE PRIMARY SCHOOL",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.851009800453, 1.36565018546903]
        }
    },

    {
        "type": "Feature",
        "properties": {
            "item": 2,
            "description": "Mall",
            "name": "AMK Hub",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.8484398, 1.36953]
        }
    },

    {
        "type": "Feature",
        "properties": {
            "item": 2,
            "description": "Supermarket",
            "name": "SHENG SIONG SUPERMARKET",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.843413231524, 1.37018860668947]
        }
    },

    #3 Property details #
    {
        "type": "Feature",
        "properties": {
            "item": 3,
            "description": "Property",
            "name": "201 ANG MO KIO AVE 3",
        },
        "geometry": {
            "type": "Point",
            "coordinates": [103.8445648, 1.368849627]
        }
    }
]
    return jsonify(GeoJSon_samples)

# End of code added by Keith #
##############################

@app.route("/no_results")
def no_results():
    return render_template("no_results.html")
