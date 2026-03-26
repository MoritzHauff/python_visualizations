# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.21.1",
#     "plotly>=6.6.0",
# ]
# ///

import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _():
    import marimo as mo

    import pandas as pd
    import geopandas as gpd
    import plotly.graph_objects as go

    return go, gpd, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Bubble Map - Bavarian Population

    This is a bubble map showing the population of cities in Bavaria.
    The size of each bubble corresponds to the population of the city, and the color indicates the population range.
    The data is sourced from the official Bavarian [statistical office](https://www.statistik.bayern.de/statistik/gebiet_bevoelkerung/bevoelkerungsstand/index.html).

    Reference on how to generate this type of plot: https://plotly.com/python/bubble-maps/
    """)
    return


@app.cell(hide_code=True)
def _(gpd):
    PATH_DATA = "src/map_bubble/" + "population/cities_population.geojson"

    # Fallback if data is not available offline
    try:
        f = open(PATH_DATA)
        f.close()
    except FileNotFoundError:
        # import urllib.request
        url = "https://raw.githubusercontent.com/MoritzHauff/python_visualizations/refs/heads/main/" + PATH_DATA
        print(f"Data file not found at {PATH_DATA}. Trying to download it from GitHub...")
        PATH_DATA = url
        # urllib.request.urlretrieve(url, PATH_DATA)


    # Load data set from GeoJSON file
    def load_postal_codes(path: str):
        print(f"Loading file: {path}")
        return gpd.read_file(path)


    def convert_to_lat_lon(df: gpd.GeoDataFrame):
        df["lon"] = df.geometry.x
        df["lat"] = df.geometry.y
        return df


    df = load_postal_codes(PATH_DATA)
    df = convert_to_lat_lon(df)

    df["text"] = df["Name"] + "<br>Post code " + (df["POSTCODE"]) + "<br>Population " + (df["Population"]).astype(str)
    df["size"] = df["Population"]
    df.head()
    return (df,)


@app.cell(hide_code=True)
def _(df, go, mo):
    def plot_bubble_map(df):
        limits = [(0, 3), (3, 11), (11, 21), (21, 50), (50, 3000)]
        colors = ["royalblue", "crimson", "lightseagreen", "orange", "lightgrey"]
        cities = []
        scale = 4000

        fig = go.Figure()

        for i in range(len(limits)):
            lim = limits[i]
            df_sub = df[lim[0] : lim[1]]
            fig.add_trace(
                go.Scattergeo(
                    locationmode="country names",
                    lon=df_sub["lon"],
                    lat=df_sub["lat"],
                    text=df_sub["text"],
                    marker=dict(
                        size=df_sub["size"] / scale,
                        color=colors[i],
                        line_color="rgb(40,40,40)",
                        line_width=0.5,
                        sizemode="area",
                    ),
                    name="{0} - {1}".format(lim[0], lim[1]),
                )
            )

        # Automatic zoom
        # https://plotly.com/python/map-configuration/
        fig.update_geos(fitbounds="locations")

        fig.update_layout(
            title_text="2024 Bavaria city populations<br>(Click legend to toggle traces)",
            showlegend=True,
            geo=dict(
                scope="europe",
                landcolor="rgb(217, 217, 217)",
            ),
            height=400,
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
        )

        return fig


    _fig = plot_bubble_map(df)

    # https://plotly.com/javascript/configuration-options/
    ui_fig = mo.ui.plotly(
        _fig,
        config={
            # Always show the mode bar (the toolbar with options like zoom, pan, etc.)
            "displayModeBar": True,
            # Select pan modus by default
            # "modeBarButtonsToAdd": ["pan2d"],
        },
    )
    ui_fig
    return (ui_fig,)


@app.cell(disabled=True)
def _(ui_fig):
    ui_fig.value
    return


if __name__ == "__main__":
    app.run()
