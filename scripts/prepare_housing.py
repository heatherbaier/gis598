"""Build data/california_housing.csv in the same columns and units as scikit-learn's
fetch_california_housing, from the 1990 census block-group file used in many textbooks
(columns: longitude, latitude, housing_median_age, total_rooms, total_bedrooms, population,
households, median_income, median_house_value).

    python prepare_housing.py housing.csv ../data/california_housing.csv

The raw file has 207 block groups with no value for total_bedrooms. Those get their average
bedrooms per household estimated from their rooms, using the statewide bedrooms-to-rooms ratio.
Nothing else in the chapter uses that column, so this does not affect the results.
"""
import sys
import pandas as pd

raw = pd.read_csv(sys.argv[1])
ratio = (raw["total_bedrooms"] / raw["total_rooms"]).median()
bedrooms = raw["total_bedrooms"].fillna(raw["total_rooms"] * ratio)

out = pd.DataFrame({
    "MedInc": raw["median_income"],                               # tens of thousands of dollars
    "HouseAge": raw["housing_median_age"],                        # years
    "AveRooms": raw["total_rooms"] / raw["households"],
    "AveBedrms": bedrooms / raw["households"],
    "Population": raw["population"],
    "AveOccup": raw["population"] / raw["households"],
    "Latitude": raw["latitude"],
    "Longitude": raw["longitude"],
    "MedHouseVal": raw["median_house_value"] / 100000,            # hundreds of thousands of dollars
})
out.round(5).to_csv(sys.argv[2], index=False)
print(len(out), "rows;", int(raw["total_bedrooms"].isna().sum()), "bedroom values estimated")
