# CSE6242 PROJECT
Ansel, Daosheng, Key, Keith

# LATEST UPDATES

### update 24/11/21 9.10pm - key
Managed to get the database and data retrieval part working.
Database is stored in data/property.db, currently loaded a dummy dataset into the database, you can view the dummy dataset at data/property.csv

If you want to create a database and load data into it, you just have to do the following steps:
> import sqlite3 as sql
  property_db = sql.connect('property.db')
  df.to_sql('property', property_db)

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
