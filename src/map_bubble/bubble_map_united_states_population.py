import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import pandas as pd
    import plotly.graph_objects as go

    return go, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Bubble Map - United States Population

    This is a bubble map showing the population of cities in the United States.
    The size of each bubble corresponds to the population of the city, and the color indicates the population range.
    The data is sourced from a CSV file containing information about US cities and their populations.

    Reference: https://plotly.com/python/bubble-maps/
    """)
    return


@app.cell
def _(pd):
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_us_cities.csv')

    df['text'] = df['name'] + '<br>Population ' + (df['pop']/1e6).astype(str)+' million'
    df.head()
    return (df,)


@app.cell
def _(df, go):
    def plot_bubble_map(df):
        limits = [(0,3),(3,11),(11,21),(21,50),(50,3000)]
        colors = ["royalblue","crimson","lightseagreen","orange","lightgrey"]
        cities = []
        scale = 5000
    
        fig = go.Figure()
    
        for i in range(len(limits)):
            lim = limits[i]
            df_sub = df[lim[0]:lim[1]]
            fig.add_trace(go.Scattergeo(
                locationmode = 'USA-states',
                lon = df_sub['lon'],
                lat = df_sub['lat'],
                text = df_sub['text'],
                marker = dict(
                    size = df_sub['pop']/scale,
                    color = colors[i],
                    line_color='rgb(40,40,40)',
                    line_width=0.5,
                    sizemode = 'area'
                ),
                name = '{0} - {1}'.format(lim[0],lim[1])))
    
        fig.update_layout(
                title_text = '2014 US city populations<br>(Click legend to toggle traces)',
                showlegend = True,
                geo = dict(
                    scope = 'usa',
                    landcolor = 'rgb(217, 217, 217)',
                )
            )
    
        return fig

    plot_bubble_map(df)
    return


if __name__ == "__main__":
    app.run()
