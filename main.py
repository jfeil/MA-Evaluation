import dash
from dash import Dash
import flask
import dash_bootstrap_components as dbc

server = flask.Flask(__name__)  # define flask app.server

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], server=server, use_pages=True)

app.layout = [
    dash.page_container
]


if __name__ == '__main__':
    app.run(debug=True)
