import dash
from dash import Dash, dcc
import flask
import dash_bootstrap_components as dbc

server = flask.Flask(__name__)  # define flask app.server
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css], server=server, use_pages=True)

app.layout = [
    dcc.Location(id='url', refresh=False),
    dash.page_container
]


if __name__ == '__main__':
    app.run(debug=True)
