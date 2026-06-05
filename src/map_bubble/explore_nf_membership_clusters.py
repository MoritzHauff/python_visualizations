import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:
    import io
    import requests
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    from crypto.encryption import get_key, read_encrypted_json


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Naturfreunde Mitgliederzahlen nach Ortsgruppe und Alter
    """)
    return


@app.function
def get_data_air_traffic() -> pd.DataFrame:
    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv"
    )
    return df


@app.function
def download_file(url: str) -> bytes:
    """Downloads a file from the specified URL and provide it as IO buffer."""
    query_parameters = {}
    response = requests.get(url, params=query_parameters)
    if response.status_code != 200:
        raise Exception(f"Failed to download file from {url}. Status code: {response.status_code}")
    return response.content


@app.cell
def _():
    #file = download_file("https://WRONG_URL")
    file = download_file("https://raw.githubusercontent.com/MoritzHauff/python_visualizations/refs/heads/main/src/map_bubble/nf_membership/nf_membership_data.enc")
    file

    return


@app.function
def get_data_nf_membership() -> pd.DataFrame:
    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv"
    )
    return df


@app.cell
def _(get_data):
    def plot_map(df: pd.DataFrame) -> go.Figure:
        # https://plotly.com/python/tile-scatter-maps/
        # https://plotly.com/python-api-reference/generated/plotly.express.scatter_map.html
    
        # create a scatter map
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

        return fig
    
    df = get_data()
    fig = plot_map(df)
    fig.show()
    return (df,)


if __name__ == "__main__":
    app.run()
