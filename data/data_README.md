# README for `data` folder

The `data` folder contains the data used in the project.

The SQLite database is `database.db` in the `data` folder.

## `processed` subdirectory

The `processed` subdirectory contains the data used to create the database. In particular the database contains
information from `df_with_features.csv` (processed into the `properties` table) as well as `features.csv` (this makes
the `features` table).

1. `df.csv` contains condominium data with quantity scores
2. `df_hdb.csv` contains HDB data with quantity scores
3. `df_with_features.csv` is the combination of the last two files, but with quality scores as well
4. `df_with_features_binned.csv`, `df_with_features_scaled.csv` and `df_with_features_scaled_with_deprecated.csv` are
   temporary "views" of the `df_with_features.csv` file, with the numeric scores binned and scaled.
5. `features.csv` contains information of the amenities.

## `raw` subdirectory

| File                                                                      | Description                                                                | Source                                                                                            |
|---------------------------------------------------------------------------|----------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `amenities.csv `                                                          | List of CHAS clinics, community centers, gyms, sports facilities           | Data.gov.sg                                                                                       |
| `batch1.json`, `batch2.json`, `batch3.json`,`batch4.json`                 | Raw JSON data from Urban Redevelopment Authority API (condominium transaction data) | Urban Redevelopment Authority API (https://www.ura.gov.sg/maps/api/#private-residential-property) |
| `ura.csv`                                                                 | Private condominium transaction data from the last 5 years (accessed Dec 2021) | Urban Redevelopment Authority API                                                                 |
| `bus_stops.csv`                                                           | List of bus stops                                                          | Land Transport Authority                                                                          |
| `carparks.csv`                                                            | List of carparks                                                           | Urban Redevelopment Authority                                                                     |
| `data_hawker.csv`                                                         | List of hawker centers                                                     | Data.gov.sg                                                                                       |
| `data_malls.csv`                                                          | List of shopping malls                                                     | Data.gov.sg                                                                                       |
| `data_MRT.csv`                                                            | List of MRT stations                                                       | Land Transport Authority                                                                          |
| `data_prischools.csv`                                                     | List of primary schools                                                    | Data.gov.sg                                                                                       |
| `eating-establishments.kml`                                               | List of eating establishments                                              | Data.gov.sg                                                                                       |
| `eating_establishments.csv`                                               | Processed list of eating establishments (kml to csv)                       |                                                                                                   |
| `general-information-of-schools.csv`                                      | List of schools in Singapore                                               | Data.gov.sg                                                                                       |                                                              |
| `listing-of-supermarkets.csv`                                             | List of supermarkets                                                       | Data.gov.sg                                                                                       |
| `supermarkets.csv`                                                        | Cleaned-up list of supermarkets                                            |                                                                                                   |
| `parks-kml.kml`                                                           | List of parks                                                              | Data.gov.sg                                                                                       |
| `parks.csv`                                                               | Processed list of parks (kml to csv) |                                                                                                   |
| `postal_codes_mapping.csv`                                                |CSV file created by Ansel to help with mapping of postal codes to districts. | Based on URA website                                                                              |                                                                              |
| `resale-flat-prices-based-on-registration-date-from-jan-2017-onwards.csv` |HDB resale data from 2017 to current | Data.gov.sg                                                                                       |
| `hdb_aggregated.csv`                                                      | HDB data (HDB resale data from 2017 to current), aggregated by block |                                                                                                   |
| `secondary_schools.csv`                                                   | List of secondary schools                                                  | Data.gov.sg                                                                                       |
| `taxi_stands.csv`                                                         | List of taxi stands | Urban Redevelopment Authority |                                                                    |

## `with_quality_scores` subdirectory

The files in this subdirectory are just processed versions of the a amenities information, but with quality scores.

1. `clinics.csv`: CHAS clinics with quality scores
2. `community_centers.csv`: community centers with quality scores
3. `gyms.csv`: gyms with quality scores
4. `hawker_centers.csv`: hawker centers with quality scores
5. `malls.csv`: malls with quality scores
6. `other_public_sports_facilities`: public sports facilities (mostly swimming complexes) with quality scopres
7. `parks.csv`: parks with quality scores
8. `primary_schools.csv`: primary schools with quality scores
9. `secondary_schools.csv`: secondary schools with quality scores
10. `supermarkets.csv`: supermarkets with quality scores

The information in these ten files was incorporated into the dataframes in the `processed` subdirectory.