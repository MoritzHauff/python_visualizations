import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:
    import io
    import json
    import requests
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    from functools import lru_cache
    from cryptography.fernet import InvalidToken

    from crypto.encryption import get_key, Fernet


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Naturfreunde Mitgliederzahlen nach Ortsgruppe und Alter
    """)
    return


@app.cell
def _():
    ui_text_password = mo.ui.text(label="Bitte Passwort eingeben:", placeholder="Passwort", kind="password")
    return (ui_text_password,)


@app.cell
def _(ui_text_password):
    ui_text_password
    return


@app.function
def get_data_air_traffic() -> pd.DataFrame:
    df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv"
    )
    return df


@app.function
@lru_cache(maxsize=None)
def download_file(url: str) -> bytes:
    """Downloads a file from the specified URL and provide it as IO buffer."""
    query_parameters = {}
    response = requests.get(url, params=query_parameters)
    if response.status_code != 200:
        raise Exception(f"Failed to download file from {url}. Status code: {response.status_code}")
    return response.content


@app.cell
def _(ui_text_password):
    _df = download_data(ui_text_password.value)
    return


@app.function
def download_data(password) -> pd.DataFrame:
    salt = download_file("https://raw.githubusercontent.com/MoritzHauff/python_visualizations/refs/heads/main/src/map_bubble/nf_membership/nf_membership_data.salt")

    print(f"Accessed salt successfully: {salt} type: {type(salt)}")

    file = download_file("https://raw.githubusercontent.com/MoritzHauff/python_visualizations/refs/heads/main/src/map_bubble/nf_membership/nf_membership_data.enc")

    # Only after both downloads were sucessful, we can proceed to get the key and decrypt the data
    key = get_key(password, salt)

    #file_stream = io.BytesIO(file)
    fernet = Fernet(key)
    try:
        data_bytes = fernet.decrypt(file)
    except InvalidToken:
        raise Exception("Decryption failed. Please check your password and try again.")
    data_json = json.loads(data_bytes.decode())
    
    return data_json


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
    return


if __name__ == "__main__":
    app.run()
