# CSE6242 PROJECT
Ansel, Daosheng, Key, Keith

# LATEST UPDATES

## update 25/11/21 8am - ansel 
No changes to repository. Just some additional comments to explain what was done. The script for computing quality scores and quantity scores for HDB and Condominiums will be run today and the data will be made available after completion. Quality score computation is only available for (iirc) ten different feature types, and the feature scores are calculated according to what Key wrote in the report. For each property, feature quality scores in each feature type are aggregated to give the median (to be clear, each feature type is treated independently). Where NO features of a certain type exist within 1km of a property, the feature quality score is `np.nan` and the number of features of that type is 0. For now, please assume that the csv file will broadly follow what you see in df_with_features and df_with_features_scaled, both of which contain example data from just 10 properties and 10 features. So, please build the database and develop according to what you see there. For quantity scores, please use the attributes prefixed by 'recomputed' for now as I need to verify that the recomputation works but it is likely that I will be renaming the column names later. A 'feature' is a place of interest within 1 km of a property. A property is a property project: for a condominium, it's the condominium project; for HDB, it's the HDB block. The data available for each project is fairly standardized, but in the dataframe, some additional attributes applicable to only condo or HDB are prefixed with 'condo_' or 'hdb_'.

### update 25/11/21 3.36am - ansel
Reorganized data. Raw data now in data/raw. Processed data will remain in data/processed. Intermediary data in data/with_quality_scores. Added quality data to multiple feature types: pls refer to df_with_features for example with just 10 properties and 10 features (a feature is a "place of interest" within 1km of a property). Note that "add_quality_data.py" is new script for computing quality metrics and recomputing quantity metrics; please use the new recalculated values instead of previously old calculated values. Script has to be run later over many hours for the actual dataset. For now, please work with the "df_with_features.csv" (unscaled data) or "df_with_features_scaled" (scaled data); this will be, apart from minor modifications and refactoring, the schema of the data file I will produce.

### update 24/11/21 9.10pm - key
Managed to get the database and data retrieval part working.
Database is stored in data/property.db, currently loaded a dummy dataset into the database, you can view the dummy dataset at data/property.csv

If you want to create a database and load data into it, you just have to do the following steps:
``` 
import sqlite3 as sql
property_db = sql.connect('property.db')
df.to_sql('property', property_db)
```

Lastly, in app/views.py, have set up the logic to retrieve the quantity and quality scores from the database, compute overall score and return top 5 recommendations.

### update 18/11/21 11.39pm - daosheng
Published first copy of questionnaire, served via Flask. html file saved in .app/templates/index.html and variables from the form can be accessed in .app/views.py
Run the command "flask run" in terminal to test.
Next steps would be to call the scoring system using the saved variables, return a result, then redirect to the map UI page

### update 31/10/21 2.10am - ansel
ura.csv is available. however, batch 3 URA data is missing ("Invalid service" error message) -- not sure why...needs further tweaking here.

### update 31/10/21 12.26am - ansel
After much debugging, I have managed to write code to download data from URA and LTA. The data is still in raw json format, but I intend to convert them into tabular format (probably csv) soon. Run the code and the data will be stored in a file called "cached_data" (I have not git-tracked this).

Future work: need to look at this interesting website https://ual.sg/post/2020/06/24/guide-for-open-urban-data-in-singapore/ in more detail and see what "mildly interesting" or "mildly novel" stuff we can do...
1. Maybe we can create some kind of measure of greenery using data from Trees.SG http://trees.sg/?
2. Thinking of using this https://tih-dev.stb.gov.sg/content-api/apis to extract amenities information (e.g. malls).

-------------

# REQUIRED API KEYS.
Place these inside a .env file.
1. URA API key. Sign up here: https://www.ura.gov.sg/maps/api/reg.html.
2. LTA API key. Sign up here: https://datamall.lta.gov.sg/content/datamall/en/request-for-api.html.

--------------

# QUICK LINKS
1. Project plan document: https://docs.google.com/spreadsheets/d/19M5vhcFxTbeEmVSc2c6b9-ALzIIv0_NME3J5ut9BpyA/edit#gid=0
2. Link to our Google Drive folder: https://drive.google.com/drive/folders/1-Q8OQy3JlwRmzUFlaK5vkOl4Wkx4wleY?usp=sharing.

# INTERESTING WEBSITES
1. https://ual.sg/post/2020/06/24/guide-for-open-urban-data-in-singapore/
2. https://www.openstreetmap.org
3. https://landtransportsg.readthedocs.io/en/latest/
4. https://exploretrees.sg, created by this guy: https://github.com/cheeaun; his other projects are at https://cheeaun.com/projects

## URA API:
1. Private residential property transactions: https://www.ura.gov.sg/maps/api/#private-residential-property-transactions.
2. maybe we can also consider using other data from here, perhaps car park available lots? maybe some people might be interested in whether there's enough parking space near their homes. https://www.ura.gov.sg/maps/api/#car-park-available-lots.

## LTA DATAMALL:
1. What data is available? check out https://datamall.lta.gov.sg/content/datamall/en/dynamic-data.html
2. User guide: https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf
