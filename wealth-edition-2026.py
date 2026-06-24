import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    from io import BytesIO

    return BytesIO, mo, np, pd


@app.cell
def _(mo):
    mo.md(r"""
    <h1>
        ACBJ's Wealth Edition
    </h1>
    ### This page contains the data and scores for ACBJ's wealth edition. Data is from the American Community Survey 2024 5-year estimates.

    Each ZIP code has been ranked based on a formula that considers per capita income, population, land area, homeownership rate, and poverty rate to determine how much wealth an area has. ZIP codes that are missing any one of these data points are not included. In addition, ACBJ's research division has made a number of assumptions to estimate total wealth in a ZIP code.

    The unfiltered, baseline dataset includes all ZIP codes. Depending on your market's economic situation, you may want to adjust the minimum per capita income, population, land area, or maximum poverty rate. The Wealthy 1000, which is a national look of the country's wealthiest ZIP codes according to our formula, is at the bottom of this page.

    **Instructions**

    Start by selecting the states you want, then narrow to your metro area and/or counties. The geographic defintions used in this dataset come from the Census Bureau or USPS, so they may not match your coverage area exactly. Be aware the filter logic goes from largest to smallest, so if you select a city first, you may produce unexpected results.

    Once you've selected your relevant areas, take a look at the table it produces. In most cases, you'll be ready to click the download button without any additional filtering. In some markets, particularly in those with large or small ZIP codes, or with ones with great income diversity, you may need to set a minimum for income, land area or population. Enter in minimums until the results look acceptable to you.

    <!-- <u>Baseline assumptions</u>: <br>
    Age savings start: **25**<br>
    Average lifetime savings rate: **10%** (0.1)<br>
    Average home equity rate: **50%** (0.5)<br>
    Poverty rate included? No (0) -->
    """)
    return


@app.cell
def _(pd):
    def load_data():
        return pd.read_csv(
            "https://raw.githubusercontent.com/ACBJ-CAR/wealth-edition-2026/refs/heads/main/data/marimo/wealthiest_zips.csv",
            dtype={"ZIP": "str"},
            usecols=lambda col: (
                col
                not in [
                    "concentrated_wealth_per_sq_mile",
                    "concentrated_wealth_per_sq_mile_difference",
                ]
            ),
        )

    df = load_data()
    df["ZIP"] = df["ZIP"].str.zfill(5)

    df.rename(
        columns={
            "ZIP": "Zip code",
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
            "usps_zip_pref_city": "City",
        },
        inplace=True,
    )

    df["State"] = df["State"].fillna("NA")
    df["Metro area"] = df["Metro area"].fillna("Not in metro area or metro not found")
    df["County"] = df["County"].fillna("County not found")
    df["_rank"] = df["concentrated_wealth_per_sq_mile_rpp_adjusted"].rank(
        ascending=False
    )
    df = df.drop(columns="concentrated_wealth_per_sq_mile_rpp_adjusted")
    return (df,)


@app.cell
def _(mo):
    min_income = mo.ui.number(label="Minimum median household income", start=0)
    min_area = mo.ui.number(label="Minimum ZIP code sq. mi", start=0)
    min_pop = mo.ui.number(label="Minimum population", start=0)
    min_pop_per_sqmi = mo.ui.number(label="Minimum population per sq. mi.", start=0)
    max_poverty = mo.ui.number(label="Maximum poverty rate", stop=100)
    return max_poverty, min_area, min_income, min_pop, min_pop_per_sqmi


@app.cell
def _(df, max_poverty, min_area, min_income, min_pop, min_pop_per_sqmi):
    def base_filtered(df):

        d = df.copy()
        d = d[
            d["Per capita income"].notna()
            & (d["Per capita income"] >= min_income.value)
        ]
        d = d[d["Sq. mi."].notna() & (d["Sq. mi."] >= min_area.value)]
        d = d[d["Total population"].notna() & (d["Total population"] >= min_pop.value)]
        d = d[d["Poverty rate"].notna() & (d["Poverty rate"] <= max_poverty.value)]
        d = d[
            d["Population per sq. mi."].notna()
            & (d["Population per sq. mi."] >= min_pop_per_sqmi.value)
        ]

        return d

    d0 = base_filtered(df)
    return (d0,)


@app.cell
def _(d0, mo, np):
    states = np.sort(d0["State"].dropna().unique())

    prev_state = (
        [s for s in locals().get("state", []).value if s in states]
        if "state" in locals()
        else []
    )

    state = mo.ui.multiselect(
        label="Select states:",
        options=states,
        value=prev_state,
    )
    return prev_state, state


@app.cell
def _(d0, mo, np, prev_state, state):
    d1 = d0[d0["State"].isin(state.value)] if state.value else d0

    metros = np.sort(d1["Metro area"].dropna().unique())

    prev_metro = (
        [s for s in locals().get("metro", []).value if s in metros]
        if "metro" in locals()
        else []
    )

    metro = mo.ui.multiselect(
        label="Select metros:",
        options=metros,
        value=prev_state,
    )
    return d1, metro


@app.cell
def _(d1, metro, mo, np):
    d2 = d1[d1["Metro area"].isin(metro.value)] if metro.value else d1

    counties = np.sort(d2["County"].dropna().unique())

    prev_county = (
        [s for s in locals().get("county", []).value if s in counties]
        if "county" in locals()
        else []
    )

    county = mo.ui.multiselect(
        label="Select counties:",
        options=counties,
        value=prev_county,
    )
    return county, d2


@app.cell
def _(county, d2, mo, np):
    d3 = d2[d2["County"].isin(county.value)] if county.value else d2

    cities = np.sort(d3["City"].astype(str).unique())

    prev_city = (
        [s for s in locals().get("city", []).value if s in cities]
        if "city" in locals()
        else []
    )

    city = mo.ui.multiselect(
        label="Select cities:",
        options=cities,
        value=prev_city,
    )
    return city, d3


@app.cell
def _(city, d3):
    def filter_df():
        d = d3.copy()

        d = d.assign(**{"Rank_within_selection": lambda d: range(1, len(d) + 1)})

        d.insert(
            loc=0, column="Rank within selection", value=d["Rank_within_selection"]
        )
        d.insert(loc=1, column="National rank", value=d["_rank"])

        d = d.drop(columns="_rank")
        d = d.drop(columns="rank")
        d = d.drop(columns="Rank_within_selection")

        if city.value:
            d = d[d["City"].isin(city.value)]
        else:
            return d

    return (filter_df,)


@app.cell
def _(max_poverty, min_area, min_income, min_pop, min_pop_per_sqmi, mo):
    mo.hstack([min_income, min_area, min_pop, min_pop_per_sqmi, max_poverty])
    return


@app.cell
def _(city, county, metro, mo, state):
    mo.hstack([state, metro, county, city])
    return


@app.cell
def _(BytesIO, filter_df, mo, pd):
    def make_excel_bytes(df):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        buffer.seek(0)
        return buffer

    filtered = filter_df()  # your function

    excel_bytes = make_excel_bytes(filtered)

    download_btn = mo.download(
        data=excel_bytes,
        filename="Wealthiest ZIPs.xlsx",
        label="Download your filtered data",
    )

    download_btn
    return (make_excel_bytes,)


@app.cell
def _(filter_df, mo):
    table_ui = mo.ui.table(
        filter_df().reset_index(drop=True),
        show_data_types=False,
        format_mapping={
            "Total population": "{:,}".format,
            "Population per sq. mi.": "{:,.2f}".format,
            "Per capita income": "${:,.2f}".format,
            "Median household income": "${:,.2f}".format,
            "Poverty rate": "{:.2%}".format,
            "Homeownership rate": "{:.2%}".format,
            "Sq. mi.": "{:,.2f}".format,
        },
        freeze_columns_left=["Zip code"],
    )

    table_ui
    return


@app.cell
def _():
    # Computing national average her
    # features = df.drop(columns=["Zip code"])
    return


@app.cell
def _(pd):
    unfiltered_df = pd.read_csv(
        "https://raw.githubusercontent.com/ACBJ-CAR/wealth-edition-2026/refs/heads/main/data/marimo/wealthiest_zips.csv",
        dtype={"ZIP_CODE_TABULATION_AREA": "str"},
    ).nlargest(1000, "concentrated_wealth_per_sq_mile_rpp_adjusted")
    return (unfiltered_df,)


@app.cell
def _(mo):
    mo.md(r"""
    # Wealthy 1000

    These are the nation's 1000 wealthiest ZIP code areas.
    """)
    return


@app.cell
def _(BytesIO, make_excel_bytes, mo, pd, unfiltered_df):
    def make_excel_bytes_1000(df):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        buffer.seek(0)
        return buffer

    excel_bytes_1000 = make_excel_bytes(unfiltered_df)

    download_btn_1000 = mo.download(
        data=excel_bytes_1000,
        filename="Wealthiest ZIPs.xlsx",
        label="Download the Wealthy 1000",
    )

    download_btn_1000
    return


@app.cell
def _(unfiltered_df):
    wealthy_1000 = unfiltered_df.drop(
        columns=[
            "concentrated_wealth_per_sq_mile_rpp_adjusted",
            "concentrated_wealth_per_sq_mile",
            "concentrated_wealth_per_sq_mile_difference",
        ]
    )

    wealthy_1000.rename(
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
            "usps_zip_pref_city": "City",
        },
        inplace=True,
    )

    wealthy_1000
    return


if __name__ == "__main__":
    app.run()
