# WMATA TSP - wmata.py
# Calculate the fastest route through all Metro stations
# (c) Zack Bamford (Not affiliated in any way with the Washington Metropolitan Area Transportation Authority)

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


@dataclass
class Station:
    """
    Show information about a rail station
    """
    station_code: str
    alt_station_code: Union[str, None]
    station_name: str
    coords: list[tuple]
    stops: Union[list[Stop], None]


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
    station_info_url = "https://api.wmata.com/Rail.svc/json/jStations"

    # get station information dump
    station_data = wmata_url_call(station_info_url)

    
    # TODO: Remember to deal with StationTogether

