import re
import uuid

from dash import Dash, html, dcc, callback, Output, Input, State
import flask
import dash_bootstrap_components as dbc

from src.database import random_question, submit_response, submit_error

server = flask.Flask(__name__)  # define flask app.server

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], server=server)
app.layout = dbc.Container(html.Div(
    [
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='session_uuid', storage_type='local'),
        html.H1(
            children='Jans Masterarbeitsevalurierungshilfswebseite :)',
            style={
                'textAlign': 'center',
            }
        ),
        html.H2(
            id="title",
            children='',
            style={
                'textAlign': 'center',
                'color': 'red'
            }
        ),
        html.Div(children="", id="output_question"),
        html.Div(children="", id="output_definition_1"),
        html.Div(children="", id="output_definition_2"),
        html.Button("SELECT 1", id="button_1"),
        html.Button("SELECT 2", id="button_2"),
        html.Button("!ERROR IN QUESTION!", id="button_error"),
    ]
), fluid=True)


@callback(
    Output("session_uuid", "data"),
    Input("session_uuid", "data")
)
def generate_uuid(current_uuid):
    if current_uuid is not None:
        return current_uuid
    return uuid.uuid4().hex


@callback(
    Output("title", "children"),
    Output("output_question", "children"),
    Output("output_definition_1", "children"),
    Output("output_definition_2", "children"),
    Input("url", "pathname")
)
def change_text(_):
    question, definition_1, definition_2 = random_question()

    highlighted_context = []
    modified_text = question.context_sentence.split(question.context_word.strip())
    for val in modified_text:
        highlighted_context += [val, html.Span(question.context_word.strip(), style={'color': 'red'}), ]

    return [
        [question.title, html.Span(str(question.id), style={"visibility": "hidden"})],
        highlighted_context[:-1],
        [definition_1.text, html.Span(str(definition_1.id), style={"visibility": "hidden"})],
        [definition_2.text, html.Span(str(definition_2.id), style={"visibility": "hidden"})],
    ]


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("button_1", "n_clicks"),
    State("title", "children"),
    State("output_definition_1", "children"),
    State("output_definition_2", "children"),
    State("session_uuid", "data"),
    prevent_initial_call=True
)
def submit_1(_, question, output_1, output_2, session_id):
    submit_selection(question, output_1, output_2, session_id)
    return "/"


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("button_2", "n_clicks"),
    State("title", "children"),
    State("output_definition_1", "children"),
    State("output_definition_2", "children"),
    State("session_uuid", "data"),
    prevent_initial_call=True
)
def submit_2(_, question, output_1, output_2, session_id):
    submit_selection(question, output_2, output_1, session_id)
    return "/"


def submit_selection(question, winner, loser, session_id):
    submit_response(question[1]['props']['children'], winner[1]['props']['children'], loser[1]['props']['children'], session_id)


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("button_1", "n_clicks"),
    State("title", "children"),
    State("session_uuid", "data"),
    prevent_initial_call=True
)
def submit_question_error(_, question, session_id):
    submit_error(question[1]['props']['children'], session_id[1]['props']['children'])
    return "/"


if __name__ == '__main__':
    app.run(debug=True)
