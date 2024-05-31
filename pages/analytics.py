from collections import defaultdict

import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
from sqlalchemy.orm import Session

from src.database import engine, DefinitionGenerator, UserResponse, Definition

dash.register_page(__name__)


layout = dbc.Container([
    dcc.Store(id='data', storage_type='memory'),
    dcc.Store(id='selection', storage_type='session'),
    html.H4('Generator comparison'),
    dcc.Dropdown(
        id="dropdown",
        clearable=False, className='dbc'
    ),
    dcc.Graph(id="generator-graph"),
    html.Br(),
    html.H4('User comparison'),
    dcc.Graph(id="user-graph"),
])


@callback(
    Output("dropdown", "options"),
    Output("dropdown", "value"),
    Output("user-graph", "figure"),
    Output("data", "data"),
    Input("url", "pathname"),
    State("selection", "data")
)
def change_text(_, selection_state):
    def generator_name(gen: DefinitionGenerator):
        return f"{gen.type}: {gen.name}"

    with Session(engine) as sess:
        generator_list = sess.query(DefinitionGenerator).all()
        generators = {g.id.hex: {g.id.hex: ([], []) for g in generator_list} for g in generator_list}
        users = defaultdict(lambda: [0, 0])

        name_to_generator = {generator_name(g): g.id.hex for g in generator_list}
        generator_to_name = {g.id.hex: generator_name(g) for g in generator_list}

        user_responses = sess.query(UserResponse).all()
        for resp in user_responses:
            winner = resp.winner  # type: int
            users[str(resp.session.hex)][winner] += 1

            result = (sess.get(Definition, resp.left).generator.id.hex, sess.get(Definition, resp.right).generator.id.hex)
            generators[result[winner]][result[1 - winner]][0].append(resp.id.hex)
            generators[result[1 - winner]][result[winner]][1].append(resp.id.hex)

    users_df = []
    for key, value in users.items():
        users_df.append([key, value[0], "Left"])
        users_df.append([key, value[1], "Right"])

    selection_list = list(name_to_generator.keys())
    if selection_state in selection_list:
        selection = selection_state
    else:
        selection = selection_list[0]

    return (selection_list,
            selection,
            px.histogram(
                pd.DataFrame(data=users_df, columns=["User", "Amount", "Selection"]),
                x="User", y="Amount", color='Selection', barmode='group', height=400),
            (generators, name_to_generator, generator_to_name)
            )


@callback(
    Output("generator-graph", "figure"),
    Output("selection", "data"),
    Input("data", "data"),
    Input("dropdown", "value"))
def update_bar_chart(data, gen):
    cur_gen = dict(data[0][data[1][gen]])
    cur_gen.pop(data[1][gen])
    test = []
    for key, value in cur_gen.items():
        test.append([len(value[0]), "Winner", data[2][key]])
        test.append([len(value[1]), "Loser", data[2][key]])
    df = pd.DataFrame(data=test, columns=["Amount", "Comparison", "Generator"])
    fig = px.histogram(df, x="Generator", y="Amount",
                       color='Comparison', barmode='group',
                       height=400)
    return fig, gen
