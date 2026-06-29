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
    ### This page contains the data and rankings for ACBJ's wealth edition. Data are from the American Community Survey 2024 5-year estimates and weighted to reflect a total wealth ranking per ZIP code.

    American City Business Journals’ &nbsp;Wealthiest ZIP Codes ranking uses publicly available data and a proprietary weighting to determine where wealth is most densely concentrated in America. The calculations factor population density, earnings, home ownership and poverty rates, among other measures.

    Each ZIP code’s ranking considers per capita income, household income, population, land area, homeownership rates and poverty rates. ZIP codes missing any one of these data points are not included. ACBJ also applied a number of assumptions to factor home equity and estimated savings on a per capita basis.

    The unfiltered, baseline dataset includes all U.S. ZIP codes. To account for local nuances in demographics and population, newsrooms can adjust data thresholds to offset some of the weighting applied to ACBJ’s ranking criteria. For example, ACBJ’s Wealthy 1000 — a national ranking of the wealthiest ZIP codes in America — thresholds were applied to filter the data to only include ZIP codes with at least 0.5 square miles in measure, a minimum per capita income of $80,000 and a maximum poverty rate of 10%. Since ACBJ’s ranking are weighted to determine concentrations of wealth, newsrooms with densely populated urban neighborhoods might want to consider adjusting local thresholds to reflect a lower poverty rate or higher minimum income levels. In areas where wealth is concentrated in more rural or suburban surroundings, setting thresholds with larger square mileage measures or higher median home values.

    **Instructions**

    To adjust filters for a local wealthiest ZIP code ranking, newsrooms can start by filtering by state and then by metro area and/or counties. Multiple selections are possible in each category.

    Geographic definitions used in this dataset come from the Census Bureau or USPS and may not match local ACBJ coverage areas exactly.

    Once you've filtered by geography, review the table results to verify your data. In most cases, you'll be ready to click the download button without any additional filtering. Otherwise, refresh the page and adjust your demographic filters accordingly, or reach out to Ethan Nelson or your senior researcher to schedule time to sift and sort the data to local preferences.

    You can find a [reader-friendly methodology you can use in stories here](https://www.bizjournals.com/bizjournals/news/2025/12/26/wealthiest-zips-methodology-2026.html).
    <div style="display: flex; gap: 5px">
        <img src = "https://media.bizj.us/view/img/12800587/mspbj-ethan-nelson.webp" style="width:80px;height:80px;">
        <span style="float: right; padding: 10px; background-color: #fff; padding-top: 6%; font-size: large"> Questions? Reach out to <a href="mailto:enelson@bizjournals.com?&subject=Wealth%20Edition%20Question"> Ethan Nelson</a> or your senior researcher.</span>
    </div>

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
                    "ALAND20",
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
            "median_home_value": "Median home value",
            "median_household_income": "Median household income",
            "poverty_rate": "Poverty rate",
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
        ascending=False, method="min"
    )
    df = df.drop(columns="concentrated_wealth_per_sq_mile_rpp_adjusted")
    return (df,)


@app.cell
def _(mo):
    min_income = mo.ui.number(label="Minimum median household income", start=0)
    min_area = mo.ui.number(label="Minimum ZIP code sq. mi", start=0)
    min_pop = mo.ui.number(label="Minimum population", start=0)
    min_pop_per_sqmi = mo.ui.number(label="Minimum population per sq. mi.", start=0)
    return min_area, min_income, min_pop, min_pop_per_sqmi


@app.cell
def _(mo):
    poverty_pcts = [
        0,
        0.05,
        0.1,
        0.15,
        0.2,
        0.25,
        0.3,
        0.35,
        0.4,
        0.45,
        0.5,
        0.55,
        0.6,
        0.65,
        0.7,
        0.75,
        0.8,
        0.85,
        0.9,
        0.95,
        1,
    ]
    poverty_options = [(f"{v:.0%}", float(v)) for v in poverty_pcts]

    firsts = [item[0] for item in poverty_options]
    max_poverty = mo.ui.dropdown(
        label="Max poverty rate", options=firsts, value=firsts[2]
    )
    return (max_poverty,)


@app.cell
def _(max_poverty):
    print(max_poverty.value)
    return


@app.cell
def _(df, max_poverty, min_area, min_income, min_pop, min_pop_per_sqmi):
    def base_filtered(df):

        d = df.copy()
        d = d[
            d["Median household income"].notna()
            & (d["Median household income"] >= min_income.value)
        ]
        d = d[d["Sq. mi."].notna() & (d["Sq. mi."] >= min_area.value)]
        d = d[d["Total population"].notna() & (d["Total population"] >= min_pop.value)]
        d = d[
            d["Poverty rate"].notna()
            & (d["Poverty rate"] <= float(max_poverty.value.rstrip("%")) / 100)
        ]
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

        d = d.assign(**{"Rank_within_selection": lambda d: d._rank.rank(method="min")})
        d.insert(
            loc=0, column="Rank within selection", value=d["Rank_within_selection"]
        )
        d.insert(loc=1, column="National rank", value=d["_rank"])

        d = d.drop(columns="_rank")
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

    filtered = filter_df()

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
            "Population per sq. mi.": "{:,.0f}".format,
            "Per capita income": "${:,.0f}".format,
            "Median household income": "${:,.0f}".format,
            "Median home value": "${:,.0f}".format,
            "Poverty rate": "{:.2%}".format,
            "Homeownership rate": "{:.2%}".format,
            "Sq. mi.": "{:,.2f}".format,
        },
        freeze_columns_left=["Zip code"],
        page_size=20,
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

    ACBJ’s Wealthy 1000 is a ranking of the wealthiest ZIP codes utilizing the data and methodology outlined above. The Wealthy 1000 applies three thresholds — a minimum square mile measure of 0.5 square miles per ZIP, a minimum per capita income of $80,000, and a maximum poverty rate of 10% — to determine its national rankings. To account for variances in cost of living per ZIP code, we adjusted each ZIP code's ranking based on its metro area [Regional Price Parity](https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area) as of the end of 2024.
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
def _(mo, unfiltered_df):
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
            "median_home_value": "Median home value",
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

    table_ui_1000 = mo.ui.table(
        wealthy_1000.reset_index(drop=True),
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
        freeze_columns_left=["ZIP"],
        page_size=20,
    )
    table_ui_1000
    return


if __name__ == "__main__":
    app.run()
