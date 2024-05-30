import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = dbc.Container(html.Div([
    html.H1('This is our Analytics page'),
    html.Div([
        "Select a city: ",
        dcc.RadioItems(
            options=['New York City', 'Montreal', 'San Francisco'],
            value='Montreal',
            id='analytics-input'
        )
    ]),
    html.Br(),
    html.Div(id='analytics-output'),
]))


@callback(
    Output('analytics-output', 'children'),
    Input('analytics-input', 'value')
)
def update_city_selected(input_value):
    return f'You selected: {input_value}'