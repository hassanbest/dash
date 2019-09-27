import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from data_container import DataContainer
import dash_d3cloud
import plotly.express as px

import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

navbar = dbc.NavbarSimple(
    brand="Tweets Analysis Demo",
    brand_href="#",
    sticky="top",
)

obj_dc = DataContainer('twitter_small.csv')

x_dates, y_freq = obj_dc.tweets_by_date()
date_ranges = obj_dc.dates_range

date_mark = {i: date_ranges[i] for i in range(0, len(date_ranges))}


trace_1 = go.Scatter(x=x_dates, y=y_freq, name='date', line=dict(width=2, color='rgb(229, 151, 50)'))

layout = go.Layout(hovermode='closest',
                   xaxis={'title': 'Date'},
                   yaxis={'title': 'Tweets Frequency'}, margin={'t': 0})

fig = go.Figure(data=[trace_1], layout=layout)



# df_map= obj_dc.tweets_by_geo()
df_map = pd.read_csv('df_map.csv')


px.set_mapbox_access_token('pk.eyJ1IjoiZ2lsdHJhcG8iLCJhIjoiY2o4eWJyNzY4MXQ1ZDJ3b2JsZHZxb3N0ciJ9.MROnmydnXtfjqjIBtC-P5g')
fig_map = px.scatter_mapbox(df_map, lat="lat", lon="long", text='location', color="number_of_tweets",
                            size="number_of_tweets",
                            color_continuous_scale=px.colors.cyclical.IceFire, size_max=20, zoom=4.6, )
fig_map.update_layout(margin=dict(t=0))


fig_cord_freq = go.Figure(go.Bar(
    x=df_map['number_of_tweets'].tolist(),
    y=df_map['location'].tolist(),
    orientation='h'), layout=go.Layout(xaxis={'title': 'Frequency'},
                                       yaxis={'title': 'Geo Locations'}, height=580, margin=dict(t=0)))


hashtag_mostcommon = obj_dc.get_Top_hashtags(top_n=20)

df_hashtag_cord_freq = obj_dc.hashtag_freq_by_geo(most_common=hashtag_mostcommon)


fig_hashtag_cord_freq = go.Figure()

for idx in range(1, len(df_hashtag_cord_freq.columns)):

    fig_hashtag_cord_freq.add_trace(go.Bar(
        y=df_map['location'],
        x=df_hashtag_cord_freq.iloc[:, idx],
        name=df_hashtag_cord_freq.columns[idx],
        orientation='h'
    ))

fig_hashtag_cord_freq.update_layout(xaxis={'title': 'Frequency'},
                                    yaxis={'title': 'Geo Locations'}, barmode='stack', height=580, margin=dict(t=0))


ls_top_hashtags = [item[0] for item in hashtag_mostcommon]
ls_top_hashtags_freq = [item[1] for item in hashtag_mostcommon]


fig_hashtag_freq = go.Figure(go.Bar(
    x=ls_top_hashtags_freq,
    y=ls_top_hashtags,
    orientation='h'), layout=go.Layout(xaxis={'title': 'Frequency'},
                                       yaxis={'title': 'Top 20 Hashtags'}, height=580, margin=dict(t=0)))


hashtags_wordcloud = [{"text": a, "value": b} for a, b in obj_dc.get_Top_hashtags(top_n=200)]

mentions_wordcloud = [{"text": a, "value": b} for a, b in obj_dc.get_Top_mentions(top_n=200)]



row1 = dbc.Row(
    [
        dbc.Col([
            html.Div([

                # range slider
                html.P([
                    html.P(
                        'The following metric shows the frequency of tweets on dates. The year/month range can be set using the below filter'),
                    html.Br(),
                    html.Label("Filter by Year"),
                    dcc.RangeSlider(id='slider',
                                    marks=date_mark,
                                    min=0,
                                    max=len(date_ranges) - 1,
                                    value=[0, len(date_ranges) - 1])
                ], style={'width': '90%',
                          'fontSize': '20px',
                          'padding': '50px 50px 50px 50px',
                          'display': 'inline-block'})

            ], style={'backgroundColor': '#f9f9f9', 'marginTop': '10px', 'boxShadow': '2px 2px 2px lightgrey',
                      'height': '350px'})

        ], md=4),

        dbc.Col(
            [
                html.Div([
                    dcc.Graph(id='plot', figure=fig),
                ], style={'height': '500px'})
            ], md=8
        ),

    ], style={'paddingLeft': '50px', 'paddingRight': '50px', 'marginTop': '10px'}
)

row2 = dbc.Row(
    [
        dbc.Col([

            html.Div([
                dcc.Graph(id='plot_cord_freq', figure=fig_cord_freq)])

        ], md=6),

        dbc.Col(
            [
                html.Div([
                    dcc.Graph(id='plot_map', figure=fig_map)] )
            ], md=6
        )
    ], style={'paddingLeft': '50px', 'paddingRight': '50px', 'marginTop': '20px'}
)


row3 = dbc.Row(
    [
        dbc.Col([

            html.Div([
                dcc.Graph(id='plot_hashtag_cord_freq', figure=fig_hashtag_cord_freq)])

        ], md=6),

        dbc.Col(
            [
                html.Div([
                    dcc.Graph(id='plot_hashtag_freq', figure=fig_hashtag_freq)])
            ], md=6
        )
    ], style={'paddingLeft': '50px', 'paddingRight': '50px', 'marginTop': '20px'}
)


row4 = dbc.Row(
    [
        dbc.Col([

            html.Div([
                dash_d3cloud.WordCloud(
                    id='hashtags_cloud',
                    words=hashtags_wordcloud,
                    options={'spiral': 'rectangular',
                             'scale': 'log',
                             'rotations': 2,
                             'rotationAngles': [0, -90]
                             },
                )
            ])

        ], md=6),

        dbc.Col(
            [
                html.Div([
                    dash_d3cloud.WordCloud(
                        id='mentions_cloud',
                        words=mentions_wordcloud,
                        options={'spiral': 'rectangular',
                                 'scale': 'log',
                                 'rotations': 2,
                                 'rotationAngles': [0, -90]
                                 },
                    )

                ])
            ], md=6
        )
    ], style={'paddingLeft': '50px', 'paddingRight': '50px', 'marginTop': '20px'}
)

app.layout = html.Div([navbar,

                       html.Div(
                           [
                               html.H3(
                                   "Tweets by Day",
                                   style={'textAlign': 'center'},
                               )
                           ], style={'paddingLeft': '50px', 'paddingRight': '50px', 'paddingTop': '10px'}
                       ),
                       row1,

                       html.Div(
                           [
                               html.H3(
                                   "Frequency of Tweets by Location",
                                   style={'textAlign': 'center'},
                               )
                           ], style={'paddingLeft': '50px', 'paddingRight': '50px'}
                       ),

                       row2,

                       html.Div(
                           [
                               html.H3(
                                   "Frequency of Top 20 Hashtags by Location ",
                                   style={'textAlign': 'center'},
                               )
                           ], style={'paddingLeft': '50px', 'paddingRight': '50px'}
                       ),
                       row3,

                       html.Div(
                           [
                               html.H3(
                                   "Word Clouds - Top Hashtags and Top Mentions",
                                   style={'textAlign': 'center'},
                               )
                           ], style={'paddingLeft': '50px', 'paddingRight': '50px','paddingTop': '10px'}
                       ),
                       row4
                       ])


@app.callback(Output('plot', 'figure'),
              [Input('slider', 'value')])
def update_figure(X):
    _x_dates, _y_freq = obj_dc.tweets_by_date(dt1=date_ranges[X[0]], dt2=date_ranges[X[1]])
    trace_1 = go.Scatter(x=_x_dates, y=_y_freq, name='date', line=dict(width=2, color='rgb(229, 151, 50)'))
    fig = go.Figure(data=[trace_1], layout=layout)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
