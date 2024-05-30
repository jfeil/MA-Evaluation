from collections import defaultdict

import dash
import pandas as pd
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from sqlalchemy.orm import Session

from src.database import engine, DefinitionGenerator, UserResponse, Definition

dash.register_page(__name__)


def generator_name(gen: DefinitionGenerator):
    return f"{gen.type}: {gen.name}"


with Session(engine) as sess:
    generator_list = sess.query(DefinitionGenerator).all()
    generators = {g: {g: ([], []) for g in generator_list} for g in generator_list}
    users = defaultdict(lambda: 0)

    name_to_generator = {generator_name(g): g for g in generator_list}

    user_responses = sess.query(UserResponse).all()
    for resp in user_responses:
        users[str(resp.session.hex)] += 1
        winner = sess.get(Definition, resp.winner).generator
        loser = sess.get(Definition, resp.loser).generator

        generators[winner][loser][0].append(resp.id)
        generators[loser][winner][1].append(resp.id)

layout = dbc.Container([
    html.H4('Generator comparison'),
    dcc.Dropdown(
        id="dropdown",
        options=list(name_to_generator.keys()),
        value=list(name_to_generator.keys())[0],
        clearable=False, className='dbc'
    ),
    dcc.Graph(id="generator-graph"),
    html.Br(),
    html.H4('User comparison'),
    dcc.Graph(id="user-graph", figure=px.histogram(pd.DataFrame(data=list(users.items()), columns=["User", "Amount"]), x="User", y="Amount", barmode='group', height=400)),
])


@callback(
    Output("generator-graph", "figure"),
    Input("dropdown", "value"))
def update_bar_chart(gen):
    cur_gen = dict(generators[name_to_generator[gen]])
    cur_gen.pop(name_to_generator[gen])
    test = []
    for key, value in cur_gen.items():
        test.append([len(value[0]), "Winner", generator_name(key)])
        test.append([len(value[1]), "Loser", generator_name(key)])
    df = pd.DataFrame(data=test, columns=["Amount", "Comparison", "Generator"])
    fig = px.histogram(df, x="Generator", y="Amount",
                       color='Comparison', barmode='group',
                       height=400)
    return fig
