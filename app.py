from pydoc import classname
from dash import Dash, dcc, html, Input, Output
import visdcc

import json
from make_network import GraphDisplay

network = GraphDisplay()
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
            className='header-title fade-in'
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
                                        'springLength': 20,
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
                    type='dot'
                ),
                className='network-div'
            ),
            html.Button('Add 1 Origin', id='add-one', n_clicks=0, className='add-button')
        ], className='left-div'),
        html.Div([
            html.H2(
                "Some Random Things",
                className='info-title'
            ),
        ])
    ], className='content-columns'),
])

@app.callback(
    Output('net', 'data'),
    [Input('add-one', 'n_clicks')])
def update_network(clicks):
    if clicks==0:
        network.reset_graph(num=3)
    else:
        network.add_graph()

    data = network.output_graph()
    return data


if __name__ == '__main__':
    app.run_server(debug=True)
