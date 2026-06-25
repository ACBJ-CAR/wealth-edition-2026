# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: wealth-edition-2026 (3.12.13)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Loading

# %%
import pandas as pd
import censusdis.data as ced
from censusdis import states
import geopandas as gpd
import os
import httpx
from pathlib import Path
import numpy as np

httpx.Client(verify=False)

# %%
CERT_PATH = os.environ["CERT_PATH"]
LOCAL_DATA_FOLDER = Path("./data")

# Load in crosswalks and merge together. I think it would behoove us at some point to have one master crosswalk that starts at Census blocks and then rolls up to states.
zip_codes = (
    pd.read_csv(LOCAL_DATA_FOLDER / "manual" / "zip_county_crosswalk.csv", dtype=str)
    .sort_values(by=["zip", "tot_ratio"], ascending=[True, False])
    .drop_duplicates(subset=["zip"], keep="first")
)
zip_codes["zip"] = zip_codes["zip"].str.zfill(5)
zip_codes["county"] = zip_codes["county"].str.zfill(5)

county_codes = pd.read_csv(LOCAL_DATA_FOLDER / "manual" / "county_codes.csv", dtype=str)
county_codes["COUNTY_CODE"] = county_codes["COUNTY_CODE"].str.zfill(5)

metros = (
    pd.read_csv(LOCAL_DATA_FOLDER / "manual" / "zip_metro_crosswalk.csv", dtype=str)
    .sort_values(by=["ZIP", "TOT_RATIO"], ascending=[True, False])
    .drop_duplicates(subset=["ZIP"], keep="first")
)
metros["ZIP"] = metros["ZIP"].str.zfill(5)

zip_county_metro_crosswalk = zip_codes.merge(
    county_codes, left_on="county", right_on="COUNTY_CODE", how="left"
).merge(metros, left_on="zip", right_on="ZIP", how="left")
zip_county_metro_crosswalk = zip_county_metro_crosswalk[
    ["zip", "usps_zip_pref_city", "CBSA", "CBSA_NAME", "COUNTYNAME", "STATE"]
].drop_duplicates()

# Load in the Regional Price Parity data
rpp = pd.read_csv(
    LOCAL_DATA_FOLDER / "manual" / "rpp.csv",
    dtype={"GeoFIPS": str, "GeoName": str, "rpp": float},
)

zip_county_metro_crosswalk_rpp = zip_county_metro_crosswalk.merge(
    rpp, left_on="CBSA", right_on="GeoFIPS", how="left"
)

# %%
CENSUS_API_KEY = ""  # Enter your API key here
DATASET = "acs/acs5"
YEAR = 2024
PRIOR_YEAR = 2014  # This is what I used for the TX Wealth Wave, but it's not used for the Wealthiest ZIPs list

# %%
# Census variable codes for the variables we want to pull from the Census API. These are based on the 2024 ACS 5-year estimates.
TOTAL_POPULATION_VARIABLE = "B01003_001E"
MEDIAN_HOUSEHOLD_INCOME_VARIABLE = "B19013_001E"
INCOME_PER_CAPITA_VARIABLE = "B19301_001E"
MEDIAN_AGE_VARIABLE = "B01002_001E"
HOUSING_UNITS_VARIABLE = "B25002_001E"
MEDIAN_HOME_VALUE_VARIABLE = "B25077_001E"
OWNER_OCCUPIED_VARIABLE = "B25003_002E"
EDUCATION_BACHELORS_VARIABLE = "B15003_022E"
EDUCATION_MASTERS_VARIABLE = "B15003_023E"
EDUCATION_PROFESSIONAL_VARIABLE = "B15003_024E"
EDUCATION_PHD_VARIABLE = "B15003_025E"
PCT_WHITE_VARIABLE = "B02001_002E"
PCT_BLACK_VARIABLE = "B02001_003E"
PCT_AMERIND_ALASKAN_VARIABLE = "B02001_004E"
PCT_ASIAN_VARIABLE = "B02001_005E"
PCT_NHPI_VARIABLE = "B02001_006E"
PCT_OTHER_VARIABLE = "B02001_007E"
PCT_TWO_PLUS_VARIABLE = "B02001_008E"
PCT_HISPANIC_VARIABLE = "B03001_003E"
POVERTY_STATUS_VARIABLE = "B17021_001E"
BELOW_POVERTY_LINE_VARIABLE = "B17001_002E"

VARIABLES = [
    "NAME",
    TOTAL_POPULATION_VARIABLE,
    MEDIAN_HOUSEHOLD_INCOME_VARIABLE,
    INCOME_PER_CAPITA_VARIABLE,
    MEDIAN_AGE_VARIABLE,
    HOUSING_UNITS_VARIABLE,
    MEDIAN_HOME_VALUE_VARIABLE,
    OWNER_OCCUPIED_VARIABLE,
    EDUCATION_BACHELORS_VARIABLE,
    EDUCATION_MASTERS_VARIABLE,
    EDUCATION_PROFESSIONAL_VARIABLE,
    EDUCATION_PHD_VARIABLE,
    PCT_WHITE_VARIABLE,
    PCT_BLACK_VARIABLE,
    PCT_AMERIND_ALASKAN_VARIABLE,
    PCT_ASIAN_VARIABLE,
    PCT_NHPI_VARIABLE,
    PCT_OTHER_VARIABLE,
    PCT_TWO_PLUS_VARIABLE,
    PCT_HISPANIC_VARIABLE,
    POVERTY_STATUS_VARIABLE,
    BELOW_POVERTY_LINE_VARIABLE,
]

# ACBJ assumptions
SAVINGS_RATE = 0.10
AGE_OF_INCOME_START = 25
PERCENT_HOME_EQUITY = 0.50

# %%
# Load ZIP-level data
# Roughly 10 seconds
with ced.certificates.use(data_verify=CERT_PATH):
    df_zips = ced.download(
        DATASET,
        YEAR,
        VARIABLES,
        zip_code_tabulation_area="*",
        with_geometry_columns=True,
        api_key=CENSUS_API_KEY,
    )

# %%
# Renaming columns to more user-friendly names.
df_zips = df_zips.rename(
    columns={
        "B01003_001E": "total_population",
        "B19013_001E": "median_household_income",
        "B19301_001E": "income_per_capita",
        "B01002_001E": "median_age",
        "B25002_001E": "housing_units",
        "B25077_001E": "median_home_value",
        "B25003_002E": "owner_occupied",
        "B15003_022E": "education_bachelors",
        "B15003_023E": "education_masters",
        "B15003_024E": "education_professional",
        "B15003_025E": "education_phd",
        "B02001_002E": "pct_white",
        "B02001_003E": "pct_black",
        "B02001_004E": "pct_amerind_alaskan",
        "B02001_005E": "pct_asian",
        "B02001_006E": "pct_nhpi",
        "B02001_007E": "pct_other",
        "B02001_008E": "pct_two_plus",
        "B03001_003E": "pct_hispanic",
        "B17021_001E": "poverty_status_known",
        "B17001_002E": "below_poverty_line",
    }
)

# %%
# Pulls down ZIP code geometries. This is necessary to get the land area for each ZIP code, which we need to calculate population per square mile.
# Roughly 40 seconds. Is there a faster way to do this?
zcta_geo = gpd.read_file(
    "https://www2.census.gov/geo/tiger/TIGER2024/ZCTA520/tl_2024_us_zcta520.zip"
)
zcta_geo = zcta_geo.rename(columns={"ZCTA5CE20": "ZIP_CODE_TABULATION_AREA"})


# %%
# Merge zip code demographic data with the geographies
df_zips_with_geometry = df_zips.merge(
    zcta_geo, on="ZIP_CODE_TABULATION_AREA", how="left"
)

# %%
# Merge with crosswalk
df_zips_with_county_metro_state_rpp = df_zips_with_geometry.merge(
    zip_county_metro_crosswalk_rpp,
    left_on="ZIP_CODE_TABULATION_AREA",
    right_on="zip",
    how="left",
)

# %%
# These are the calculations we need to get the wealth score. At the end, we rank ZIP codes by concentrated wealth per square mile.
df_zips_with_county_metro_state_rpp["population_per_sq_mile"] = (
    df_zips_with_county_metro_state_rpp["total_population"]
    / df_zips_with_county_metro_state_rpp["ALAND20"].replace(0, pd.NA)
    * 2.58999e6
)
df_zips_with_county_metro_state_rpp["square_miles"] = (
    df_zips_with_county_metro_state_rpp["ALAND20"] / 2.58999e6
)

df_zips_with_county_metro_state_rpp["poverty_rate"] = (
    df_zips_with_county_metro_state_rpp["below_poverty_line"]
    / df_zips_with_county_metro_state_rpp["poverty_status_known"].replace(0, pd.NA)
)

df_zips_with_county_metro_state_rpp["home_ownership_rate"] = (
    df_zips_with_county_metro_state_rpp["owner_occupied"]
    / df_zips_with_county_metro_state_rpp["housing_units"].replace(0, pd.NA)
)

df_zips_with_county_metro_state_rpp["assumed_saved_sum"] = (
    df_zips_with_county_metro_state_rpp["income_per_capita"]
    * (df_zips_with_county_metro_state_rpp["median_age"] - AGE_OF_INCOME_START)
    * SAVINGS_RATE
)

df_zips_with_county_metro_state_rpp["assumed_home_equity"] = (
    df_zips_with_county_metro_state_rpp["home_ownership_rate"]
    * df_zips_with_county_metro_state_rpp["median_home_value"]
) * PERCENT_HOME_EQUITY

cols = ["population_per_sq_mile", "assumed_saved_sum", "assumed_home_equity"]

df_zips_with_county_metro_state_rpp[cols] = df_zips_with_county_metro_state_rpp[
    cols
].apply(pd.to_numeric, errors="coerce")

df_zips_with_county_metro_state_rpp["concentrated_wealth_per_sq_mile"] = (
    df_zips_with_county_metro_state_rpp["population_per_sq_mile"]
    * df_zips_with_county_metro_state_rpp["assumed_saved_sum"]
) + (
    df_zips_with_county_metro_state_rpp["population_per_sq_mile"]
    * df_zips_with_county_metro_state_rpp["assumed_home_equity"]
)

df_zips_with_county_metro_state_rpp["concentrated_wealth_per_sq_mile_rpp_adjusted"] = (
    np.where(
        df_zips_with_county_metro_state_rpp["rpp"].isna(),
        df_zips_with_county_metro_state_rpp["concentrated_wealth_per_sq_mile"],
        (
            df_zips_with_county_metro_state_rpp[
                "concentrated_wealth_per_sq_mile"
            ].apply(pd.to_numeric, errors="coerce")
            / df_zips_with_county_metro_state_rpp["rpp"]
        )
        * 100,
    )
)

df_zips_with_county_metro_state_rpp["concentrated_wealth_per_sq_mile_difference"] = (
    df_zips_with_county_metro_state_rpp["concentrated_wealth_per_sq_mile_rpp_adjusted"]
    - df_zips_with_county_metro_state_rpp["concentrated_wealth_per_sq_mile"]
)

df_zips_with_county_metro_state_rpp = df_zips_with_county_metro_state_rpp.sort_values(
    "concentrated_wealth_per_sq_mile_rpp_adjusted", ascending=False
)

# %%
# Get only the columns we care about and sort again just for good measure
wealthiest_zips = df_zips_with_county_metro_state_rpp[
    [
        "ZIP_CODE_TABULATION_AREA",
        "usps_zip_pref_city",
        "CBSA_NAME",
        "COUNTYNAME",
        "STATE",
        "concentrated_wealth_per_sq_mile_rpp_adjusted",
        "concentrated_wealth_per_sq_mile",
        "concentrated_wealth_per_sq_mile_difference",
        "total_population",
        "population_per_sq_mile",
        "income_per_capita",
        "median_household_income",
        "median_home_value",
        "poverty_rate",
        "ALAND20",
        "median_age",
        "square_miles",
        "home_ownership_rate",
    ]
].sort_values("concentrated_wealth_per_sq_mile_rpp_adjusted", ascending=False)
wealthiest_zips = wealthiest_zips[wealthiest_zips["square_miles"] > 0.5]
wealthiest_zips["County, state"] = (
    wealthiest_zips["COUNTYNAME"] + ", " + wealthiest_zips["STATE"]
)
wealthiest_zips["usps_zip_pref_city"] = wealthiest_zips[
    "usps_zip_pref_city"
].str.title()

# Commenting this out because we'll rank in the Marimo notebook so we can recalculate it with filters
# wealthiest_zips["Rank"] = wealthiest_zips["concentrated_wealth_per_sq_mile_rpp_adjusted"].rank(ascending=False)

# %%
# This is what I'll use for the Marimo dashboard, but I won't save it to the repo since it can be easily generated from the code above.
wealthiest_zips_formatted = wealthiest_zips.rename(
    columns={
        "rank": "Rank",
        "ZIP_CODE_TABULATION_AREA": "ZIP",
        "usps_zip_pref_city": "City",
        "CBSA_NAME": "Metro area",
        "COUNTYNAME": "County",
        "STATE": "State",
    }
)

# wealthiest_zips_formatted.to_csv(LOCAL_DATA_FOLDER / "marimo" / "wealthiest_zips.csv", index=False)

# %%
with ced.certificates.use(data_verify=CERT_PATH):
    df_states = ced.download(
        DATASET,
        YEAR,
        ["B01003_001E", "NAME"],
        state="*",
        api_key=CENSUS_API_KEY,
    )

df_states = df_states.rename(
    columns={"B01003_001E": "total_population_statewide", "NAME": "state_name"}
)
df_states["Abbreviation"] = df_states["STATE"].map(states.ABBREVIATIONS_FROM_IDS)

# %%
# This is to make sure each state has at least a few dozen ZIPs, and this also helps us see how many people we're excluding in our wealthiest ZIPs.
# ZIPs that don't have all data points won't be included in our wealthiest dataframe, so I'm not super worried with differences in the the thousands of people
state_groups = wealthiest_zips.groupby("STATE").agg(
    {
        "concentrated_wealth_per_sq_mile": "mean",
        "total_population": "sum",
        "ZIP_CODE_TABULATION_AREA": "count",
    }
)
state_comparison = state_groups.merge(
    df_states, left_on="STATE", right_on="Abbreviation", how="outer"
)[
    [
        "STATE",
        "state_name",
        "Abbreviation",
        "concentrated_wealth_per_sq_mile",
        "total_population",
        "total_population_statewide",
        "ZIP_CODE_TABULATION_AREA",
    ]
].sort_values("state_name", ascending=True)
state_comparison["population_difference"] = (
    state_comparison["total_population"]
    - state_comparison["total_population_statewide"]
)
state_comparison

# %% [markdown]
# ## Stuff below here was used to generate the 2014 data for the Texas Wealth Wave project

# %%
# 2014 variables
TOTAL_POPULATION_VARIABLE_2014 = "B01003_001E"
MEDIAN_HOUSEHOLD_INCOME_VARIABLE_2014 = "B19013_001E"
INCOME_PER_CAPITA_VARIABLE_2014 = "B19301_001E"
MEDIAN_AGE_VARIABLE_2014 = "B01002_001E"
HOUSING_UNITS_VARIABLE_2014 = "B25001_001E"
MEDIAN_HOME_VALUE_VARIABLE_2014 = "B25077_001E"
OWNER_OCCUPIED_VARIABLE_2014 = "B25003_002E"
EDUCATION_BACHELORS_VARIABLE_2014 = "B15003_022E"
EDUCATION_MASTERS_VARIABLE_2014 = "B15003_023E"
EDUCATION_PROFESSIONAL_VARIABLE_2014 = "B15003_024E"
EDUCATION_PHD_VARIABLE_2014 = "B15003_025E"
PCT_WHITE_VARIABLE_2014 = "B02001_002E"
PCT_BLACK_VARIABLE_2014 = "B02001_003E"
PCT_AMERIND_ALASKAN_VARIABLE_2014 = "B02001_004E"
PCT_ASIAN_VARIABLE_2014 = "B02001_005E"
PCT_NHPI_VARIABLE_2014 = "B02001_006E"
PCT_OTHER_VARIABLE_2014 = "B02001_007E"
PCT_TWO_PLUS_VARIABLE_2014 = "B02001_008E"
PCT_HISPANIC_VARIABLE_2014 = "B03001_003E"
POVERTY_STATUS_VARIABLE_2014 = "B17021_001E"
BELOW_POVERTY_LINE_VARIABLE_2014 = "B17001_002E"

VARIABLES_2014 = [
    "NAME",
    TOTAL_POPULATION_VARIABLE_2014,
    MEDIAN_HOUSEHOLD_INCOME_VARIABLE_2014,
    INCOME_PER_CAPITA_VARIABLE_2014,
    MEDIAN_AGE_VARIABLE_2014,
    HOUSING_UNITS_VARIABLE_2014,
    MEDIAN_HOME_VALUE_VARIABLE_2014,
    OWNER_OCCUPIED_VARIABLE_2014,
    EDUCATION_BACHELORS_VARIABLE_2014,
    EDUCATION_MASTERS_VARIABLE_2014,
    EDUCATION_PROFESSIONAL_VARIABLE_2014,
    EDUCATION_PHD_VARIABLE_2014,
    PCT_WHITE_VARIABLE_2014,
    PCT_BLACK_VARIABLE_2014,
    PCT_AMERIND_ALASKAN_VARIABLE_2014,
    PCT_ASIAN_VARIABLE_2014,
    PCT_NHPI_VARIABLE_2014,
    PCT_OTHER_VARIABLE_2014,
    PCT_TWO_PLUS_VARIABLE_2014,
    PCT_HISPANIC_VARIABLE_2014,
    POVERTY_STATUS_VARIABLE_2014,
    BELOW_POVERTY_LINE_VARIABLE_2014,
]

# %%
# 2014 data
with ced.certificates.use(data_verify=CERT_PATH):
    df_zips_2014 = ced.download(
        DATASET,
        PRIOR_YEAR,
        VARIABLES_2014,
        state="*",
        zip_code_tabulation_area="*",
        with_geometry_columns=True,
        api_key=CENSUS_API_KEY,
    )


# %%
# 2014 geographies
zcta_geo_2014 = gpd.read_file(
    "https://www2.census.gov/geo/tiger/TIGER2014/ZCTA5/tl_2014_us_zcta510.zip"
)
zcta_geo_2014 = zcta_geo_2014.rename(columns={"ZCTA5CE10": "ZIP_CODE_TABULATION_AREA"})

# %%
zip_codes_2014 = (
    pd.read_csv(
        LOCAL_DATA_FOLDER / "manual" / "zip_county_crosswalk_2014.csv", dtype=str
    )
    .sort_values(by=["ZIP", "TOT_RATIO"], ascending=[True, False])
    .drop_duplicates(subset=["ZIP"], keep="first")
)
zip_codes_2014["ZIP"] = zip_codes_2014["ZIP"].str.zfill(5)
zip_codes_2014["COUNTY"] = zip_codes_2014["COUNTY"].str.zfill(5)

metros_2014 = (
    pd.read_csv(
        LOCAL_DATA_FOLDER / "manual" / "zip_metro_crosswalk_2014.csv", dtype=str
    )
    .sort_values(by=["ZIP", "TOT_RATIO"], ascending=[True, False])
    .drop_duplicates(subset=["ZIP"], keep="first")
)
metros_2014["ZIP"] = metros_2014["ZIP"].str.zfill(5)

zip_county_metro_crosswalk_2014 = zip_codes_2014.merge(
    county_codes, left_on="COUNTY", right_on="COUNTY_CODE", how="left"
).merge(metros_2014, left_on="ZIP", right_on="ZIP", how="left")
zip_county_metro_crosswalk_2014 = zip_county_metro_crosswalk_2014[
    ["ZIP", "CBSA_NAME", "COUNTYNAME", "STATE"]
].drop_duplicates()

# %%
df_zips_2014 = df_zips_2014.rename(
    columns={
        "B01003_001E": "total_population",
        "B19013_001E": "median_household_income",
        "B19301_001E": "income_per_capita",
        "B01002_001E": "median_age",
        "B25001_001E": "housing_units",
        "B25077_001E": "median_home_value",
        "B25003_002E": "owner_occupied",
        "B15003_022E": "EDUCATION_BACHELORS_VARIABLE_2014",
        "B15003_023E": "EDUCATION_MASTERS_VARIABLE_2014",
        "B15003_024E": "EDUCATION_PROFESSIONAL_VARIABLE_2014",
        "B15003_025E": "EDUCATION_PHD_VARIABLE_2014",
        "B02001_002E": "PCT_WHITE_VARIABLE_2014",
        "B02001_003E": "PCT_BLACK_VARIABLE_2014",
        "B02001_004E": "PCT_AMERIND_ALASKAN_VARIABLE_2014",
        "B02001_005E": "PCT_ASIAN_VARIABLE_2014",
        "B02001_006E": "PCT_NHPI_VARIABLE_2014",
        "B02001_007E": "PCT_OTHER_VARIABLE_2014",
        "B02001_008E": "PCT_TWO_PLUS_VARIABLE_2014",
        "B03001_003E": "PCT_HISPANIC_VARIABLE_2014",
        "B17021_001E": "poverty_status_known",
        "B17001_002E": "below_poverty_line",
    }
)

# %%
df_zips_with_geometry_2014 = df_zips_2014.merge(
    zcta_geo_2014, on="ZIP_CODE_TABULATION_AREA", how="left"
)

# %%
# These are the calculations we need to get the wealth score. At the end, we rank ZIP codes by concentrated wealth per square mile.
df_zips_with_geometry_2014["population_per_sq_mile"] = (
    df_zips_with_geometry_2014["total_population"]
    / df_zips_with_geometry_2014["ALAND10"].replace(0, pd.NA)
    * 2.58999e6
)
df_zips_with_geometry_2014["square_miles"] = (
    df_zips_with_geometry_2014["ALAND10"] / 2.58999e6
)

df_zips_with_geometry_2014["poverty_rate"] = df_zips_with_geometry_2014[
    "below_poverty_line"
] / df_zips_with_geometry_2014["poverty_status_known"].replace(0, pd.NA)

df_zips_with_geometry_2014["home_ownership_rate"] = df_zips_with_geometry_2014[
    "owner_occupied"
] / df_zips_with_geometry_2014["housing_units"].replace(0, pd.NA)

df_zips_with_geometry_2014["assumed_saved_sum"] = (
    df_zips_with_geometry_2014["income_per_capita"]
    * (df_zips_with_geometry_2014["median_age"] - AGE_OF_INCOME_START)
    * SAVINGS_RATE
)
df_zips_with_geometry_2014["assumed_home_equity"] = (
    df_zips_with_geometry_2014["home_ownership_rate"]
    * df_zips_with_geometry_2014["median_home_value"]
) * PERCENT_HOME_EQUITY

df_zips_with_geometry_2014["concentrated_wealth_per_sq_mile"] = (
    df_zips_with_geometry_2014["population_per_sq_mile"]
    * df_zips_with_geometry_2014["assumed_saved_sum"]
) + (
    df_zips_with_geometry_2014["population_per_sq_mile"]
    * df_zips_with_geometry_2014["assumed_home_equity"]
)
df_zips_with_geometry_2014 = df_zips_with_geometry_2014.sort_values(
    "concentrated_wealth_per_sq_mile", ascending=False
)
df_zips_with_geometry_2014["rank"] = df_zips_with_geometry_2014[
    "concentrated_wealth_per_sq_mile"
].rank(ascending=False)

# %%
df_zips_with_county_metro_state_2014 = df_zips_with_geometry_2014.merge(
    zip_county_metro_crosswalk_2014,
    left_on="ZIP_CODE_TABULATION_AREA",
    right_on="ZIP",
    how="left",
)

# %%
wealthiest_zips_2014 = df_zips_with_county_metro_state_2014[
    [
        "rank",
        "ZIP_CODE_TABULATION_AREA",
        "CBSA_NAME",
        "COUNTYNAME",
        "STATE_x",
        "concentrated_wealth_per_sq_mile",
        "total_population",
        "population_per_sq_mile",
        "income_per_capita",
        "median_household_income",
        "poverty_rate",
        "ALAND10",
        "median_age",
        "square_miles",
        "home_ownership_rate",
    ]
].sort_values("concentrated_wealth_per_sq_mile", ascending=False)

# wealthiest_zips_2014.to_csv("wealthiest_zips_2014.csv")
