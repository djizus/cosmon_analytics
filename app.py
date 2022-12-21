import dash, pymongo
from datetime import datetime, timedelta
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, meta_tags=[{'name': 'Cache-control', 'content': 'no-cache, no-store, must-revalidate'}, {'name': 'Pragma', 'content': 'no-cache'}, {'name': 'Expires', 'content': '0'}])

server = app.server
app.title = "Cosmon Data"

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

#database setup
connectionstring = #magic sauce#
mongoClient = pymongo.MongoClient(connectionstring)
db = mongoClient["Cosmon"]
leaderCol = db["leaders"]
walletListCol = db["walletList"]
walletDataCol = db["walletLeagueData"]
lastExecutionCol = db["lastExecution"]
wallet = ""

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
                        #Hide this div, this is where we get the wallet data from the JS script
                        html.Div(id = 'wallet-output', className="hidden-div"),
                        html.Div(id = 'wallet-div', children="Wallet", className="menu-title"),
                        html.Div(id="wallet"),
                        html.Button('Refresh data', id='get-data', n_clicks=0, className = "buttons"),
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
                            children="Total $XKI spent", className="menu-title"
                        ),
                        dcc.Loading(
                            id="loading-xki",
                            children=[html.Div(id="xki-spent-output")],
                            type="default",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Last data fetched", className="menu-title"
                        ),
                        html.Div(
                            id="fetched-timestamp",
                        ),
                        dcc.Interval(
                            id='interval-component',
                            interval=150*1000, # in milliseconds
                            n_intervals=0
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        dcc.Tabs(id="tabs-data",  parent_className='custom-tabs', className='custom-tabs-container', children=[
            dcc.Tab(label='Arena Data', style=tab_style, selected_style=tab_selected_style, children=[
                html.Div(
                    children=[
                        dcc.Loading(
                            id="loading-table-arena",
                            children=[
                                    dash_table.DataTable(
                                        id='table-output-arena', 
                                        data=[],
                                        filter_action="native",
                                        sort_action="native",
                                        sort_mode="multi",
                                        column_selectable="single",
                                        cell_selectable=False,
                                        style_header={
                                            'backgroundColor': 'rgb(26, 28, 29)',
                                            'color': '#e8e6e3',
                                            },
                                        style_data={
                                            'backgroundColor': 'rgb(26, 28, 29)',
                                            'color': '#e8e6e3',
                                            },
                                        style_filter={
                                            'backgroundColor': 'rgb(26, 28, 29)',
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
                                        filter_action="native",
                                        sort_action="native",
                                        sort_mode="multi",
                                        column_selectable="single",
                                        cell_selectable=False,
                                        style_header={
                                            'backgroundColor': 'rgb(26, 28, 29)',
                                            'color': '#e8e6e3',
                                            },
                                        style_data={
                                            'backgroundColor': 'rgb(26, 28, 29)',
                                            'color': '#e8e6e3',
                                            },
                                        style_filter={
                                            'backgroundColor': 'rgb(26, 28, 29)',
                                            },
                                        ),
                                    ],
                            type="default",
                        )
                    ],
                    className="wrapper",
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
                                   href="https://github.com/djizus/"),
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
    Output('fetched-timestamp', 'children'),
    Input('interval-component', 'n_intervals'))
def update_timestamp(n):
    lastTimestamp = lastExecutionCol.find_one({}, {'_id': False})["date"]
    minutes = datetime.now() - lastTimestamp
    minutes = divmod(minutes.seconds, 60)
    delta = minutes[0], " minutes and ", minutes[1], "s ago"
    return delta

@app.callback(
    Output("table-output-arena", "data"), Output('table-output-arena', 'columns'),
    Output("table-output-training", "data"), Output('table-output-training', 'columns'),
    Output("number-output", "children"),
    Output("global-winrate-output", "children"),
    Output("xki-spent-output", "children"),
    Input('wallet-output', 'children'),
)
def update_output(children):
    data_arena = []
    columns_arena = []
    data_training = []
    columns_training = []
    number_fights_league = 0
    winrate = 0
    xki_str = 0
    if len(children) == 0:
        return (data_arena, columns_arena, data_training, columns_training, number_fights_league, winrate, xki_str)
    if walletListCol.count_documents({'wallet': children}, limit = 1) == 0 :
        walletListCol.insert_one({'wallet' : children})
        return (data_arena, columns_arena, data_training, columns_training, "Your wallet has been added to our database.", "Press the get data button on the next data refresh to show your stats !", xki_str)
    else : 
        number_fights_league = walletDataCol.count_documents({"$and": [{'wallet': children},{'arena': "League 1"}]})
        if number_fights_league > 0 :
            df = pd.DataFrame(list(walletDataCol.find({"$and": [{'wallet': children},{'arena': "League 1"}]}, {'_id': 0, 'my_deck_id': 1, 'my_deck_score':1, 'my_deck_score_bonus':1,'score_diff':1,'my_cosmon_1_nft_name': 1, 'my_cosmon_1_lvl' :1,'my_cosmon_2_nft_name': 1, 'my_cosmon_2_lvl' :1,'my_cosmon_3_nft_name': 1, 'my_cosmon_3_lvl' :1, 'winner': 1})))
            #get number of fights in league
            df_count = df.groupby(['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name']).size().reset_index(name='Fights')
            #get wins
            df_winner= df[df['winner'] == 2]
            df_winner = df_winner.groupby(['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name']).size().reset_index(name='Wins')
            #merge to get the winrate
            df_output = df_count.merge(df_winner, on=['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name'], how='outer').fillna(0)
            df_output["Winrate"] = df_output["Wins"] / df_output["Fights"]
            df_output = df_output.merge(df.drop_duplicates(['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name'], keep='last'),how='left',on=['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name'])
            #format the dataframe
            df_output = df_output.rename(columns={'my_deck_id': 'DeckId', 'my_cosmon_1_nft_name': 'Cosmon #1', 'my_cosmon_2_nft_name': 'Cosmon #2', 'my_cosmon_3_nft_name': 'Cosmon #3', 'my_cosmon_1_lvl': 'Level #1', 'my_cosmon_2_lvl': 'Level #2', 'my_cosmon_3_lvl': 'Level #3'})
            df_output = df_output[['DeckId', 'Fights', 'Wins', 'Winrate','Cosmon #1','Level #1','Cosmon #2','Level #2','Cosmon #3','Level #3']]
            df_output = df_output.sort_values(by='Winrate', ascending=False)
            #get global winrate
            winrate = "{:.2%}".format(df_output["Wins"].sum() / df_output["Fights"].sum())
            df_output["Winrate"] = df_output["Winrate"].astype(float).map("{:.2%}".format)     
            
            columns_arena = [{'name': col, 'id': col} for col in df_output.columns]
            data_arena = df_output.to_dict(orient='records')
            
        number_fights_training = walletDataCol.count_documents({"$and": [{'wallet': children},{'arena': "Training"}]})
        
        if number_fights_training > 0 :
            df = pd.DataFrame(list(walletDataCol.find({"$and": [{'wallet': children},{'arena': "Training"}]}, {'_id': 0, 'my_deck_id': 1, 'my_deck_score':1, 'my_deck_score_bonus':1,'score_diff':1,'my_cosmon_1_nft_name': 1, 'my_cosmon_1_lvl' :1,'my_cosmon_2_nft_name': 1, 'my_cosmon_2_lvl' :1,'my_cosmon_3_nft_name': 1, 'my_cosmon_3_lvl' :1, 'winner': 1})))
            #get number of fights in league
            df_count = df.groupby(['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name']).size().reset_index(name='Fights')
            #get wins
            df_winner= df[df['winner'] == 2]
            df_winner = df_winner.groupby(['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name']).size().reset_index(name='Wins')
            #merge to get the winrate
            df_output = df_count.merge(df_winner, on=['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name'], how='outer').fillna(0)
            df_output["Winrate"] = df_output["Wins"] / df_output["Fights"]
            df_output = df_output.merge(df.drop_duplicates(['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name'], keep='last'),how='left',on=['my_deck_id','my_cosmon_1_nft_name','my_cosmon_2_nft_name','my_cosmon_3_nft_name'])
            #format the dataframe
            df_output = df_output.rename(columns={'my_deck_id': 'DeckId', 'my_cosmon_1_nft_name': 'Cosmon #1', 'my_cosmon_2_nft_name': 'Cosmon #2', 'my_cosmon_3_nft_name': 'Cosmon #3', 'my_cosmon_1_lvl': 'Level #1', 'my_cosmon_2_lvl': 'Level #2', 'my_cosmon_3_lvl': 'Level #3'})
            df_output = df_output[['DeckId', 'Fights', 'Wins', 'Winrate','Cosmon #1','Level #1','Cosmon #2','Level #2','Cosmon #3','Level #3']]
            df_output = df_output.sort_values(by='Winrate', ascending=False)            
            df_output["Winrate"] = df_output["Winrate"].astype(float).map("{:.2%}".format)
            
            columns_training = [{'name': col, 'id': col} for col in df_output.columns]
            data_training = df_output.to_dict(orient='records')
        
        #get money spent overall
        xki_spent = list(walletDataCol.aggregate([{"$match": {'wallet': children}},{"$group": {"_id": "null","totalAmount": {"$sum": "$xkiSpent"}}}]))
        xki_str = "{:.7}".format(10 + round(xki_spent[0]["totalAmount"] / 1000000,4)) + " xki"
        
        return (data_arena, columns_arena, data_training, columns_training, number_fights_league, winrate, xki_str)

if __name__ == "__main__":
    app.run_server(debug=True)
