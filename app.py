from dash import Dash, html, dcc, Input, Output, State
from figure_creator import FigureCreator
import dash_bootstrap_components as dbc
from PIL import Image
import os

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(
    __name__,
    external_stylesheets=[dbc_css, dbc.themes.DARKLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)

app.title = "ТрансCиб Навигатор"
server = app.server

fc = FigureCreator()
fig = fc.get_figure()
station_lats, station_lons, station_names = fc.station_lats, fc.station_lons, fc.station_names

logo_image = Image.open(os.getcwd() + "/logo.png")
logo = html.Img(src=logo_image, width=150, height=150)

station_options = [{"label": sname, "value": sname} for sname in station_names]
station_from = html.Div(
    [
        dbc.FormText("Станция отправления"),
        dcc.Dropdown(
            id='station_from',
            options=station_options,
            placeholder='Откуда'
        ),
    ]
)
station_to = html.Div(
    [
        dbc.FormText("Станция назначения"),
        dcc.Dropdown(
            id='station_to',
            options=station_options,
            placeholder='Куда',
        )
    ]
)


map_graph = dcc.Graph(figure=fig, id="map_graph", style={'width': '90vh', 'height': '90vh'})


route_info_fig = fc.get_route_info()
route_graph = dcc.Graph(figure=route_info_fig, id="route_info_graph",
                        className="dbc",
                        config=dict(displayModeBar=False))
route_info = dbc.Collapse(
            route_graph,
            id="route_info_collapse",
            is_open=False,
            className="dbc",
        )


# Layout of Dash App
app.layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [html.Div(logo, style={'textAlign': 'center'})],
                            justify="center",
                        ),
                        dbc.Row(
                            [station_from, html.P(), station_to, html.Br(), route_info]
                        )
                    ],
                    width={'size': 3},
                    className="p-3 ",
                ),
                dbc.Col(
                    [map_graph],
                    width="auto",
                    className="p-3",
                )
            ],
        )
    ],
    className="dbc px-4"
)


@app.callback(
    Output(component_id='map_graph', component_property='figure'),
    Output(component_id='route_info_graph', component_property='figure'),
    Output(component_id="route_info_collapse", component_property="is_open"),
    Input("station_from", "value"),
    Input("station_to", "value")
)
def choose_start_end_stations(from_value, to_value):
    route_is_formed = fc.update_figure(station_from=from_value, station_to=to_value)
    return fc.figure, fc.route_info_figure, route_is_formed


if __name__ == '__main__':
    app.run_server(debug=False)