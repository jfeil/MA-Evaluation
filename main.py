from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import flask
import dash_bootstrap_components as dbc


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

server = flask.Flask(__name__)  # define flask app.server

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], server=server)
app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
], className="dash-bootstrap")


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x='year', y='pop')


if __name__ == '__main__':
    app.run(debug=True)
