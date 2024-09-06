import base64
import time
import uuid

import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc

from src.database import random_question, submit_response, submit_error, get_highscore

dash.register_page(__name__, path='/')

image_filename = 'assets/medal-champion-award-winner-olympic-2.svg'
encoded_image = base64.b64encode(open(image_filename, 'rb').read()).decode()

help_modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Herzlich Willkommen!"), close_button=True),
                dbc.ModalBody("Hey du :)\n"
                              "\n"
                              "Super, dass du Lust hast mir bei meiner Masterarbeit zu helfen! In der Arbeit geht es um"
                              " die automatisierte Erstellung von Definitionen für Wörter.\n"
                              "\n"
                              "Du findest ganz oben das Wort, welches wir definieren wollen, gefolgt von einem "
                              "Beispielsatz, der das Wort beinhaltet. Hier ist das Wort auch immer (hoffentlich) rot "
                              "markiert. \n\n"
                              "Deine Aufgabe ist zu bewerten, welche Definition dir besser gefällt. Wenn du das Wort "
                              "nicht kennst, nimmst du bitte die Definition, die für dich sinnvoller klingt! Du musst "
                              "NICHT das Wort suchen und definieren!\n\n"
                              "Danke für deine Mithilfe!\n"
                              "Dein Jan :)",
                              style={"white-space": "pre-line"}),
                dbc.ModalFooter(
                    dbc.Button(
                        "Gelesen und Verstanden!",
                        id="close-centered",
                        className="ms-auto",
                        n_clicks=0,
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=False,
            keyboard=False,
            backdrop="static"
        ),
    ]
)


layout = dbc.Container(html.Div(
    [
        dcc.Store(id='session_uuid', storage_type='local'),
        dcc.Store(id='help_presented', storage_type='session'),
        dcc.Store(id='load-time', data=time.time()),
        help_modal,
        # Title (Centered)
        html.H1(
            children='Jans Masterarbeits​evaluierungs​hilfs​webseite :)',
            style={'textAlign': 'center'}
        ),
        html.Div([
            dbc.Button("?", id="button_help", color="info", className="mt-auto")
        ], className="d-grid gap-2 d-md-flex justify-content-md-end"),
        html.Br(),
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
        dbc.Button("!ERROR IN QUESTION!", id="button_error", color="danger", className="me-1",
                   style={"display": "none"}),
        html.Div(id="highscore-div", style={"white-space": "pre-line"}),
        html.Br(),
        html.Div([
            dbc.Button("Überspringen", id="button_skip", color="danger", className="mt-auto"),
        ], className="d-grid gap-2 d-md-flex justify-content-md-end"),
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
    Output("help_presented", "data"),
    Output("modal-centered", "is_open"),
    Input("help_presented", "data"),
    Input("button_help", "n_clicks"),
    Input("close-centered", "n_clicks"),
    State("modal-centered", "is_open"),
    prevent_initial_call=True
)
def initial_help(help_presented, n_open, n_close, is_open):
    help_presented = help_presented is None
    if help_presented or n_open or n_close:
        return help_presented, not is_open
    return help_presented, is_open


@callback(
    Output("title", "children"),
    Output("output_question", "children"),
    Output("output_definition_1", "children"),
    Output("output_definition_2", "children"),
    Output("info_1", "children"),
    Output("info_2", "children"),
    Output("load-time", "data"),
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
        ["Option 1"],  # , f" ({generator_1.type}: {generator_1.name})"],
        ["Option 2"],  # , f" ({generator_2.type}: {generator_2.name})"],
        time.time()
    ]


@callback(
    Output("highscore-div", "children"),
    Input("url", "pathname"),
    State("session_uuid", "data"),
)
def gamification(_, session_id):
    highscore, userscore = get_highscore(session_id)
    resp = [(f"Deine bisherige Anzahl an Antworten: {userscore}\n"
            f"Highscore: {highscore}")]
    if highscore <= userscore:
        resp.append(html.Img(src='assets/medal-champion-award-winner-olympic-2.svg'))
    return resp


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("button_skip", "n_clicks"),
    prevent_initial_call=True
)
def skip(_):
    return "/"


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("button_1", "n_clicks"),
    State("title", "children"),
    State("output_definition_1", "children"),
    State("output_definition_2", "children"),
    State("session_uuid", "data"),
    State("load-time", "data"),
    prevent_initial_call=True
)
def submit_1(_, question, output_1, output_2, session_id, load_time):
    if not question:
        return dash.no_update
    submit_selection(question, output_1, output_2, 0, session_id, load_time)
    return "/"


@callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("button_2", "n_clicks"),
    State("title", "children"),
    State("output_definition_1", "children"),
    State("output_definition_2", "children"),
    State("session_uuid", "data"),
    State("load-time", "data"),
    prevent_initial_call=True
)
def submit_2(_, question, output_1, output_2, session_id, load_time):
    if not question:
        return dash.no_update
    submit_selection(question, output_1, output_2, 1, session_id, load_time)
    return "/"


def submit_selection(question, left, right, winner, session_id, load_time):
    time_on_page = time.time() - load_time
    if time_on_page < 1.5:
        return
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
