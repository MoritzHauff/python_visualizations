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


@app.function
def get_data() -> pd.DataFrame:
    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv"
    )
    return df


@app.cell
def _():
    df = get_data()

    # https://plotly.com/python/tile-scatter-maps/
    fig = px.scatter_map(
        df,
        lat="lat",  # latitude column
        lon="long",  # longitude column
        size="cnt",  # size of the markers based on the 'cnt' column
        size_max=100,  # maximum mark size (defalt 20)
        zoom=3,
    )
    # enable clustering of points if they are close together
    fig.update_traces(cluster=dict(enabled=True))

    # update the map layout (underlying tile provider)
    # https://plotly.com/python/tile-map-layers/
    fig.update_layout(map_style="open-street-map")

    fig.show()
    return


if __name__ == "__main__":
    app.run()
