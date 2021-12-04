# Personalized Apartment Recommendations Project

Group members: Ansel, Daosheng, Key, Keith

Author of this readme: Ansel Lim.

## Introduction

The purpose of our web application is to help homebuyers in Singapore find their ideal homes based on their preferences.
In particular, we feel that while homebuyers can easily access price information online, it is not so easy for
homebuyers to select neighborhoods or property projects based on the amenities and facilities (e.g., parks, malls, or
schools) are available in the vicinity. Furthermore, different homebuyers may have different preferences with regard to
types of amenities and facilities. Therefore, the novelty of our project lies in how a homebuyer may define his
preferences, and our application returns *personalized* recommendations based on a scoring system which uses the
preference weight assignments defined by the user.

## What data was analyzed

A total of 10,614 properties were analyzed. Transaction records were obtained from the Housing and Development Board (
HDB) and the Urban Redevelopment Authority (URA). The HDB dataset contained sale prices, floor areas, and block and
street names for public housing apartments which were sold in the market from 2017 to 2021. The URA dataset contained
sale prices, floor areas, project names, and street names for private residential properties sold from 2017 to 2021.

A total of 32,695 amenities were analyzed. We obtained datasets containing the addresses and/or locations of amenities (
which we also call "features") in the city. The following table shows the fourteen different types of amenities for
which we had location information. For some of these amenity types, we computed **weighted quality scores** based on the
ratings (0 to 5 stars) these amenities received on Google Places. These scores were *weighted* scores in the sense that
the ratings were adjusted for the number of ratings an amenity receives in comparison to the total number of ratings
received by amenities of the same type.

| Type of place                                              | Standardized `feature_type` variable name | Quality scores available?  |
|------------------------------------------------------------|------------------------------------------|----------------------------|
| CHAS clinic                                                | `clinic`                                 | Yes                        |
| Community center                                           | `community_center`                       | Yes                        |
| Gym                                                        | `gym`                                    | Yes                        |
| Hawker center                                              | `hawker_center`                          | Yes                        |
| Shopping mall                                              | `mall`                                   | Yes                        |
| Other public sports facilities (mostly swimming complexes) | `other_public_sports_facility`           | Yes                        |
| Park                                                       | `park`                                   | Yes                        |
| Primary school                                             | `primary_school`                         | Yes                        |
| Secondary school                                           | `secondary_school`                       | Yes                        |
| Supermarket                                                | `supermarket`                            | Yes                        |
| Bus stop                                                   | `bus_stop`                               | No                         |
| Carpark                                                    | `carpark`                                | No                         |
| Subway (MRT) station                                       | `mrt`                                    | No                         |
| F&B (eating establishment)                                 | `eating_establishment`                   | No (too many to calculate) |
| Taxi stand                                                 | `taxi_stand`                             | No                         |

## Creating our custom database

With location data available for homes as well as amenities, we then computed, for each residential property project,
the **number of amenities** ("quantity score") as well as the **median weighted quality score of amenities** ("quality
score") in the residential property's vicinity. The definition of vicinity used was one-kilometer radius. To illustrate,
the residential property project "City Gate" at Beach Road has 10 gyms within a one-kilometer radius, and the median
weighted quality score of these 10 gyms is 3.59.

The data pertaining to quantity and quality scores of each property are stored in the `properties` table `database.db`,
a SQLite database. For each property, we also store location and price data. In a different table `features` in the same
database, we also store information pertaining to the amenities.

## How the application works

Our web application is simple and intuitive. The user specifies the parameters of his search by specifying a price
range. Since different properties have different floor areas, price per square meter is a simple way to compare home
prices across projects. The user may also restrict the search to a selection of districts in the city. Then, the user
specifies the priority and importance of various amenities.

![](docs/user_interface.png)

Based on the user's settings, a SQL query is then executed. The user's weights are applied to the precomputed scores
available for each property. A weighted score for each property is thereby calculated. The SQL query then returns a
shortlist of properties which are then passed as a GeoJSON object to our map, which is based on OneMap Singapore's
API (https://www.onemap.gov.sg/docs/), which is a mapping application designed for Singapore.

The user may then view the top recommendations (top 5 recommendations) as well as nearby amenities in the browser.

![](docs/mapping_example.png)

## Try it out yourself!

### Run the app on the web

The app is available
at [https://apartments-recommendation.herokuapp.com/](https://apartments-recommendation.herokuapp.com/). (inprogress)

### Run the app locally

Create a conda environment using the `environment.yml` file by running the following command in the project root.

```
conda env create -f environment.yml
```

Then, activate the new environment with `conda activate 6242-project`.

Then, run the app by entering `flask run` in your terminal window, and then go to http://127.0.0.1:5000/ in your
favorite browser.
