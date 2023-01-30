import plotly.graph_objects as go
import pandas as pd
import time
import numpy as np
from shared import mapbox_access_token, THEMECOLORS


class FigureCreator:
    """
        Class for creating map and route info.
    """
    def __init__(self):

        self.station_lats, self.station_lons, self.station_names, self.station_coords = [], [], [], []
        self.read_data()

        self.unset_scale_params = {"zoom": 2.3, "lat_center": 50., "lon_center": 88.}
        self.figure = self.generate_figure()
        self.route_info_figure = self.generate_route_info_figure()

    def generate_figure(self):
        """
            Generation of map with all the railroad.
        """
        railroad_data = [
            # gray railroad (parts not in route)
            go.Scattermapbox(
                lat=self.station_lats,
                lon=self.station_lons,
                name="not_route",
                mode="lines",
                hoverinfo="text",
                text=self.station_names,
                marker=dict(
                    showscale=False,
                    color=THEMECOLORS['gray'],
                    opacity=0.99,
                    size=5,
                ),
            ),

            # stations inside the route
            go.Scattermapbox(
                lat=self.station_lats,
                lon=self.station_lons,
                name="route",
                mode="markers+lines",
                hoverinfo="text",
                text=self.station_names,
                marker=dict(
                    showscale=False,
                    color=THEMECOLORS['blue'],
                    opacity=0.99,
                    size=5,
                ),
            ),

            #
            go.Scattermapbox(
                lat=[self.station_lats[0], self.station_lats[-1]],
                lon=[self.station_lons[0], self.station_lons[-1]],
                name="boundaries",
                mode="markers+text",
                hoverinfo="text",
                text=[self.station_names[0], self.station_names[-1]],
                textposition="bottom center",
                textfont=dict(
                    family="sans serif",
                    size=18,
                    color=THEMECOLORS["blue"],
                ),
                marker=dict(
                    showscale=False,
                    color=THEMECOLORS['blue'],
                    opacity=0.99,
                    size=10,
                ),
            )
        ]

        layot_object = go.Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=0, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center={
                    "lat": self.unset_scale_params["lat_center"],
                    "lon": self.unset_scale_params["lon_center"]
                },
                style="dark",
                zoom=self.unset_scale_params["zoom"],
            ),
            paper_bgcolor=THEMECOLORS['background'],
            updatemenus=[],
        )
        fig = go.Figure(data=railroad_data, layout=layot_object)
        fig.add_annotation(x=self.station_lats[0], y=self.station_lons[0],
                           text=self.station_names[0],
                           showarrow=False,
                           yshift=10)
        return fig

    def read_data(self):
        """
            Read all the necessary data from csv-file and save it in class fields.
        """
        df = pd.read_csv('geospatial_data.csv', delimiter=';')
        self.station_lats = df.lat.tolist()
        self.station_lons = df.lon.tolist()
        self.station_names = df.name.tolist()
        self.station_coords = df.coordinate.tolist()

    @staticmethod
    def calculate_zoom_and_center(lats, lons):
        delta_lats = max(lats) - min(lats)
        delta_lons = max(lons) - min(lons)
        max_delta = max(delta_lats, delta_lons)

        lat_center = (max(lats) + min(lats)) / 2
        lon_center = (max(lons) + min(lons)) / 2

        zoom = np.interp(max_delta, [1., 97.], [4.4, 2.3])
        return {"zoom": zoom, "lat_center": lat_center, "lon_center": lon_center}

    def update_figure(self, station_from, station_to):
        from_set = not (station_from == "Откуда" or station_from == '' or station_from is None)
        to_set = not (station_to == "Куда" or station_to == '' or station_to is None)
        from_idx = self.station_names.index(station_from) if from_set else 0
        to_idx = self.station_names.index(station_to) if to_set else 0

        route_data = self.figure.data[1]
        boundaries_data = self.figure.data[2]
        route_info_data = self.route_info_figure.data
        route_is_formed = False

        if from_set and not to_set:
            route_data.lat = [self.station_lats[from_idx]]
            route_data.lon = [self.station_lons[from_idx]]
            boundaries_data.lat = [self.station_lats[from_idx]]
            boundaries_data.lon = [self.station_lons[from_idx]]
            boundaries_data.text = [self.station_names[from_idx]]
            self.figure. \
                update_traces(selector={"name": "route"},
                              marker=dict(color=THEMECOLORS['green'])). \
                update_traces(selector={"name": "boundaries"},
                              marker=dict(color=THEMECOLORS['green']),
                              textfont=dict(color=THEMECOLORS['green'])
                              )
            self.figure.update_layout(
                mapbox=dict(
                    zoom=self.unset_scale_params["zoom"],
                    center={
                        "lat": self.unset_scale_params["lat_center"],
                        "lon": self.unset_scale_params["lon_center"]
                    },
                )
            )

        elif to_set and not from_set:
            route_data.lat = [self.station_lats[to_idx]]
            route_data.lon = [self.station_lons[to_idx]]
            boundaries_data.lat = [self.station_lats[to_idx]]
            boundaries_data.lon = [self.station_lons[to_idx]]
            boundaries_data.text = [self.station_names[to_idx]]
            self.figure. \
                update_traces(selector={"name": "route"},
                              marker=dict(color=THEMECOLORS['green'])). \
                update_traces(selector={"name": "boundaries"},
                              marker=dict(color=THEMECOLORS['green']),
                              textfont=dict(color=THEMECOLORS['green'])
                              )
            self.figure.update_layout(
                mapbox=dict(
                    zoom=self.unset_scale_params["zoom"],
                    center={
                        "lat": self.unset_scale_params["lat_center"],
                        "lon": self.unset_scale_params["lon_center"]
                    },
                )
            )

        elif from_set and to_set:
            route_is_formed = True
            start, end = min(from_idx, to_idx), max(from_idx, to_idx)
            route_data.lat = self.station_lats[start:end+1]
            route_data.lon = self.station_lons[start:end+1]
            route_data.text = self.station_names[start:end+1]
            boundaries_data.lat = [self.station_lats[start], self.station_lats[end]]
            boundaries_data.lon = [self.station_lons[start], self.station_lons[end]]
            boundaries_data.text = [self.station_names[start], self.station_names[end]]
            self.figure.\
                update_traces(selector={"name": "route"},
                              marker=dict(color=THEMECOLORS['green'])). \
                update_traces(selector={"name": "boundaries"},
                              marker=dict(color=THEMECOLORS['green']),
                              textfont=dict(color=THEMECOLORS['green'])
                              )

            new_scale = self.calculate_zoom_and_center(
                self.station_lats[start:end+1],
                self.station_lons[start:end+1])
            self.figure.update_layout(
                mapbox=dict(
                    zoom=new_scale["zoom"],
                    center={
                        "lat": new_scale["lat_center"],
                        "lon": new_scale["lon_center"]
                    },
                )
            )
            route_info_data[0].text = ("   " + station_from,
                                       "   " + station_to)

            distance = int(self.station_coords[end] - self.station_coords[start])
            distance_text = "Расстояние: " + str(distance) + " км"
            time = distance / 59.5
            days = int(time // 24)
            hours = int(time % 24)

            if hours % 10 == 1 and hours % 100 > 20:
                hour_ending = "час"
            elif hours % 10 in [2, 3, 4]:
                hour_ending = "часа"
            else:
                hour_ending = "часов"

            if days % 10 == 1 and days % 100 > 20:
                day_ending = "день"
            elif days % 10 < 5:
                day_ending = "дня"
            else:
                day_ending = "дней"

            time_text = str(hours) + " " + hour_ending
            if days > 0:
                time_text = str(days) + " " + day_ending + ", " + time_text
            time_text = "В пути: ~" + time_text
            stations_text = "Остановок: " + str(end-start)
            route_info_data[1].text = [distance_text, time_text, stations_text]
        else:
            route_data.lat = self.station_lats
            route_data.lon = self.station_lons
            boundaries_data.lat = [self.station_lats[0], self.station_lats[-1]]
            boundaries_data.lon = [self.station_lons[0], self.station_lons[-1]]
            boundaries_data.text = [self.station_names[0], self.station_names[-1]]
            self.figure. \
                update_traces(selector={"name": "route"},
                              marker=dict(color=THEMECOLORS['blue'])). \
                update_traces(selector={"name": "boundaries"},
                              marker=dict(color=THEMECOLORS['blue']),
                              textfont=dict(color=THEMECOLORS['blue'])
                              )
            self.figure.update_layout(
                mapbox=dict(
                    zoom=self.unset_scale_params["zoom"],
                    center={
                        "lat": self.unset_scale_params["lat_center"],
                        "lon": self.unset_scale_params["lon_center"]
                    },
                )
            )
        return route_is_formed

    @staticmethod
    def generate_route_info_figure():
        route_info_fig = go.Figure(
            data=[
                go.Scatter(
                    x=[0, 0],
                    y=[100, 0],
                    mode="markers+lines+text",
                    text=["  Станция 1", "  Станция 2"],
                    textposition="middle right",
                    textfont=dict(
                        size=18,
                        color=THEMECOLORS["green"],
                    ),
                    hoverinfo='none',
                    marker=dict(
                        size=18,
                        color=THEMECOLORS["green"]
                    ),
                ),
                go.Scatter(
                    x=[0.3, 0.3, 0.3],
                    y=[60, 50, 40],
                    mode="text",
                    text=["Расстояние", "Время", "Остановок"],
                    textposition="middle right",
                    textfont=dict(
                        size=14,
                        color=THEMECOLORS["gray"],
                    ),
                    hoverinfo='none',
                    marker=dict(
                        size=18,
                        color=THEMECOLORS["green"]
                    ),
                ),
            ],
            layout=go.Layout(
                autosize=True,
                margin=go.layout.Margin(l=0, r=0, t=0, b=0),
                showlegend=False,
                updatemenus=[],
                plot_bgcolor=THEMECOLORS['background'],
                paper_bgcolor=THEMECOLORS['background'],
            )
        )

        route_info_fig.update_layout(
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False, "range": [-1, 10]},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False, "range": [-20, 120]})

        return route_info_fig

    def get_figure(self):
        """
            Simple getter for current figure (mapbox).
        """
        return self.figure

    def get_route_info(self):
        """
            Simple getter for route info (shown in collapse).
        """
        return self.route_info_figure

