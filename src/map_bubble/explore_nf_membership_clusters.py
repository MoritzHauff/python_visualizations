import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import pandas as pd
    import plotly.express as px


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Naturfreunde Mitgliederzahlen nach Ortsgruppe und Alter
    """)
    return


@app.cell
def _():
    # https://plotly.com/python/tile-scatter-maps/

    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv"
    )
    fig = px.scatter_map(df, lat="lat", lon="long", size="cnt", zoom=3)
    fig.update_traces(cluster=dict(enabled=True))

    #fig.update_layout(
    #    map=dict(
    #        style="https://tile.openstreetmap.de/{z}/{x}/{y}.png"
    #    )
    #)

    # update the map layout (underlying tile provider)
    # https://plotly.com/python/tile-map-layers/
    fig.update_layout(map_style="open-street-map")

    fig.show()
    return


if __name__ == "__main__":
    app.run()
