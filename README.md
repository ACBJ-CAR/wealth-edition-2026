# wealth-edition-2026

Downloading and processing Census data for the 2026 wealth edition

*Reporter: Ethan Nelson*

*Editor: Cole Schnell*

## Project goal

*TK: Briefly describe this project*

## Methodology

*TK: Link to or state methodology here*

## Data sources

### TK Source 1

Source: *TK: source attribution (e.g. U.S. Census Bureau)*

Source URL: *TK: source URL*

*TK: any notes or links about the source go here*

### TK Source 2

Source: *TK: source attribution (e.g. U.S. Census Bureau)*

Source URL: *TK: source url*

*TK: any notes or links about the source go here*

## Project usage

**Cloning the GitHub repo**

1. Run `git clone git@github.com:ACBJ-CAR/wealth-edition-2026.git`
2. Run `uv sync` to create the virtual environment and install all dependencies from `pyproject.toml`.
3. Run `datakit data pull` to retrieve the data files.
4. Run `uv run pre-commit install` to add pre-commit hooks. This ensures consistent formatting and runs code checks before committing code.

**Making edits**


1. Run `uv run jupyter labs` or open notebook in VS Code
> Reminder: Git is not tracking or saving notebooks. Instead, using jupytext, notebooks are synced with a .py file. Any changes made in either file sync with the other paired file when you save. If you are using VS Code for editing your notebooks, you must have the "Jupytext Sync" VS code extension.



**Commiting changes to GitHub**

1. Run `git add . &&  git commit -m "describe message of changes here"`
2. Run `git push origin main`
3. Run `datakit data push`


## Data notes

* Add important caveats, limitations, and source contact info here.
