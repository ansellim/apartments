from app import app
from flask import render_template
from flask import request, redirect
import pandas as pd
import sqlite3 as sql

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
                districts.append(k[6:])

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
        weight_num_mrt = int(request.form.get("num_mrt_slider"))/100.0
        weight_num_carpark = int(request.form.get("num_carparks_slider"))/100.0
        weight_num_bus_stop = int(request.form.get("num_bus_stops_slider"))/100.0
        weight_num_taxi_stand = int(request.form.get("num_taxi_stands_slider"))/100.0

        #Logic to query precomputed scores, compute overall score and return top 5 recommendations
        query = f"""
                 SELECT project_id, price_per_sqm, area, district,
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
                 AND """ + district_str + f"""
                 ORDER BY overall_score desc
                 LIMIT 5
        """
        property_db = sql.connect('data/database.db')
        top_five_property = pd.read_sql_query(query, property_db)
        print(top_five_property)

        return redirect(request.url)
    return render_template("index.html")

@app.route("/about")
def about():
    return """
    <h1 style='color: red;'>I'm a red H1 heading!</h1>
    <p>This is a lovely little paragraph</p>
    <code>Flask is <em>awesome</em></code>
    """
