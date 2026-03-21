import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import json
    import folium
    import pandas as pd
    import geopandas as gpd

    return folium, gpd, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Find postal code

    Load data set from GeoJSON file, all postal codes in Germany are included.
    The marimo table allows to select which postal codes should be shown on the map.

    The used dataset was released under the following licence:

    © European Union - GISCO, 2024, postal code point dataset, Licence CC-BY-SA 4.0.
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
    return (postal_codes,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Select which postal codes should be shown
    """)
    return


@app.cell
def _(mo, postal_codes):
    ui_table = mo.ui.table(postal_codes)
    ui_table
    return (ui_table,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Map
    """)
    return


@app.cell
def _(folium, gpd, ui_table):
    def plot_postal_codes(postal_codes):
        # Center map on Germany
        m = folium.Map(location=[51.7, 10], zoom_start=5.5)
    
        # Add point locations
        folium.GeoJson(
            postal_codes,
            name="Postal Codes",
            tooltip=folium.GeoJsonTooltip(fields=["POSTCODE", "LAU_NAT"], aliases=["Postleitzahl", "Name"]),
        ).add_to(m)
    
        folium.LayerControl().add_to(m)

        return m

    map = plot_postal_codes(gpd.GeoDataFrame(ui_table.value))
    map
    return


if __name__ == "__main__":
    app.run()
