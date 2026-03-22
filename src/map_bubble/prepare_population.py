import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import pandas as pd
    import geopandas as gpd

    return gpd, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Prepare population dataset

    https://www.statistik.bayern.de/statistik/gebiet_bevoelkerung/bevoelkerungsstand/index.html

    And then in detail [this table](https://www.statistikdaten.bayern.de/genesis//online?operation=table&code=12411-001&bypass=true&levelindex=0&levelid=1774139315541#abreadcrumb) was used.
    """)
    return


@app.cell
def _(pd):
    PATH_CSV = "src/map_bubble/" + "population/12411-001.csv"

    def load_csv(path):
        print(f"Loading population dataset from: {path}")
        df = pd.read_csv(path, encoding="latin1", sep=";", skiprows=5, names=["Identifier", "Name", "Population"])
        return df

    df_raw = load_csv(PATH_CSV)
    df_raw
    return (df_raw,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Filter the dataset to include only rows that do correspond to cities.
    """)
    return


@app.cell
def _(df_raw, pd):
    def filter_cities(df):
        # Filter the DataFrame to include only rows with a Population value not NaN
        df = df[df['Population'].notna()]

        # Filter for Popultion not equal '-'
        df = df[df['Population'] != '-']
    
        # Filter the DataFrame to include only rows where the 'Identifier' has more than 3 digits
        df_cities = df[df['Identifier'].str.len() > 3]

        # Filter the DataFrame to remove rows where the 'Name' column contains the word "Lkr" (Landkreis).
        df_cities = df_cities[~df_cities['Name'].str.contains("Lkr")]

        # Rename Munich
        df_cities.loc[df_cities['Name'].str.contains('München, Landeshauptstadt'), ['Name']] = 'München'

        # Trim whitespace from the 'Name' column
        df_cities['Name'] = df_cities['Name'].str.strip()

        # Remove (Krfr.St) from the 'Name' column
        df_cities['Name'] = df_cities['Name'].str.replace(r'\s*\(Krfr\.St\)\s*', '', regex=True)

        # Remove everything after the last comma in the 'Name' column
        df_cities['Name'] = df_cities['Name'].str.replace(r',.*$', '', regex=True)

        # Convert Population column to numeric
        df_cities['Population'] = pd.to_numeric(df_cities['Population'])

        # Sum all rows with the same 'Name' and keep only the first occurrence
        df_cities = df_cities.groupby('Name', as_index=False).agg({'Population': 'sum', 'Identifier': 'first'})

        # Sort the DataFrame by Population in descending order
        df_cities = df_cities.sort_values(by='Population', ascending=False)
    
        return df_cities[['Identifier', 'Name', 'Population']]

    df_cities = filter_cities(df_raw)
    df_cities
    return (df_cities,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Match cities with geocoding dataset
    """)
    return


@app.cell
def _(gpd):
    PATH_GEOJSON = "src/map_bubble/" + "postal_codes_de.geojson"

    # Load data set from GeoJSON file
    def load_postal_codes(path: str):
        print(f"Loading file: {path}")
        return gpd.read_file(path)

    postal_codes = load_postal_codes(PATH_GEOJSON)
    postal_codes
    return (postal_codes,)


@app.cell
def _(df_cities, pd, postal_codes):
    def match_cities_with_geocoding(df_cities, postal_codes):
        # Merge the cities DataFrame with the postal codes GeoDataFrame on the 'Name' column
        # The postal_codes 'LAU_NAT' must only contain the city's 'Name' and must not be equal.
        for index, row in df_cities.iterrows():
            city_name = row['Name']
            postal_codes['Name'] = postal_codes['LAU_NAT'].apply(lambda lau_nat: city_name if city_name in lau_nat else None)

        df_merged = pd.merge(df_cities, postal_codes, on='Name', how='inner')
    

        # Select relevant columns and rename them
        #df_merged = df_merged[['Identifier', 'Name', 'Population', 'geometry']]
        #df_merged.rename(columns={'geometry': 'Coordinates'}, inplace=True)

        return df_merged

    df_matched = match_cities_with_geocoding(df_cities, postal_codes)
    df_matched

    return


if __name__ == "__main__":
    app.run()
