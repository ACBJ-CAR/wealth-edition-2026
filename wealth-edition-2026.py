import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np

    return mo, np, pd


@app.cell
def _(mo):
    mo.md(r"""
    #ACBJ's Wealth Edition
    ### This page contains the data and scores for ACBJ's wealth edition. Data is from the American Community Survey 2024 5-year estimates.

    Each ZIP code has been ranked based on a formula that considers per capita income, population, land area, homeownership rate, and poverty rate to determine how much wealth an area has. ZIP codes that are missing any one of these data points are not included. In addition, ACBJ's research division has made a number of assumptions to estimate total wealth in a ZIP code.

    <u>Baseline assumptions</u>: <br>
    Age savings start: **25**<br>
    Average lifetime savings rate: **10%** (0.1)<br>
    Average home equity rate: **50%** (0.5)<br>
    Poverty rate included? No (0)

    Use the filters to select conditions for your market.
    """)
    return


@app.cell
def _(pd):
    def load_data():
        return pd.read_csv(
            "https://raw.githubusercontent.com/ACBJ-CAR/wealth-edition-2026/refs/heads/main/data/marimo/wealthiest_zips.csv",
            dtype={"ZIP_CODE_TABULATION_AREA": "str"},
            usecols=lambda col: col not in ["concentrated_wealth_per_sq_mile"],
        )

    df = load_data()
    df["ZIP_CODE_TABULATION_AREA"] = df["ZIP_CODE_TABULATION_AREA"].str.zfill(5)
    df["poverty_rate"] = df["poverty_rate"] * 100

    df.rename(
        columns={
            "ZIP_CODE_TABULATION_AREA": "Zip code",
            "CBSA_NAME": "Metro area",
            "COUNTYNAME": "County",
            "STATE": "State",
            "total_population": "Total population",
            "population_per_sq_mile": "Population per sq. mi.",
            "income_per_capita": "Per capita income",
            "median_household_income": "Median household income",
            "poverty_rate": "Poverty rate",
            "ALAND20": "Land area (sq. meters)",
            "median_age": "Median age",
            "square_miles": "Sq. mi.",
            "home_ownership_rate": "Homeownership rate",
        },
        inplace=True,
    )

    df["State"] = df["State"].fillna("NA")
    df["Metro area"] = df["Metro area"].fillna("Not in metro area or metro not found")
    df["County"] = df["County"].fillna("County not found")
    return (df,)


@app.cell
def _(counties, metros, mo, states):
    min_income = mo.ui.number(label="Minimum median household income", start=0)
    min_area = mo.ui.number(label="Minimum ZIP code sq. mi", start=0)
    min_pop = mo.ui.number(label="Minimum population", start=0)
    max_poverty = mo.ui.number(label="Maximum poverty rate", start=100)

    state = mo.ui.multiselect(label="Select states: ", options=states, value=[])
    metro = mo.ui.multiselect(label="Select metros: ", options=metros, value=[])
    county = mo.ui.multiselect(label="Select counties: ", options=counties, value=[])
    city = mo.ui.multiselect(label="Select cities: ", options="TKTK")
    return (
        city,
        county,
        max_poverty,
        metro,
        min_area,
        min_income,
        min_pop,
        state,
    )


@app.cell
def _(county, df, max_poverty, metro, min_area, min_income, min_pop, state):
    def filter_df():
        d = df.copy()
        d = d[
            d["Per capita income"].notna()
            & (d["Per capita income"] >= min_income.value)
        ]
        d = d[d["Sq. mi."].notna() & (d["Sq. mi."] >= min_area.value)]
        d = d[d["Total population"].notna() & (d["Total population"] >= min_pop.value)]
        d = d[d["Poverty rate"].notna() & (d["Poverty rate"] <= max_poverty.value)]

        if state.value:
            d = d[d["State"].isin(state.value)]
        if metro.value:
            d = d[d["Metro area"].isin(metro.value)]
        if county.value:
            d = d[d["County"].isin(county.value)]
        return d

    return (filter_df,)


@app.cell
def _(max_poverty, min_area, min_income, min_pop, mo):
    mo.hstack([min_income, min_area, min_pop, max_poverty])
    return


@app.cell
def _(city, county, metro, mo, state):
    mo.hstack([state, county, metro, city])
    return


@app.cell
def _(filter_df, mo):
    table_ui = mo.ui.table(
        filter_df(),
        show_data_types=False,
        format_mapping={
            "Poverty rate": "{:.2}%".format,
            "Total population": "{:,}".format,
            "Population per sq. mi.": "{:,.2f}".format,
            "Per capita income": "${:,.2f}".format,
            "Median household income": "${:,.2f}".format,
            "Homeownership rate": "{:.2%}".format,
        },
        freeze_columns_left=["rank", "Zip code"],
    )

    table_ui
    return


@app.cell
def _(df, np):
    states = np.sort(df["State"].unique())
    counties = np.sort(df["County"].unique())
    metros = np.sort(df["Metro area"].unique())
    return counties, metros, states


@app.cell
def _():
    # Computing national average her
    # features = df.drop(columns=["Zip code"])
    return


if __name__ == "__main__":
    app.run()
