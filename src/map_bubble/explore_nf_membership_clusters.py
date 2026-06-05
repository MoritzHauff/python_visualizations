import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")

with app.setup:
    import json
    import locale
    import requests
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    from functools import lru_cache
    from cryptography.fernet import InvalidToken

    from crypto.encryption import get_key, Fernet

    # Set the locale to German
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")


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


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Einstellungen und Filter
    """)
    return


@app.cell
def _(df, ui_settings, ui_settings_show_raw_df):
    mo.accordion(
        {
            "Einstellungen": ui_settings,
            "Rohdaten": df if ui_settings_show_raw_df.value else mo.md('Aktiviere "Rohdaten", in den Einstellungen.'),
            "Filter": mo.md("Hier kommen bald Filter dazu."),
        },
        multiple=True,
    )
    return


@app.function
def get_data_air_traffic() -> pd.DataFrame:
    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv")
    return df


@app.function
@lru_cache(maxsize=None)
def download_file(url: str) -> bytes:
    """Downloads a file from the specified URL and provide it as bytes.
    https://realpython.com/python-download-file-from-url/"""
    query_parameters = {}
    response = requests.get(url, params=query_parameters)
    if response.status_code != 200:
        raise Exception(f"Failed to download file from {url}. Status code: {response.status_code}")
    print(f"Successfully downloaded file from {url}. Size: {len(response.content)} bytes.")
    return response.content


@app.function
def download_data(password) -> dict:
    """Downloads the encrypted data file and the corresponding salt, derives the encryption key using the provided password, and decrypts the data."""
    salt = download_file(
        "https://raw.githubusercontent.com/MoritzHauff/python_visualizations/refs/heads/main/src/map_bubble/nf_membership/nf_membership_data.salt"
    )
    # print(f"Accessed salt successfully: {salt} type: {type(salt)}")

    file = download_file(
        "https://raw.githubusercontent.com/MoritzHauff/python_visualizations/refs/heads/main/src/map_bubble/nf_membership/nf_membership_data.enc"
    )

    # Only after both downloads were sucessful, we can proceed to get the key and decrypt the data
    key = get_key(password, salt)

    fernet = Fernet(key)
    try:
        data_bytes = fernet.decrypt(file)
    except InvalidToken:
        raise Exception("Decryption failed. Please check your password and try again.")
    data_json = json.loads(data_bytes.decode())

    return data_json


@app.cell
def _():
    COL_GROUP = "Gruppenbez."
    return (COL_GROUP,)


@app.cell
def _(COL_GROUP, ui_text_password):
    def prepare_data_nf_membership() -> tuple[bool, pd.DataFrame]:
        try:
            data_dict = download_data(ui_text_password.value)
            df_locations = pd.DataFrame.from_records(data_dict["group_locations"])
            df_memberships = pd.DataFrame.from_records(data_dict["group_memberships"])
        except Exception as e:
            print(f"**Fehler:** {str(e)}")
            return False, pd.DataFrame(), True

        # validate data
        if len(df_locations) == 0 or len(df_memberships) == 0:
            print("**Fehler:** Die heruntergeladenen Daten sind leer.")
            return False, pd.DataFrame()

        if len(df_locations) != len(df_memberships):
            print(
                "**Warnung:** Die Anzahl der Ortsgruppen in den beiden Datensätzen stimmt nicht überein. Es könnte sein, dass einige Gruppen in einem Datensatz fehlen."
            )

        # clean data
        df_locations = df_locations.rename(columns={"Unnamed: 6": "Koordinaten Kommentar"})
        df_locations = df_locations.rename(columns={"Gruppenbezeichnung": COL_GROUP})
        # df_locations[COL_GROUP] = df_locations[COL_GROUP].str.replace("Bezirk München", "Bz München")

        df_memberships = df_memberships.rename(columns={"Gruppenbezeichnung": COL_GROUP})
        df_memberships[COL_GROUP] = df_memberships[COL_GROUP].str.replace("Bz München", "Bezirk München")
        df_memberships.columns = df_memberships.columns.str.replace(
            "Anzahl der Mitglieder nach Altersgruppen.", "Mitglieder Alter."
        )

        # combine the two dataframes to have the membership numbers directly in the location dataframe
        df_combined = pd.merge(df_locations, df_memberships, left_on=COL_GROUP, right_on=COL_GROUP, how="outer")
        df_combined[COL_GROUP] = df_combined[COL_GROUP].str.replace("LV Bayern", "Landesverband Bayern")
        return True, df_combined

    return (prepare_data_nf_membership,)


@app.cell
def _(prepare_data_nf_membership):
    data_success, df = prepare_data_nf_membership()
    return (df,)


@app.cell
def _():
    # df
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Karte
    """)
    return


@app.cell
def _(
    COL_GROUP,
    df,
    ui_layout_checkbox_cluster,
    ui_layout_color_column,
    ui_layout_marker_size,
    ui_settings_map_height,
):
    def plot_map(df: pd.DataFrame) -> go.Figure:
        # https://plotly.com/python/tile-scatter-maps/
        # https://plotly.com/python-api-reference/generated/plotly.express.scatter_map.html

        hover_data = {
            "lat": False,
            "lon": False,
            "Bezirk": True,
            "Mitglieder.gesamt": True,
            "Altersdurchschnitt": ":.1f",  # format to one decimal place"
            "Frauenanteil (Prozent)": ":.1f",  # format to one decimal place"
        }

        # create a scatter map
        fig = px.scatter_map(
            df,
            lat="lat",  # latitude column
            lon="lon",  # longitude column
            size="Mitglieder.gesamt",  # column which determines the size of the markers
            size_max=ui_layout_marker_size.value,  # maximum mark size (defalt 20)
            color=ui_layout_color_column.value,  # column which determines the color of the markers
            hover_name=COL_GROUP,  # column to show in the hover tooltip
            hover_data=hover_data,  # columns to show/hide in the hover tooltip
            custom_data=[COL_GROUP],  # column to include in the click event data
            # labels={"Mitglieder.gesamt": "Mitglieder"},  # rename column for legend
            zoom=6,  # initial zoom level
        )
        # enable clustering of points if they are close together
        if ui_layout_checkbox_cluster.value:
            fig.update_traces(cluster=dict(enabled=True))

        # update the map layout (underlying tile provider)
        # https://plotly.com/python/tile-map-layers/
        fig.update_layout(map_style="open-street-map")

        # increase height of the figure
        fig.update_layout(height=ui_settings_map_height.value)

        return fig


    _df = get_data_air_traffic()
    fig = plot_map(df)
    return (fig,)


@app.cell
def _(ui_layout):
    ui_layout
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Diese Karte ist interaktiv. Mit der "Pan" Funktion oben rechts über der Karte, kann diese verschoben werden.
    Mithilfe von "Box Select" und "Lasso" können bestimmte Ortsgruppen ausgewählt werden, um diese genauer zu untersuchen.
    """)
    return


@app.cell
def _(fig, ui_settings_always_show_mode_bar):
    _plotly_options = {}
    if ui_settings_always_show_mode_bar.value:
        # https://plotly.com/python/configuration-options/
        _plotly_options["displayModeBar"] = True

    plot = mo.ui.plotly(fig, config=_plotly_options)
    plot
    return (plot,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Details
    """)
    return


@app.cell
def _(plot):
    plot.value
    return


@app.cell
def _(COL_GROUP, df, plot):
    df_details = df
    # Get user selection if available
    selection = plot.value
    if selection is not None and len(selection) > 0:
        selected_groups = pd.DataFrame(selection)
        df_details = df_details[df_details["lat"].isin(selected_groups["lat"]) & df_details["lon"].isin(selected_groups["lon"])]  # filter the details dataframe to the selected group

    # remove uninteresting columns
    _remove_columns = ["lat", "lon", "Postleitzahl", "Stadt", "Strasse", "Koordinaten Kommentar"]
    df_details = df_details[[col for col in df_details.columns if col not in _remove_columns]]

    # reorder columns for interesting columns first then the rest
    df_details = df_details[
        [COL_GROUP, "Bezirk", "Mitglieder.gesamt", "Altersdurchschnitt", "Frauenanteil (Prozent)"]
        + [
            col
            for col in df_details.columns
            if col not in [COL_GROUP, "Bezirk", "Mitglieder.gesamt", "Altersdurchschnitt", "Frauenanteil (Prozent)"]
        ]
    ]

    mo.ui.table(df_details, freeze_columns_left=[COL_GROUP])
    return


@app.cell
def _():
    # Layout UI elements
    ui_layout_checkbox_cluster = mo.ui.checkbox(label="Gruppieren", value=True)

    ui_layout_color_column = mo.ui.dropdown(
        label="Farbkategorie",
        options={
            "Einfarbig": None,
            "Bezirk": "Bezirk",
            "Altersdurchschnitt": "Altersdurchschnitt",
            "Frauenanteil": "Frauenanteil (Prozent)",
        },
        value="Bezirk",
    )

    ui_layout_marker_size = mo.ui.slider(start=10, stop=200, step=10, label="Kreisgröße", value=100)

    ui_layout = mo.hstack(
        [
            ui_layout_checkbox_cluster,
            ui_layout_color_column,
            ui_layout_marker_size,
        ]
    )
    return (
        ui_layout,
        ui_layout_checkbox_cluster,
        ui_layout_color_column,
        ui_layout_marker_size,
    )


@app.cell
def _():
    # Settings UI elements
    ui_settings_map_height = mo.ui.number(label="Höhe der Karte", value=700, start=300, stop=2000)
    ui_settings_always_show_mode_bar = mo.ui.checkbox(label="Karten Tool Bar immer anzeigen", value=True)
    ui_settings_show_raw_df = mo.ui.checkbox(label="Rohdaten anzeigen", value=False)

    ui_settings = mo.vstack(
        [
            ui_settings_map_height, 
            ui_settings_always_show_mode_bar,
            ui_settings_show_raw_df,
        ]
    )
    return (
        ui_settings,
        ui_settings_always_show_mode_bar,
        ui_settings_map_height,
        ui_settings_show_raw_df,
    )


@app.cell
def _(ui_settings):
    ui_settings
    return


if __name__ == "__main__":
    app.run()
