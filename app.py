from pydoc import classname
from dash import Dash, dcc, html, Input, Output, callback_context, no_update
import visdcc

import json
import os

from make_network import GraphDisplay, empty_histogram

with open('./assets/conclusions.txt', 'r') as f:
    conclusions = f.read().split('\n\nNEWNUMBER\n\n')

with open('./assets/explanation.txt', 'r') as f:
    explanation_text = f.read()

external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Roboto",
]


app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Wikipedia-dia'

server = app.server

app.layout = html.Div([
    html.Div([
        html.H1(
            "Wikipedia-dia",
            className='header-title title-fade-in'
        )
    ], className='header-box'
    ),
    html.Div([
        html.Div([
            html.Div(
                dcc.Loading(
                    id='loading',
                    children=[
                        visdcc.Network(
                            id='net',
                            data={'nodes':[],'edges':[]},
                            options={
                                'clickToUse': True,
                                'physics':{
                                    'repulsion':{
                                        'nodeDistance': 150,
                                        'springLength': 50,
                                        'springConstant': 0.25,
                                    },
                                    'solver':'repulsion',
                                    'timestep': 1,
                                },
                                'edges':{
                                    'arrows':'to',
                                }
                            },
                            style={
                                'height':'100%',
                                'borderColor':'#000',
                                'borderStyle':'solid',
                            }
                        ),
                    ],
                    type='default'
                ),
                className='network-div'
            ),
            html.Div([
                html.Div([
                    html.Button('Add Starting Page', id='add-one', n_clicks=0, className='button add-button'),
                    dcc.RadioItems([1,5,10], value=1, id='node-num-selector', labelStyle={'margin-right':'10px'})
                ], className='button-box'),
                html.Div([
                    "Wikipedia-dia is clicking link number:",
                    dcc.Input(
                        value=2, type='number', min=1, step=1,
                        id='change-n', debounce=True, className='numeric-input',
                    )
                ], style={'height':'40px', 'align-items':'center', 'display':'flex'}),
                html.Button('Reset Network', id='reset-network', n_clicks=0, className='button reset-button')
            ], className='inputs-div'),
            html.Div(
                "*Adding 5 or 10 nodes at a time may be slow.\n*Do not change the number of added nodes while loading. It can break the network.",
                className='warnings-box'
            ),
            html.Div([
                html.H3(
                    "Explanation of Wikipedia-dia:"
                ),
                html.Div(
                    explanation_text,
                    style={'whiteSpace': 'pre-wrap'}
                )
            ], className='network-explanation')
        ], className='left-div'),
        html.Div([
            html.H2(
                "Some Random Things",
                className='info-title'
            ),
            html.Div(
                children="",
                id='cycles-vs-total'
            ),
            dcc.Graph(
                id='cycle-histogram',
                figure= empty_histogram,
                config={'displayModeBar': False},
            ),
            html.Div(id='conclusions', className='conclusions')
        ], className='right-div')
    ], className='content-columns'),
    dcc.Store(data = False, id='cached-graph')
], className='body-fade-in')

@app.callback(
    [Output('net', 'data'),
    Output('cycles-vs-total', 'children'),
    Output('cycle-histogram', 'figure'),
    Output('conclusions', 'children'),
    Output('cached-graph', 'data')],
    [Input('add-one', 'n_clicks'),
    Input('node-num-selector', 'value'),
    Input('change-n', 'value'),
    Input('reset-network', 'n_clicks'),
    Input('cached-graph', 'data')])
def update_network(add_one_clicks, num_nodes, link_num, reset_clicks, cached_data):
    active_id = [p['prop_id'] for p in callback_context.triggered]

    value = min(link_num, 4) - 1
    text =  conclusions[value]

    if 'add-one.n_clicks' in active_id:
        network = GraphDisplay(n=link_num, cached_data=cached_data)
        for _ in range(num_nodes):
            network.add_graph()

    elif 'change-n.value' in active_id:
        network = GraphDisplay(n=link_num, cached_data=False)

    elif 'reset-network.n_clicks' in active_id:
        network = GraphDisplay(n=link_num, cached_data=False, starting_nodes=1)

    elif '.' in active_id:
        network = GraphDisplay(n=link_num, cached_data=False)

    else:
        return no_update, no_update, no_update, text, no_update
    
    data = network.output_graph()

    cycle_lens, _ = network.cycle_lens()

    cycle_len_string = f'There are a total of {len(network.graph)} node{"s" if len(network.graph)!=1 else ""}, \
        of which {sum(cycle_lens)} are in {len(cycle_lens)} cycle{"s" if len(cycle_lens)!=1 else ""}.'
    return data, cycle_len_string, network.cycle_lens_histogram(), text, network.return_cache()

if __name__ == '__main__':
    app.run(debug=True)