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


@app.function
def get_data_air_traffic() -> pd.DataFrame:
    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv")
    return df


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
def _(df, ui_filter_age_groups, ui_settings, ui_settings_show_raw_df):
    mo.accordion(
        {
            "Einstellungen": ui_settings,
            "Rohdaten": df if ui_settings_show_raw_df.value else mo.md('Aktiviere "Rohdaten", in den Einstellungen.'),
            "Filter": ui_filter_age_groups,
        },
        multiple=True,
    )
    return


@app.cell
def _():
    get_age_updated, set_age_updated = mo.state(1)
    return get_age_updated, set_age_updated


@app.cell
def _(set_age_updated):
    age_groups = ["0-8", "9-14", "15-18", "19-26", "27-45", "46-57", "58-64", "65-75", ">75"]
    ui_checkoboxes_age_groups = {
        age_group: mo.ui.checkbox(label=age_group.replace(">", "\>"), value=True, on_change=set_age_updated) for age_group in age_groups
    }

    ui_filter_age_groups = mo.vstack([mo.md("Summiere folgende Altersgruppen"), mo.hstack(ui_checkoboxes_age_groups.values())])
    return age_groups, ui_checkoboxes_age_groups, ui_filter_age_groups


@app.cell
def _(age_groups, ui_checkoboxes_age_groups):
    def determine_col_size():
        """If all age filter checkboxes are checked use the total membership column otherwise use the sum of the selected age groups."""
        if all(ui_checkoboxes_age_groups[age_group].value for age_group in age_groups):
            return "Mitglieder.gesamt"
        else:
            return "Mitglieder.summiert"

    return (determine_col_size,)


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
            return False, pd.DataFrame()

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
    data_success, df_raw = prepare_data_nf_membership()
    return data_success, df_raw


@app.cell
def _():
    # df_raw
    return


@app.cell
def _(
    age_groups,
    determine_col_size,
    df_raw,
    get_age_updated,
    ui_checkoboxes_age_groups,
):
    get_age_updated()  # COL_SIZE should be updated each time one checkbox is updated.
    COL_SIZE = determine_col_size()
    df = df_raw

    # if all age groups are selected, we can use the total membership column, otherwise we need to sum up the selected age groups to get the total membership for the selected age groups.
    if COL_SIZE == "Mitglieder.summiert":
        enabled_age_groups = [f"Mitglieder Alter.{age_group}" for age_group in age_groups if ui_checkoboxes_age_groups[age_group].value]
        df[COL_SIZE] = df[enabled_age_groups].sum(axis=1)
    return COL_SIZE, df


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Karte
    """)
    return


@app.cell
def _(
    COL_GROUP,
    COL_SIZE,
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
            COL_SIZE: True,
            "Altersdurchschnitt": ":.1f",  # format to one decimal place"
            "Frauenanteil (Prozent)": ":.1f",  # format to one decimal place"
        }

        # create a scatter map
        fig = px.scatter_map(
            df,
            lat="lat",  # latitude column
            lon="lon",  # longitude column
            size=COL_SIZE,  # column which determines the size of the markers
            size_max=ui_layout_marker_size.value,  # maximum mark size (defalt 20)
            color=ui_layout_color_column.value,  # column which determines the color of the markers
            hover_name=COL_GROUP,  # column to show in the hover tooltip
            hover_data=hover_data,  # columns to show/hide in the hover tooltip
            custom_data=[COL_GROUP],  # column to include in the click event data
            # labels={"Mitglieder.gesamt": "Mitglieder"},  # rename column for legend
            zoom=6,  # initial zoom level
            title="Mitgliederzahlen der Naturfreunde Ortsgruppen in Bayern (2025)",  # set title
        )
        # enable clustering of points if they are close together
        if ui_layout_checkbox_cluster.value:
            fig.update_traces(cluster=dict(enabled=True))

        # update the map layout (underlying tile provider)
        # https://plotly.com/python/tile-map-layers/
        fig.update_layout(map_style="open-street-map")

        # Start in pan mode
        fig.update_layout(dragmode="pan")

        # increase height of the figure
        fig.update_layout(height=ui_settings_map_height.value)

        return fig


    _df = get_data_air_traffic()
    fig = plot_map(df)
    return (fig,)


@app.cell
def _():
    ui_label_map = mo.md("""
    Diese Karte ist interaktiv. Mit der "Pan" Funktion oben rechts über der Karte, kann diese verschoben werden. Mithilfe von "Box Select" und "Lasso" können bestimmte Ortsgruppen ausgewählt werden, um diese genauer zu untersuchen.
    """)
    return (ui_label_map,)


@app.cell
def _(fig, ui_settings_always_show_mode_bar):
    _plotly_options = {}
    if ui_settings_always_show_mode_bar.value:
        # https://plotly.com/python/configuration-options/
        # always show the mode bar (the toolbar above the plot with the buttons for zooming, saving, etc.)
        _plotly_options["displayModeBar"] = True

    # add a custom button to the mode bar to download the plot as an HTML file
    #_plotly_options["modeBarButtonsToAdd"] = [
    #         {
    #             "name": "Download HTML",
    #             "icon": "download",
    #             "click": """
    #                 function(gd) {
    #                     const html = Plotly.toHTML(gd.data, gd.layout);
    #                     const blob = new Blob([html], {type: 'text/html'});
    #                     const a = document.createElement('a');
    #                     a.href = URL.createObjectURL(blob);
    #                     a.download = 'map_plot_nf_membership_2025.html';
    #                     a.click();
    #                 }
    #             """
    #         }
    #     ]
    # 

    plot = mo.ui.plotly(fig, config=_plotly_options)
    return (plot,)


@app.cell
def _(data_success):
    _out = None
    if not data_success:
        _out = mo.callout("Zugriff auf Daten verweigert. Bitte überprüfe dein Passwort und lade die Seite zu einem späteren Zeitpunkt neu, um es erneut zu versuchen.", kind="warn")
    _out
    return


@app.cell
def _(data_success, plot, ui_label_map, ui_layout):
    _out = None  # use two different cells to now ancestor exceptions prevent rendering of the warning callout
    if data_success:
        _out = mo.vstack([
            ui_layout,
            ui_label_map,
            plot,
        ])

    _out
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Details
    """)
    return


@app.cell
def _(COL_GROUP, COL_SIZE, df, plot):
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
        [COL_GROUP, "Bezirk", COL_SIZE, "Altersdurchschnitt", "Frauenanteil (Prozent)"]
        + [
            col
            for col in df_details.columns
            if col not in [COL_GROUP, "Bezirk", COL_SIZE, "Altersdurchschnitt", "Frauenanteil (Prozent)"]
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
def _(fig):
    # HTML download with lazy loading
    async def get_html_data():
        _data = io.StringIO()
        # https://plotly.com/python-api-reference/generated/plotly.io.write_html.html
        fig.write_html(_data, full_html=True)
        return _data.getvalue().encode("utf-8")

    # https://docs.marimo.io/api/media/download/
    ui_download_html_lazy = mo.download(
        data=get_html_data,
        filename="plot_map_nf_membership_2025.html",
        mimetype="text/html",
        label="Download aktuelle Karte als HTML",
        disabled=True,  # shows 403r Access blocked
    )
    return get_html_data, ui_download_html_lazy


@app.cell(disabled=True)
async def _(get_html_data):
    await get_html_data()
    return


@app.cell(disabled=True)
def _(ui_download_html_lazy):
    ui_download_html_lazy
    return


if __name__ == "__main__":
    app.run()
