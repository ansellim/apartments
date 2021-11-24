from app import app
from flask import render_template
from flask import request, redirect
import pandas as pd
import sqlite3 as sql

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        req = request.form
        # print(req)

        minPrice = request.form.get("minPrice")
        maxPrice = request.form.get("maxPrice")
        if minPrice == '':
            minPrice = 0
        if maxPrice == '':
            # set to 10b.. probably no houses above this price.....?
            maxPrice = 10000000000

        minArea = request.form.get("minArea")
        maxArea = request.form.get("maxArea")
        if minArea == '':
            minArea = 0
        if maxArea == '':
            # set to 10b sqm.. bigger than the size of SG?!
            maxArea = 10000000000

        districts = []
        for k, v in req.items():
            if k[:7] == 'check_D':
                districts.append(k[6:])

        num_primary_schools = int(request.form.get("num_primary_schools_slider"))/100.0
        qlt_primary_schools = int(request.form.get("qlt_primary_schools_slider"))/100.0
        num_secondary_schools = int(request.form.get("num_secondary_schools_slider"))/100.0
        num_hawker = int(request.form.get("num_hawker_slider"))/100.0
        qlt_hawker = int(request.form.get("qlt_hawker_slider"))/100.0
        num_eating_establishments = int(request.form.get("num_eating_establishments_slider"))/100.0
        num_chas_clinics = int(request.form.get("num_chas_clinics_slider"))/100.0
        num_sports_facilities = int(request.form.get("num_sports_facilities_slider"))/100.0
        num_community_centers = int(request.form.get("num_community_centers_slider"))/100.0
        num_parks = int(request.form.get("num_parks_slider"))/100.0
        num_malls = int(request.form.get("num_malls_slider"))/100.0
        qlt_malls = int(request.form.get("qlt_malls_slider"))/100.0
        num_supermarkets = int(request.form.get("num_supermarkets_slider"))/100.0
        num_mrt = int(request.form.get("num_mrt_slider"))/100.0
        num_carparks = int(request.form.get("num_carparks_slider"))/100.0
        num_bus_stops = int(request.form.get("num_bus_stops_slider"))/100.0
        num_taxi_stands = int(request.form.get("num_taxi_stands_slider"))/100.0

        print(minPrice,maxPrice,minArea,maxArea,districts,num_primary_schools,qlt_primary_schools,num_secondary_schools,num_hawker,qlt_hawker,num_eating_establishments,num_chas_clinics,num_sports_facilities,num_community_centers,num_parks,num_malls,qlt_malls,num_supermarkets,num_mrt,num_carparks,num_bus_stops,num_taxi_stands)

        #Handle edge case where there is only 1 district selected
        if len(districts) == 1:
            district_value = districts[0]
            district_str = f"""district == '{district_value}'"""
        else:
            district_value = tuple(districts)
            district_str = f"""district in {district_value}"""

        #Logic to query precomputed scores, compute overall score and return top 5 recommendations
        query = f"""
                 SELECT property_id, price, area, district,
                        num_primary_schools_score * {num_primary_schools}
                        + qlt_primary_schools_score * {qlt_primary_schools}
                        + num_secondary_schools_score * {num_secondary_schools}
                        + num_hawker_score * {num_hawker}
                        + qlt_hawker_score * {qlt_hawker}
                        + num_eating_establishments_score * {num_eating_establishments}
                        + num_chas_clinics_score * {num_chas_clinics}
                        + num_sports_facilities_score * {num_sports_facilities}
                        + num_community_centers_score * {num_community_centers}
                        + num_parks_score * {num_parks}
                        + num_malls_score * {num_malls}
                        + qlt_malls_score * {qlt_malls}
                        + num_supermarkets_score * {num_supermarkets}
                        + num_mrt_score * {num_mrt}
                        + num_carparks_score * {num_carparks}
                        + num_bus_stops_score * {num_bus_stops}
                        + num_taxi_stands_score * {num_taxi_stands}
                        as overall_score
                 FROM property
                 WHERE price>={minPrice} and price<={maxPrice} and area>={minArea} and area<={maxArea}
                 AND """ + district_str + f"""
                 ORDER BY overall_score desc
                 LIMIT 5
        """
        property_db = sql.connect('data/property.db')
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
