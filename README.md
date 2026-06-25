# wealth-edition-2026

Downloading and processing Census data for the 2026 wealth edition

*Reporter: Ethan Nelson*

*Editor: Cole Schnell*

## Project goal

American City Business Journals analyzed Census Bureau data to determine the nation's wealthiest 1,000 ZIP code areas, and to rank each area by its concentrated wealth per square mile.

## Methodology

In this notebook, we download national ZCTA-level demographic data and geographies using Censusdis, then apply our formula to each area.

ACBJ developed a formula that considers a number of demographic and economic data points: per capita income, median home value, population per square mile and median age. We take these metrics and adjust for the land area of each ZIP code to determine the area's wealth per square mile. We then adjust each ZIP code's wealth score to account for regional differences in affordability. More expensive areas receive a lower score in this step.

The full formula is available in the ghost article called "Wealthiest ZIPs methodology, 2026 (internal use only)"

## Data sources

### Census Bureau

Source: *Census Bureau's American Community Survey 2024 five-year estimates*

### Bureau of Economic Analysis

Source: [*BEA's Regional Price Parities*](https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area)

## Project usage

**Cloning the GitHub repo**

1. Run `git clone git@github.com:ACBJ-CAR/wealth-edition-2026.git`
2. Run `uv sync` to create the virtual environment and install all dependencies from `pyproject.toml`.
3. Run `datakit data pull` to retrieve the data files.
4. Run `uv run pre-commit install` to add pre-commit hooks. This ensures consistent formatting and runs code checks before committing code.

**Making edits**


1. Run `uv run jupyter labs` or open notebook in VS Code
> Reminder: Git is not tracking or saving notebooks. Instead, using jupytext, notebooks are synced with a .py file. Any changes made in either file sync with the other paired file when you save. If you are using VS Code for editing your notebooks, you must have the "Jupytext Sync" VS code extension.
2. To open the Marimo notebook, run `marimo edit wealth-edition-2026.py` in the project's root directory.


**Commiting changes to GitHub**

1. Run `git add . &&  git commit -m "describe message of changes here"`
2. Run `git push origin main`
3. Run `datakit data push`


## Data notes

- We use the term "ZIP code" here as a shorthand for ZIP Code Tabulation Area. ZIP codes are used to coordinate USPS mail delivery routes and can be subsets of each other or be composed only of PO boxes. ZCTAs are the Census Bureau's geographic representations of ZIP codes.

- We only include ZIP codes that have a land area of more than 0.5 square miles. Only ZIP codes that had all data points considered by the formula were ranked. Roughly 2,000 ZIP codes across the country's about 33,000 ZIP codes were excluded.
