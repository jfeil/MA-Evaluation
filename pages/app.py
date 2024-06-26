import uuid

import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc

from src.database import random_question, submit_response, submit_error

dash.register_page(__name__, path='/')


layout = dbc.Container(html.Div(
    [
        dcc.Store(id='session_uuid', storage_type='local'),
        html.H1(
            children='Jans Masterarbeitsevaluierungshilfswebseite :)',
            style={
                'textAlign': 'center',
            }
        ),
        dbc.Card([
            dbc.CardHeader([
                html.H5("", id="title", className="card-title"),
            ]),
            dbc.CardBody(
                [
                    html.P(
                        "",
                        id="output_question",
                        className="card-text",
                    ),
                ]
            )]),
        html.Div(children="", id=""),
        dbc.CardGroup(
            [
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Option 1", id="info_1", className="card-title"),
                    ]),
                    dbc.CardBody(
                        [
                            html.P(
                                "",
                                id="output_definition_1",
                                className="card-text",
                            ),
                            dbc.Button(
                                "1 ist besser", id="button_1", color="primary", className="mt-auto"
                            ),
                        ]
                    )]
                ),
                dbc.Card([
                    dbc.CardHeader(
                        [html.H5("Option 2", id="info_2", className="card-title")]
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                "",
                                id="output_definition_2",
                                className="card-text",
                            ),
                            dbc.Button(
                                "2 ist besser", id="button_2", color="success", className="mt-auto"
                            ),
                        ]
                    )]
                )]),
        html.Br(),
        dbc.Button("!ERROR IN QUESTION!", id="button_error", color="danger", className="me-1"),
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
    Output("info_1", "children"),
    Output("info_2", "children"),
    Input("url", "pathname")
)
def change_text(_):
    question, definition_1, definition_2, generator_1, generator_2 = random_question()

    highlighted_context = []
    modified_text = question.context_sentence.split(question.context_word.strip())
    for val in modified_text:
        highlighted_context += [val, html.Span(question.context_word.strip(), style={'color': 'red'}), ]

    return [
        [question.title.strip(), html.Span(str(question.id), style={"visibility": "hidden"})],
        highlighted_context[:-1],
        [definition_1.text, html.Span(str(definition_1.id), style={"visibility": "hidden"})],
        [definition_2.text, html.Span(str(definition_2.id), style={"visibility": "hidden"})],
        ["Option 1", f" ({generator_1.type}: {generator_1.name})"],
        ["Option 2", f" ({generator_2.type}: {generator_2.name})"]
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
    if not question:
        return dash.no_update
    submit_selection(question, output_1, output_2, 0, session_id)
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
    if not question:
        return dash.no_update
    submit_selection(question, output_1, output_2, 1, session_id)
    return "/"


def submit_selection(question, left, right, winner, session_id):
    submit_response(question[1]['props']['children'], left[1]['props']['children'], right[1]['props']['children'],
                    winner, session_id)


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("button_error", "n_clicks"),
    State("title", "children"),
    State("session_uuid", "data"),
    prevent_initial_call=True
)
def submit_question_error(_, question, session_id):
    if not question:
        return dash.no_update
    submit_error(question[1]['props']['children'], session_id)
    return "/"
