from pydoc import classname
from dash import Dash, dcc, html, Input, Output, callback_context
from dash.exceptions import PreventUpdate
import visdcc

import json
from make_network import GraphDisplay

network = GraphDisplay(n=2)
loading = True

external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Roboto",
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Wikipedia-dia'

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
                                'physics':{
                                    'repulsion':{
                                        'nodeDistance': 150,
                                        'springLength': 10,
                                    },
                                    'solver':'repulsion',
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
                    html.Button('Add Starting Node', id='add-one', n_clicks=0, className='button add-button'),
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
                "*Adding 5 or 10 nodes at a time may be slow.",
                style={'margin-left':'10px'}
            )
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
                figure= network.cycle_lens_histogram(),
                config={'displayModeBar': False},
            )
        ], className='right-div')
    ], className='content-columns'),
], className='body-fade-in')

@app.callback(
    [Output('net', 'data'),
    Output('cycles-vs-total', 'children'),
    Output('cycle-histogram', 'figure')],
    [Input('add-one', 'n_clicks'),
    Input('node-num-selector', 'value'),
    Input('change-n', 'value'),
    Input('reset-network', 'n_clicks')])
def update_network(clicks, num_nodes, link_num, reset_num):
    active_id = [p['prop_id'] for p in callback_context.triggered]

    if 'add-one.n_clicks' in active_id:
        for _ in range(num_nodes):
            network.add_graph()
    elif 'change-n.value' in active_id:
        network.change_n(link_num)
    elif 'reset-network.n_clicks' in active_id:
        network.reset_graph(num=1)
    elif '.' in active_id:
        network.reset_graph()
    else:
        raise PreventUpdate
    
    data = network.output_graph()

    cycle_lens, _ = network.cycle_lens()

    cycle_len_string = f'There are a total of {len(network.graph)} node{"s" if len(network.graph)!=1 else ""}, \
        of which {sum(cycle_lens)} are in {len(cycle_lens)} cycle{"s" if len(cycle_lens)!=1 else ""}.'
    return data, cycle_len_string, network.cycle_lens_histogram()


if __name__ == '__main__':
    app.run_server(debug=True)
