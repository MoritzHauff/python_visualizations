import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import os
    import glob
    import requests
    import zipfile
    import pandas as pd
    import geopandas as gpd

    return glob, gpd, mo, os, pd, requests, zipfile


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Prepare postal codes geodata

    The code below downloads the [GISCO](https://ec.europa.eu/eurostat/web/gisco/geodata/administrative-units/postal-codes) postal code dataset,
    extracts it, loads the shapefiles into a GeoDataFrame, filters for German postal codes, and saves the filtered data as a GeoJSON file.
    The final GeoDataFrame is also displayed using Marimo's UI.

    The dataset was released under the following licence:

    © European Union - GISCO, 2024, postal code point dataset, Licence CC-BY-SA 4.0.
    """)
    return


@app.cell
def _(os, requests, zipfile):
    # GISCO postal code dataset (2024 release)
    # https://ec.europa.eu/eurostat/web/gisco/geodata/administrative-units/postal-codes
    URL = "https://gisco-services.ec.europa.eu/distribution/v2/pcode/shp/PCODE_PT_2024_4326.shp.zip"
    ZIP_PATH = "src/map_bubble/" + "postal_codes.zip"
    EXTRACT_DIR = "src/map_bubble/" + "postal_codes"

    def download_and_extract():
        # Download if not already present
        if not os.path.exists(ZIP_PATH):
            print("Downloading GISCO postal code dataset...")
            r = requests.get(URL)
            with open(ZIP_PATH, "wb") as f:
                f.write(r.content)
        else:
            print("ZIP file already exists. Skipping download.")
    
        # Extract ZIP
        if not os.path.exists(EXTRACT_DIR):
            print("Extracting ZIP...")
            with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
                zip_ref.extractall(EXTRACT_DIR)
        else:
            print("Extracted folder already exists. Skipping extraction.")
    
        print("Download & extraction complete.")

    download_and_extract()
    return (EXTRACT_DIR,)


@app.cell
def _(EXTRACT_DIR, glob, gpd, pd):
    def load_postal_codes(extract_dir: str):
        # Load all shapefiles inside the extracted folder
        shp_files = glob.glob(f"{extract_dir}/**/*.shp", recursive=True)
    
        gdfs = []
        for shp in shp_files:
            print(f"Processing file: {shp}")
            gdf = gpd.read_file(shp)
            gdfs.append(gdf)
    
        # Merge into a single GeoDataFrame
        postal_codes = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
    
        # Reproject to WGS84 for web mapping
        postal_codes = postal_codes.to_crs(epsg=4326)

        return postal_codes


    postal_codes = load_postal_codes(EXTRACT_DIR)
    print(postal_codes.head())
    return (postal_codes,)


@app.cell
def _(gpd, postal_codes):
    GEOJSON_PATH = "src/map_bubble/" + "postal_codes_de.geojson"

    def filter_postal_codes(gdf: gpd.GeoDataFrame, country_id: str="DE"):
        # Assuming the country code is stored in a column named 'CNTR_ID'
        filtered_gdf = gdf[gdf["CNTR_ID"] == country_id]
        # Only return relevant columns (e.g., postal code, city name and geometry)
        filtered_gdf = filtered_gdf[["POSTCODE", "LAU_NAT", "geometry"]]
        return filtered_gdf

    postal_codes_filtered = filter_postal_codes(postal_codes, country_id="DE")
    postal_codes_filtered.to_file(GEOJSON_PATH, driver="GeoJSON")
    print("Filtered postal codes saved as GeoJSON.")
    postal_codes_filtered
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explore data further

    Here you can use the Marimo Dataframe UI to explore the data set further.
    """)
    return


@app.cell
def _(mo, postal_codes):
    mo.ui.dataframe(postal_codes)
    return


if __name__ == "__main__":
    app.run()
