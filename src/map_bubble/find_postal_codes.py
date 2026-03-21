import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import os
    import requests
    import zipfile
    import geopandas as gpd

    return os, requests, zipfile


@app.cell
def _(os, requests, zipfile):
    # GISCO postal code dataset (2024 release)
    # https://ec.europa.eu/eurostat/web/gisco/geodata/administrative-units/postal-codes
    URL = "https://gisco-services.ec.europa.eu/distribution/v2/pcode/shp/PCODE_PT_2024_4326.shp.zip"
    ZIP_PATH = "src/map_bubble/" + "postal_codes.zip"
    EXTRACT_DIR = "src/map_bubble/" + "postal_codes"

    # Download if not already present
    if not os.path.exists(ZIP_PATH):
        print("Downloading GISCO postal code dataset...")
        r = requests.get(URL)
        with open(ZIP_PATH, "wb") as f:
            f.write(r.content)

    # Extract ZIP
    if not os.path.exists(EXTRACT_DIR):
        print("Extracting ZIP...")
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)

    print("Download & extraction complete.")
    return


if __name__ == "__main__":
    app.run()
