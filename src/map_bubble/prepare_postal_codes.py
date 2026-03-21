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

    return glob, gpd, os, pd, requests, zipfile


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
    return


if __name__ == "__main__":
    app.run()
