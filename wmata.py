# WMATA TSP - wmata.py
# Calculate the fastest route through all Metro stations
# (c) Zack Bamford
# (Not affiliated in any way with the Washington Metropolitan Area Transportation Authority)

import os
from dataclasses import dataclass
import requests
from typing import Union


def wmata_url_call(url: str) -> dict:
    """
    Make a WMATA API request

    :param url: Fully Formatted URL Endpoint
    :return: JSON response from WMATA
    """
    api_key = os.environ["WMATA_KEY"]
    headers = {"api_key": api_key}

    # make request
    r = requests.get(url, headers=headers)

    return r.json()
    # TODO: WMATA Endpoint error handling


@dataclass
class Stop:
    """
    Store information about a bus stop
    """
    stop_id: str
    stop_name: str
    routes: list[str]


@dataclass(frozen=True)  # frozen to add to graph
class Station:
    """
    Show information about a rail station
    """
    station_code: str
    station_name: str
    coords: tuple
    lines_served: list[str]
    bus_stops: Union[list[Stop], None]


@dataclass(frozen=True)
class PathBetweenStations:
    """
    Store information about the lines connecting two rail stations
    """
    start_code: str
    end_code: str
    line: str
    distance: int
    OSI: bool


def get_nearby_stops(lat: float, lon: float) -> list[Stop]:
    """
    Return a list of stops near a coordinate

    :param lat: Latitude to search
    :param lon: Longitude to search
    :return: List of stops within radius
    """
    valid_radius = 250  # meters (250m ≈ .15 mile)
    nearby_stops_url = "https://api.wmata.com/Bus.svc/json/jStops?Lat={0}&Lon={1}&Radius={2}"  # Lat, Lon, Dist

    # get data
    stop_data = wmata_url_call(nearby_stops_url.format(lat, lon, valid_radius))
    stops = []

    # iter through stops
    for s in stop_data["Stops"]:
        stops.append(Stop(
            s["StopID"],
            s["Name"],
            s["Routes"]
        ))

    return stops


def get_all_stations() -> list[Station]:
    """
    Get information for all stations in the system

    :return: List of all Station objects
    """
    stations = []

    station_info_url = "https://api.wmata.com/Rail.svc/json/jStations"

    # get station information dump
    station_data = wmata_url_call(station_info_url)

    # generate object for every station
    for station in station_data["Stations"]:
        # create list of line codes
        line_codes = []
        for ln_num in range(1, 5):
            code = station["LineCode" + str(ln_num)]

            # check for valid line code
            if code is not None:
                line_codes.append(code)

        # fill in data fields
        new_station = Station(station["Code"],
                              station["Name"],
                              (station["Lat"], station["Lon"]),
                              line_codes,
                              None)  # ignore buses for now

        stations.append(new_station)

    return stations


def get_all_paths_between_stations() -> list[PathBetweenStations]:
    """
    Find distance between all stations

    :return: A list of all sections of track between stations
    """

    # get line destinations
    lines = wmata_url_call("https://api.wmata.com/Rail.svc/json/jLines")
    station_codes = []
    paths = []

    # extract destinations on every line
    for l in lines["Lines"]:
        station_codes.append((l["StartStationCode"], l["EndStationCode"]))

    # get all paths on a line
    for ln in station_codes:

        raw_paths = wmata_url_call(
            "https://api.wmata.com/Rail.svc/json/jPath?FromStationCode={0}&ToStationCode={1}".format(ln[0], ln[1]))

        # format list to reverse through
        raw_paths = raw_paths.get("Path")
        raw_paths.reverse()

        last_dist = None
        last_station_code = None

        for raw_path in raw_paths:
            # store first dist
            if last_dist is None:
                last_dist = raw_path["DistanceToPrev"]
                last_station_code = raw_path["StationCode"]

            else:
                # create path object
                new_path = PathBetweenStations(last_station_code,
                                               raw_path["StationCode"],
                                               raw_path["LineCode"],
                                               last_dist,
                                               False)
                paths.append(new_path)

            # store new information
            last_dist = raw_path["DistanceToPrev"]
            last_station_code = raw_path["StationCode"]

    return paths
