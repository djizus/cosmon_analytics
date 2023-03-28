import dash, pymongo, decimal
from datetime import datetime, timedelta
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, update_title=None, external_stylesheets=external_stylesheets,
                meta_tags=[{'name': 'Cache-control', 'content': 'no-cache, no-store, must-revalidate'},
                           {'name': 'Pragma', 'content': 'no-cache'}, {'name': 'Expires', 'content': '0'}])

server = app.server
app.title = "Cosmon Analytics"

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': 'rgb(31, 33, 34)',
    'color': 'white'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': 'rgb(24, 26, 27)',
    'color': '#079A82'
}

tooltip_style = {
    'backgroundColor': 'rgb(31, 33, 34)',
    'color': 'white',
    'width': '10%',
    'border': '1px solid #d6d6d6',
}

# database setup
connectionstring = #magic_sauce#
mongoClient = pymongo.MongoClient(connectionstring)
db = mongoClient["Cosmon"]
leaderCol = db["leaders"]
walletListCol = db["walletList"]
walletDataCol = db["walletLeagueData"]
walletBoostCol = db["walletBoosts"]
leaderboardCol = db["leaderboard"]
rankByLeadersCol = db["rankByLeaders"]
rankByPersonnalityCol = db["rankByPersonnality"]
wallet = ""

currentDateTime = datetime.now()
leagueDebutDate = currentDateTime - timedelta(days=currentDateTime.weekday())
if (currentDateTime - leagueDebutDate).days == 0:
    if (currentDateTime - currentDateTime.replace(hour=16, minute=0, second=0, microsecond=0)).total_seconds() > 0:
        leagueDebutDate = currentDateTime.replace(hour=16, minute=0, second=0, microsecond=0)
    else:
        tmpCurrentDateTime = currentDateTime - timedelta(days=1)
        leagueDebutDate = tmpCurrentDateTime - timedelta(days=tmpCurrentDateTime.weekday())

leagueDebutDate = leagueDebutDate.replace(hour=16, minute=0, second=0, microsecond=0)
leagueDebutDate = leagueDebutDate.strftime("%Y-%m-%dT%H:%M")

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="⚔️", className="header-emoji"),
                html.H1(
                    children="Cosmon analytics", className="header-title"
                ),
                html.P(
                    children="Analyze your performance during the current cosmon league",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        # Hide this div, this is where we get the wallet data from the JS script
                        html.Div(id='wallet-output', hidden=True),
                        html.Div(id='wallet-div', children="Wallet", className="menu-title"),
                        html.Div(id="wallet"),
                        html.Button('Refresh data', id='get-data', n_clicks=0, className="buttons"),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Number of fights", className="menu-title"),
                        dcc.Loading(
                            id="loading-nb",
                            children=[html.Div(id="number-output")],
                            type="default",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Global winrate", className="menu-title"),
                        dcc.Loading(
                            id="loading-winrate",
                            children=[html.Div(id="global-winrate-output")],
                            type="default",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Rank", className="menu-title"
                        ),
                        dcc.Loading(
                            id="loading-rank",
                            children=[html.Div(id="rank-output")],
                            type="default",
                        ),
                    ]
                ),
                html.Div(
                    id="xki-performance-div",
                    children=[
                        html.Div(
                            children="Performance in $XKI", className="menu-title"
                        ),
                        dcc.Loading(
                            id="loading-xki",
                            children=[html.Div(id="xki-performance-output")],
                            type="default",
                        ),
                        dbc.Tooltip(
                            "Ranking: +0 xki "
                            "Instant: +0 xki "
                            "Registration: -0 xki "
                            "Arena fees: -0 xki "
                            "Training fees: -0 xki "
                            "Boosts : -0 xki ",
                            id="tooltip-xki",
                            target="xki-performance-div",
                            style=tooltip_style,
                            placement="bottom",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Get data since (UTC)",
                            className="menu-title"
                        ),
                        dbc.Input(
                            id="date-time",
                            type="datetime-local",
                            min=leagueDebutDate,
                            max=currentDateTime,
                            value=leagueDebutDate,
                            style={
                                'border-color': '#736b5e',
                                'color': '#e8e6e3',
                                'background-color': 'rgb(26, 28, 29)',
                                'width': '100%'
                            }
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        dcc.Tabs(id="tabs-data", parent_className='custom-tabs', className='custom-tabs-container', children=[
            dcc.Tab(label='Arena Data', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div(
                    children=[
                        dcc.Loading(
                            id="loading-table-arena",
                            children=[
                                dash_table.DataTable(
                                    id='table-output-arena',
                                    data=[],
                                    sort_action="native",
                                    filter_action='native',
                                    sort_mode="multi",
                                    column_selectable="single",
                                    cell_selectable=False,
                                    row_deletable=True,
                                    style_header={
                                        'backgroundColor': 'rgb(26, 28, 29)',
                                        'color': '#079A82',
                                        'border': '0.5px solid gray',
                                    },
                                    style_data={
                                        'backgroundColor': 'rgb(36, 38, 39)',
                                        'color': '#e8e6e3',
                                        'border': '0.5px solid gray',
                                    },
                                    style_filter={
                                        'backgroundColor': 'rgb(36, 38, 39)',
                                        'color': '#e8e6e3',
                                        'border': '0.5px solid gray',
                                    },
                                ),
                            ],
                            type="default",
                        )
                    ],
                    className="wrapper",
                ),
            ]),
            dcc.Tab(label='Training Data', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div(
                    children=[
                        dcc.Loading(
                            id="loading-table-training",
                            children=[
                                dash_table.DataTable(
                                    id='table-output-training',
                                    data=[],
                                    sort_action="native",
                                    filter_action='native',
                                    sort_mode="multi",
                                    column_selectable="single",
                                    cell_selectable=False,
                                    style_header={
                                        'backgroundColor': 'rgb(26, 28, 29)',
                                        'color': '#079A82',
                                        'border': '0.5px solid gray',
                                    },
                                    style_data={
                                        'backgroundColor': 'rgb(36, 38, 39)',
                                        'color': '#e8e6e3',
                                        'border': '0.5px solid gray',
                                    },
                                    style_filter={
                                        'backgroundColor': 'rgb(36, 38, 39)',
                                        'color': '#e8e6e3',
                                        'border': '0.5px solid gray',
                                    },
                                ),
                            ],
                            type="default",
                        )
                    ],
                    className="wrapper",
                ),
            ]),
            dcc.Tab(label='Leaderboard', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div(
                    children=[
                        dcc.Loading(
                            id="loading-table-leaderboard",
                            children=[
                                dash_table.DataTable(
                                    id='table-output-leaderboard',
                                    data=[],
                                    sort_action="native",
                                    sort_mode="multi",
                                    column_selectable="single",
                                    cell_selectable=False,
                                    page_size=25,
                                    style_header={
                                        'backgroundColor': 'rgb(26, 28, 29)',
                                        'color': '#079A82',
                                        'border': '0.5px solid gray',
                                    },
                                    style_data={
                                        'backgroundColor': 'rgb(36, 38, 39)',
                                        'color': '#e8e6e3',
                                        'border': '0.5px solid gray',
                                    },
                                ),
                            ],
                            type="default",
                        )
                    ],
                    className="leaderboard",
                ),
            ]),
        ]),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div([
                            html.P(["\xA0\xA0\xA0\xA0Find me on :"], id='find-me-on'),
                            html.A([html.Img(src=app.get_asset_url('githubLogo.png'), style={'height': '3rem'})],
                                   href="https://github.com/djizus/cosmon_analytics"),
                            html.A([html.Img(src=app.get_asset_url('twitterLogo.png'), style={'height': '3rem'})],
                                   href="https://twitter.com/letaljc")
                        ], id='footer-links'),
                        html.P("If you like my work, you can donate @ ki1txqg3z8f0tj02z88afw2f9q8qfl54gpl238vt6"),
                        html.P("Cosmon analytics is not affiliated with Cosmon\xA0\xA0\xA0"),
                    ],
                    className="footer",
                ),
            ]),
    ])

app.clientside_callback(
    """
    function(n_clicks) {
        return document.getElementById("wallet").innerHTML;
    }
    """,
    Output('wallet-output', 'children'),
    Input('get-data', 'n_clicks'),
)


@app.callback(
    Output("tooltip-xki", "children"),
    Input("tooltip-xki", "is_open"),
    Input('wallet-output', 'children'),
)
def toggle_tooltip(is_open, children):
    registration = 0
    arena = 0
    training = 0
    boosts = 0
    reward = 0
    instant = 0
    if is_open:
        if walletDataCol.count_documents({"$and": [{'wallet': children}, {'arena': "League 1"}]}) > 0:
            registration = 10
            arena = list(walletDataCol.aggregate([{"$match": {"$and": [{'wallet': children}, {'arena': "League 1"}]}},
                                                  {"$group": {"_id": "null", "totalAmount": {"$sum": "$xkiSpent"}}}]))
            arena = "{:.5}".format(round(arena[0]["totalAmount"] / 1000000, 4))
            reward = "{:.5}".format(leaderboardCol.find_one({'wallet': children}, {'_id': False})["reward"])
            instant = list(walletDataCol.aggregate([{"$match": {"$and": [{'wallet': children}, {'arena': "League 1"}]}},
                                                    {"$group": {"_id": "null", "totalAmount": {"$sum": "$xkiWon"}}}]))
            instant = "{:.5}".format(round(instant[0]["totalAmount"] / 1000000, 4))

        if walletDataCol.count_documents({"$and": [{'wallet': children}, {'arena': "Training"}]}) > 0:
            training = list(walletDataCol.aggregate(
                [{"$match": {"$and": [{'wallet': children}, {'arena': "Training"}]}},
                 {"$group": {"_id": "null", "totalAmount": {"$sum": "$xkiSpent"}}}]))
            training = "{:.5}".format(round(training[0]["totalAmount"] / 1000000, 4))

        if walletBoostCol.count_documents({'wallet': children}) > 0:
            boosts = list(walletBoostCol.aggregate(
                [{"$match": {'wallet': children}}, {"$group": {"_id": "null", "totalAmount": {"$sum": "$xkiSpent"}}}]))
            boosts = "{:.5}".format(round(boosts[0]["totalAmount"] / 1000000, 4))

        detailed_fees = "Reward: +" + str(reward) + " xki " + "Instant: +" + str(
            instant) + " xki " + "Registration: -" + str(registration) + " xki " + "Arena fees: -" + str(
            arena) + " xki " + "Training fees: -" + str(training) + " xki " + "Boosts : -" + str(boosts) + " xki "
        return detailed_fees


@app.callback(
    Output("table-output-arena", "data"), Output('table-output-arena', 'columns'),
    Output("table-output-training", "data"), Output('table-output-training', 'columns'),
    Output("table-output-leaderboard", "data"), Output('table-output-leaderboard', 'columns'),
    Output('table-output-leaderboard', 'style_data_conditional'),
    Output("number-output", "children"),
    Output("global-winrate-output", "children"),
    Output("xki-performance-output", "children"),
    Output("rank-output", "children"),
    Input('wallet-output', 'children'),
    Input("date-time", "value"),
)
def update_output(children, date):
    data_arena = []
    columns_arena = []
    data_training = []
    columns_training = []
    data_leaderboard = []
    columns_leaderboard = []
    style_data_conditional = []
    number_fights_league = 0
    winrate = 0
    xki_str = 0
    rank = 0
    xki_reward = 0.0
    if len(children) == 0:
        return (data_arena, columns_arena, data_training, columns_training, data_leaderboard, columns_leaderboard,
                style_data_conditional, number_fights_league, winrate, xki_str, rank)
    if walletListCol.count_documents({'wallet': children}, limit=1) == 0:
        walletListCol.insert_one({'wallet': children})
        return (data_arena, columns_arena, data_training, columns_training, data_leaderboard, columns_leaderboard,
                style_data_conditional, "Your wallet has been added to our database.",
                "Press the get data button to show your stats !", xki_str, rank)
    else:
        date = datetime.strptime(date, '%Y-%m-%dT%H:%M')
        number_fights_league = walletDataCol.count_documents(
            {"$and": [{'wallet': children}, {'arena': "League 1"}, {'txDate': {'$gte': date}}]})
        if number_fights_league > 0:
            df = pd.DataFrame(list(
                walletDataCol.find({"$and": [{'wallet': children}, {'arena': "League 1"}, {'txDate': {'$gte': date}}]},
                                   {'_id': 0})))
            # get number of fights in league
            df_count = df.groupby(
                ['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id']).size().reset_index(name='Fights')
            # get wins/draws/losses
            df_winner = df[df['winner'] == 2]
            df_winner = df_winner.groupby(
                ['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id']).size().reset_index(name='Won')
            df_draw = df[df['winner'] == 0]
            df_draw = df_draw.groupby(
                ['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id']).size().reset_index(name='Drawn')
            df_lost = df[df['winner'] == -1]
            df_lost = df_lost.groupby(
                ['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id']).size().reset_index(name='Lost')
            # merge to get the winrate
            df_output = df_count.merge(df_winner, on=['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'],
                                       how='outer').fillna(0)
            df_output = df_output.merge(df_draw, on=['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'],
                                        how='outer').fillna(0)
            df_output = df_output.merge(df_lost, on=['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'],
                                        how='outer').fillna(0)
            df_output["Winrate"] = df_output["Won"] / df_output["Fights"]
            # drop duplicates
            df_output = df_output.merge(
                df.drop_duplicates(['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'], keep='last'),
                how='left', on=['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'])
            # get points scored per deck
            df_output["Points"] = df_output["Won"] * 2 + df_output["Lost"] * -1
            # get deck rank
            df_rankL = pd.DataFrame(list(rankByLeadersCol.find({}, {'_id': 0, 'winner_sum': 0, 'winner_average': 0,
                                                                    'fight_number': 0, 'rank': 0})))
            df_output = df_output.merge(df_rankL,
                                        on=['my_cosmon_1_nft_name', 'my_cosmon_2_nft_name', 'my_cosmon_3_nft_name'],
                                        how='left').fillna(0)
            # format the dataframe
            df_output = df_output.rename(
                columns={'my_cosmon_1_nft_name': 'Cosmon #1', 'my_cosmon_2_nft_name': 'Cosmon #2',
                         'my_cosmon_3_nft_name': 'Cosmon #3', 'my_cosmon_1_lvl': 'Level #1',
                         'my_cosmon_2_lvl': 'Level #2', 'my_cosmon_3_lvl': 'Level #3', 'my_deck_score': 'Deck Score',
                         'stars': 'Deck Rating'})
            df_output = df_output[
                ['Fights', 'Won', 'Drawn', 'Lost', 'Winrate', 'Points', 'Cosmon #1', 'Level #1', 'Cosmon #2',
                 'Level #2', 'Cosmon #3', 'Level #3', 'Deck Score', 'Deck Rating']]
            df_output = df_output.sort_values(by='Winrate', ascending=False)
            # get global winrate
            winrate = "{:.2%}".format(df_output["Won"].sum() / df_output["Fights"].sum())
            df_output["Winrate"] = df_output["Winrate"].astype(float).map("{:.2%}".format)
            # output data
            data_arena = df_output.to_dict(orient='records')
            columns_arena = [{'name': col, 'id': col} for col in df_output.columns]

        number_fights_training = walletDataCol.count_documents(
            {"$and": [{'wallet': children}, {'arena': "Training"}, {'txDate': {'$gte': date}}]})
        if number_fights_training > 0:
            df = pd.DataFrame(list(
                walletDataCol.find({"$and": [{'wallet': children}, {'arena': "Training"}, {'txDate': {'$gte': date}}]},
                                   {'_id': 0})))
            # get number of fights in league
            df_count = df.groupby(
                ['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id']).size().reset_index(name='Fights')
            # get wins/draws/losses
            df_winner = df[df['winner'] == 2]
            df_winner = df_winner.groupby(
                ['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id']).size().reset_index(name='Won')
            df_draw = df[df['winner'] == 0]
            df_draw = df_draw.groupby(
                ['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id']).size().reset_index(name='Drawn')
            df_lost = df[df['winner'] == -1]
            df_lost = df_lost.groupby(
                ['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id']).size().reset_index(name='Lost')
            # merge to get the winrate
            df_output = df_count.merge(df_winner, on=['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'],
                                       how='outer').fillna(0)
            df_output = df_output.merge(df_draw, on=['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'],
                                        how='outer').fillna(0)
            df_output = df_output.merge(df_lost, on=['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'],
                                        how='outer').fillna(0)
            df_output["Winrate"] = df_output["Won"] / df_output["Fights"]
            # drop duplicates
            df_output = df_output.merge(
                df.drop_duplicates(['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'], keep='last'),
                how='left', on=['my_cosmon_1_nft_id', 'my_cosmon_2_nft_id', 'my_cosmon_3_nft_id'])
            # get points scored per deck
            df_output["Points"] = df_output["Won"] * 2 + df_output["Lost"] * -1
            # get deck rank
            df_rankL = pd.DataFrame(list(rankByLeadersCol.find({}, {'_id': 0, 'winner_sum': 0, 'winner_average': 0,
                                                                    'fight_number': 0, 'rank': 0})))
            df_output = df_output.merge(df_rankL,
                                        on=['my_cosmon_1_nft_name', 'my_cosmon_2_nft_name', 'my_cosmon_3_nft_name'],
                                        how='left').fillna(0)
            # format the dataframe
            df_output = df_output.rename(
                columns={'my_cosmon_1_nft_name': 'Cosmon #1', 'my_cosmon_2_nft_name': 'Cosmon #2',
                         'my_cosmon_3_nft_name': 'Cosmon #3', 'my_cosmon_1_lvl': 'Level #1',
                         'my_cosmon_2_lvl': 'Level #2', 'my_cosmon_3_lvl': 'Level #3', 'my_deck_score': 'Deck Score',
                         'stars': 'Deck Rating'})
            df_output = df_output[
                ['Fights', 'Won', 'Drawn', 'Lost', 'Winrate', 'Points', 'Cosmon #1', 'Level #1', 'Cosmon #2',
                 'Level #2', 'Cosmon #3', 'Level #3', 'Deck Score', 'Deck Rating']]
            df_output = df_output.sort_values(by='Winrate', ascending=False)
            # get global winrate
            df_output["Winrate"] = df_output["Winrate"].astype(float).map("{:.2%}".format)
            # output data
            data_training = df_output.to_dict(orient='records')
            columns_training = [{'name': col, 'id': col} for col in df_output.columns]

        # get leaderboard
        df = pd.DataFrame(list(leaderboardCol.find({}, {'_id': 0})))
        df_output = df.rename(
            columns={'wallet': 'Wallet', 'points': 'Score', 'rank': 'Rank', 'reward': '$XKI Reward', 'fights': 'Fights',
                     'won': 'Won', 'drawn': 'Drawn', 'lost': 'Lost', 'winrate': 'Winrate', 'boostNumber': 'Boosts used',
                     'xkiWon': '$XKI Won'})
        df_output = df_output[
            ['Rank', 'Wallet', 'Fights', 'Won', 'Drawn', 'Lost', 'Score', 'Winrate', 'Boosts used', '$XKI Won',
             '$XKI Reward']]
        df_output = df_output.sort_values(by='Rank', ascending=True)

        data_leaderboard = df_output.to_dict(orient='records')
        columns_leaderboard = [{'name': col, 'id': col} for col in df_output.columns]

        # highlight wallet in leaderboad
        style_data_conditional = [
            {
                'if': {
                    'filter_query': '{Wallet} eq "' + children + '"'
                },
                'backgroundColor': '#079A82'
            },
        ]

        # get rank
        if leaderboardCol.count_documents({'wallet': children}) > 0:
            rank = leaderboardCol.find_one({'wallet': children}, {'_id': 0})["rank"]
            number_players = leaderboardCol.count_documents({})
            rank = str(int(rank)) + "/" + str(number_players)
            # get reward
            xki_reward = leaderboardCol.find_one({'wallet': children}, {'_id': 0})["reward"]

        # get xki performance overall
        xki_spent = 0
        xki_won = 0
        if walletDataCol.count_documents({"$and": [{'wallet': children}, {'arena': "League 1"}]}) > 0:
            xki_spent = 10
            xki_spent_wallet = list(walletDataCol.aggregate(
                [{"$match": {'wallet': children}}, {"$group": {"_id": "null", "totalAmount": {"$sum": "$xkiSpent"}}}]))
            xki_spent = xki_spent + round(xki_spent_wallet[0]["totalAmount"] / 1000000, 4)
            xki_won = list(walletDataCol.aggregate([{"$match": {"$and": [{'wallet': children}, {'arena': "League 1"}]}},
                                                    {"$group": {"_id": "null", "totalAmount": {"$sum": "$xkiWon"}}}]))
            xki_won = round(xki_won[0]["totalAmount"] / 1000000, 4)

        if walletBoostCol.count_documents({'wallet': children}) > 0:
            boosts = list(walletBoostCol.aggregate(
                [{"$match": {'wallet': children}}, {"$group": {"_id": "null", "totalAmount": {"$sum": "$xkiSpent"}}}]))
            xki_spent = xki_spent + round(boosts[0]["totalAmount"] / 1000000, 4)

        xki_str = "{:.7}".format(xki_reward + xki_won - xki_spent) + " xki"

        return (data_arena, columns_arena, data_training, columns_training, data_leaderboard, columns_leaderboard,
                style_data_conditional, number_fights_league, winrate, xki_str, rank)


if __name__ == "__main__":
    app.run_server(debug=True)
