# CSE6242 PROJECT

Ansel, Daosheng, Key, Keith

# LATEST UPDATES

## Update 25/11/21 11pm-12mn - Ansel. A partial dataset is now available for use! Harmonization of 'schema' of `df_with_features_scaled.csv` dataframe to make column names more sensible. Corrected add_quality_data.py script.

While the full dataset is pending script execution, a **partial dataset** of 2000 properties (1000 condos and 1000 HDB
flats) is now available for immediate use and prototyping of downstream tasks. Please refer
to `data/processed/df_with_features_scaled.csv` and `data/processed/features.csv`.

Read the following explanation to find out about the column names in `data/processed/df_with_features_scaled.csv`
and `data/processed/features.csv`, which are the two csv files that can be the two relations in our database. The former
contains properties & nearby features (a property's nearby 'features' are so-called places of interest which are within
a 1-kilometer radius), whereas the latter contains all features. Note that all properties and features have unique IDs
which can serve as keys in the database.

In the earlier update this morning, I didn't want to drop the previously computed `num_{feature}` columns from the
dataframe of properties and nearby features, because I was thinking of comparing the old and new computed values.
However, I now think that this is not of interest, so I'll be dropping the old columns and harmonizing the column names
that we actually want to use.

So, please check out the description of the tables here:

### `features.csv` - schema is unchanged from 25/11/21 8.30AM description

A "feature" is a place of interest. There are different `feature_type`'s, such as "mall", "gym", or "hawker_center".

| Attribute| Description |
| ------ | ----------- |
| `feature_id` | A unique identiifer for each feature |
| `name` | Name of feature |
| `google_place_id` | A unique place ID assigned to a place |
| `num_ratings` | Number of ratings on Google Places API |
| `avg_rating` | Average rating on Google Places API (max of 5 stars) |
| `weighted_rating` | A weighted rating, calculated according to formula in report |
| `W` | a "normalization" ratio used in calculation of weighted rating. Equals the number of ratings for a feature divided by sum of number of ratings for all features with the same feature type. |
| `lat` | Latitude |
| `long` | Longitude |
| `address` | Address of the feature, if available |
| `feature_type` | Type of feature (type of place of interest) |

### Feature types used in the `feature_type` column in `features.csv`- definitions are unchanged from 25/11/21 8.30AM description

| Type of place | `feature_type` in features.csv | Quality scores available? |
| ------ | --- | --- |
| CHAS clinic | `clinic` | Yes |
| Community center | `community_center` | Yes |
| Gym | `gym` | Yes |
| Hawker center | `hawker_center` | Yes |
| Shopping mall | `mall` | Yes |
| Other public sports facilities (mostly swimming complexes) | `other_public_sports_facility` | Yes |
| Park | `park` | Yes |
| Primary school | `primary_school` | Yes |
| Secondary school | `secondary_school` | Yes |
| Supermarket | `supermarket` | Yes |
| Bus stop | `bus_stop` | No |
| Carpark | `carpark` | No |
| MRT station | `mrt` | No |
| F&B (eating establishment) | `eating_establishment` | No (too many to calculate) |
| Taxi stand | `taxi_stand` | No |

### `df_with_features.scaled.csv` -- **CHANGED SCHEMA FROM 25/11/21 8.30AM**

A dataframe of property projects (a 'project' is an HDB block or a condo project), with quantity and *median* quality
scores for each feature type. Since a feature is a place of interest, such as 'Bukit Timah Hawker Center' or 'Clementi
MRT', it follows that a feature type is a type of place of interest, for example a community center or CHAS clinic. For
each property, we look at a one-kilometer radius calculated based on latitude and longitude.

For each property, therefore, we count the number of features (within each feature type) within a one-kilometer radius,
as well as compute the median `quality` score of features (within each feature type), again within that one-kilometer
radius. The 'quality' score of a feature is a rating (out of a maximum of 5 stars) extracted from the Google Places API,
normalized/weighted by the number of reviews that feature received compared to other features of the same feature type.

To be clear, given a property, for each feature type, the number of features within a 1-kilometer radius is the quantity
score, and the median of the quality scores of features within that same 1-kilometer radius is the quality score. Since
different features may have different ranges of scores (this is more of an issue for quantity score, since quality score
is on a Likert scale), the quality and quantity scores are scaled according to min-max scaling.

| Attribute| Description |
| ------ | ----------- |
| `project_id` | A unique identifier for each property |
| `project` | Name of property 'project': condominium name or HDB block |
| `project_type` | Project type: HDB or condominium |
| `lat` | Latitude |
| `long` | Longitude |
| `price_per_sqm` | Average price per square meter of units in this property (historical) |
| `district` | Postal district |
| `num_` + any `feature_type` in the list of feature types | (scaled) quantity score: scaled number of features of that `feature_type` within 1km of the property  |
| `feature_ids_` + any `feature_type` | a list of `feature_id`'s of that `feature_type` within 1km of the property; can join with `features.csv` to get feature data attributes |
| `quality_` + any `feature_type` | (scaled) quality score: scaled median quality score (weighted/normalized Google Places API rating) of features of that `feature_type` within 1km of the property |
| `condo_street` | Street name (only available for condominiums) |
| `condo_market_segment` | Market segment (only available for condos) |
| `condo_commonest_tenure` | Commonest tenure type (only available for condominiums) |
| `hdb_avg_floor_area_sqm` | Average floor area of transacted units in the property  (available for HDB only) |
| `hdb_avg_resale_price` | Average resale price of units in the property [historical] (available for HDB only) | 

------------------------------------------------------

## Update 25/11/21 8.30AM - Ansel. EXPLANATION OF THE DATAFRAMES.

Explanation of what attributes are available in `df_with_features.scaled.csv` (properties + features)
and `features.csv` (Features) in the `data/processed` folder.

### `features.csv`

A "feature" is a place of interest.

| Attribute| Description |
| ------ | ----------- |
| `feature_id` | A unique identiifer for each feature |
| `name` | Name of feature |
| `google_place_id` | A unique place ID assigned to a place |
| `num_ratings` | Number of ratings on Google Places API |
| `avg_rating` | Average rating on Google Places API (max of 5 stars) |
| `weighted_rating` | A weighted rating, calculated according to formula in report |
| `W` | a "normalization" ratio used in calculation of weighted rating. Equals the number of ratings for a feature divided by sum of number of ratings for all features with the same feature type. |
| `lat` | Latitude |
| `long` | Longitude |
| `address` | Address of the feature, if available |
| `feature_type` | Type of feature (type of place of interest) |

### Feature types

| Type of place | `feature_type` in features.csv | Quality scores available? |
| ------ | --- | --- |
| CHAS clinic | `clinic` | Yes |
| Community center | `community_center` | Yes |
| Gym | `gym` | Yes |
| Hawker center | `hawker_center` | Yes |
| Shopping mall | `mall` | Yes |
| Other public sports facilities (mostly swimming complexes) | `other_public_sports_facility` | Yes |
| Park | `park` | Yes |
| Primary school | `primary_school` | Yes |
| Secondary school | `secondary_school` | Yes |
| Supermarket | `supermarket` | Yes |
| Bus stop | `bus_stop` | No |
| Carpark | `carpark` | No |
| MRT station | `mrt` | No |
| F&B (eating establishment) | `eating_establishment` | No (too many to calculate) |
| Taxi stand | `taxi_stand` | No |

### `df_with_features.scaled.csv`

A dataframe of properties (a "property" is an HDB block or a condo project), with quantity and quality scores for each
feature type. A feature type is a type of place of interest, for example community center or CHAS clinic. For each
property, we look at a one-kilometer radius calculated based on latitude and longitude. For each property, therefore, we
count number of features (for each feature type) within the one-kilometer radius, as well as the
median `weighted_rating` (a weighted Google Places API rating [maximum of 5 stars] normalized by number of ratings) of
the features (for each feature type) within the one-kilometer radius of the property. Given a property, for each feature
type, the number of features is the quality score, and the median `weighted_rating` is the quantity score. The quality
and quantity scores are scaled according to min-max scaling.

Not all attributes are listed here:

| Attribute| Description |
| ------ | ----------- |
| `project_id` | A unique identifier for each property |
| `condo_street` | Street name (only available for condominiums |
| `project` | Name of property: condominium name or HDB block |
| `condo_market_segment` | Market segment (only available for condos) |
| `lat` | Latitude |
| `long` | Longitude |
| `price_per_sqm` | Average price per square meter of units in this property (historical) |
| `district` | Postal district |
| `condo_commonest_tenure` | Commonest tenure type (only available for condos) |
| `recomputed_num_` + any `feature_type` | (scaled) quantity score: scaled number of features of that `feature_type` within 1km of the property  |
| `feature_ids_` + any `feature_type` | (scaled) a list of `feature_id`'s of that `feature_type` within 1km of the property; can join with `features.csv` to get feature data attributes |
| `median_weighted_score_` + any `feature_type` | (scaled) quality score: scaled median weighted rating of features of that `feature_type` within 1km of the property |
| `hdb_avg_floor_area_sqm` | Average floor area of transacted units in the property  (available for HDB only) |
| `hdb_avg_resale_price` | Average resale price of units in the property [historical] (available for HDB only) | 

## update 25/11/21 8am - ansel

No changes to repository. Just some additional comments to explain what was done. The script for computing quality
scores and quantity scores for HDB and Condominiums will be run today and the data will be made available after
completion. Quality score computation is only available for (iirc) ten different feature types, and the feature scores
are calculated according to what Key wrote in the report. For each property, feature quality scores in each feature type
are aggregated to give the median (to be clear, each feature type is treated independently). Where NO features of a
certain type exist within 1km of a property, the feature quality score is `np.nan` and the number of features of that
type is 0. For now, please assume that the csv file will broadly follow what you see in df_with_features and
df_with_features_scaled, both of which contain example data from just 10 properties and 10 features. So, please build
the database and develop according to what you see there. For quantity scores, please use the attributes prefixed by '
recomputed' for now as I need to verify that the recomputation works but it is likely that I will be renaming the column
names later. A 'feature' is a place of interest within 1 km of a property. A property is a property project: for a
condominium, it's the condominium project; for HDB, it's the HDB block. The data available for each project is fairly
standardized, but in the dataframe, some additional attributes applicable to only condo or HDB are prefixed with '
condo_' or 'hdb_'.

### update 25/11/21 3.36am - ansel

Reorganized data. Raw data now in data/raw. Processed data will remain in data/processed. Intermediary data in
data/with_quality_scores. Added quality data to multiple feature types: pls refer to df_with_features for example with
just 10 properties and 10 features (a feature is a "place of interest" within 1km of a property). Note that "
add_quality_data.py" is new script for computing quality metrics and recomputing quantity metrics; please use the new
recalculated values instead of previously old calculated values. Script has to be run later over many hours for the
actual dataset. For now, please work with the "df_with_features.csv" (unscaled data) or "df_with_features_scaled" (
scaled data); this will be, apart from minor modifications and refactoring, the schema of the data file I will produce.

### update 24/11/21 9.10pm - key

Managed to get the database and data retrieval part working. Database is stored in data/property.db, currently loaded a
dummy dataset into the database, you can view the dummy dataset at data/property.csv

If you want to create a database and load data into it, you just have to do the following steps:

``` 
import sqlite3 as sql
property_db = sql.connect('property.db')
df.to_sql('property', property_db)
```

Lastly, in app/views.py, have set up the logic to retrieve the quantity and quality scores from the database, compute
overall score and return top 5 recommendations.

### update 18/11/21 11.39pm - daosheng

Published first copy of questionnaire, served via Flask. html file saved in .app/templates/index.html and variables from
the form can be accessed in .app/views.py Run the command "flask run" in terminal to test. Next steps would be to call
the scoring system using the saved variables, return a result, then redirect to the map UI page

### update 31/10/21 2.10am - ansel

ura.csv is available. however, batch 3 URA data is missing ("Invalid service" error message) -- not sure why...needs
further tweaking here.

### update 31/10/21 12.26am - ansel

After much debugging, I have managed to write code to download data from URA and LTA. The data is still in raw json
format, but I intend to convert them into tabular format (probably csv) soon. Run the code and the data will be stored
in a file called "cached_data" (I have not git-tracked this).

Future work: need to look at this interesting
website https://ual.sg/post/2020/06/24/guide-for-open-urban-data-in-singapore/ in more detail and see what "mildly
interesting" or "mildly novel" stuff we can do...

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
2. Link to our Google Drive folder: https://drive.google.com/drive/folders/1-Q8OQy3JlwRmzUFlaK5vkOl4Wkx4wleY?usp=sharing
   .

# INTERESTING WEBSITES

1. https://ual.sg/post/2020/06/24/guide-for-open-urban-data-in-singapore/
2. https://www.openstreetmap.org
3. https://landtransportsg.readthedocs.io/en/latest/
4. https://exploretrees.sg, created by this guy: https://github.com/cheeaun; his other projects are
   at https://cheeaun.com/projects

## URA API:

1. Private residential property transactions: https://www.ura.gov.sg/maps/api/#private-residential-property-transactions
   .
2. maybe we can also consider using other data from here, perhaps car park available lots? maybe some people might be
   interested in whether there's enough parking space near their
   homes. https://www.ura.gov.sg/maps/api/#car-park-available-lots.

## LTA DATAMALL:

1. What data is available? check out https://datamall.lta.gov.sg/content/datamall/en/dynamic-data.html
2. User guide: https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf
