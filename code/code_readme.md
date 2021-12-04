# README for code folder

Author: Ansel Lim. Date: December 4, 2021.

The code folder contains the code used for processing the data and performing scoring.

The scripts were run in the following order:

1. get_data.py: the first pass of data collection & preprocessing
2. scoring_condo.ipynb and scoring_hdb.ipynb: calculating quantitative scores for properties (number of amenities in
   vicinity of each property)
3. add_quality_data.py: calculating quality scores (median rating on Google Places, adjusted for relative number of
   reviews) for some amenity types in the vicinity of each property
4. create_database.py: creating database containing the csv files created in the previous step
5. update_database.ipynb: updating the database to adjust the score-specific thresholding for the quantity and quality
   scores, based on the individual distributions of these scores.

Read the code in the individual files for more information. Detailed comments & explanatory notes are available.