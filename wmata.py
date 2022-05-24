# WMATA TSP - wmata.py
# Calculate the fastest route through all Metro stations
# (c) Zack Bamford
# (Not affiliated in any way with the Washington Metropolitan Area Transportation Authority)

import os
import pickle
from dataclasses import dataclass
import requests
from typing import Union

STATION_TO_STATION_SAVE_FILE = "station_to_station.p"
STATION_TO_STATION_SAVED = False


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
    station_together: Union[str, None]
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
    ISI: bool


@dataclass(frozen=True)
class StationToStationInformation:
    """
    Store information about travel between two rail stations
    """
    start_station: str
    end_station: str
    composite_miles: float
    rail_time: int
    peak_fare: float
    off_peak_fare: float
    reduced_fare: float


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
                              station["StationTogether1"],
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
                                               False, False)
                paths.append(new_path)

            # store new information
            last_dist = raw_path["DistanceToPrev"]
            last_station_code = raw_path["StationCode"]

    return paths


def get_ISI_from_stations(stations: list[Station]) -> list[PathBetweenStations]:
    """
    Get a list of In-Station Interchanges from stations

    :param stations:
    :return: A list of ISI paths
    """
    ISIs = []

    # WMATA ISI are used for StationTogether and therefore have no *distance* costs

    for s in stations:
        if s.station_together != '':
            for line in s.lines_served:
                path = PathBetweenStations(s.station_code, s.station_together, line, 0, False, True)
                ISIs.append(path)

    return ISIs


def get_all_station_to_stations() -> dict:
    """
    Get all station to station information

    :return: Dict of (start_code, end_code) key with StationToStationInformation value
    """

    data = dict()

    station_station_endpoint = "https://api.wmata.com/Rail.svc/json/jSrcStationToDstStationInfo"

    # get data
    raw_data = wmata_url_call(station_station_endpoint)

    # TODO: add error handling

    # format data into objects
    for rd in raw_data["StationToStationInfos"]:
        sts_obj = StationToStationInformation(rd["SourceStation"], rd["DestinationStation"],
                                              float(rd["CompositeMiles"]), int(rd["RailTime"]),
                                              float(rd["RailFare"]["PeakTime"]), float(rd["RailFare"]["OffPeakTime"]),
                                              float(rd["RailFare"]["SeniorDisabled"]))
        data[(rd["SourceStation"], rd["DestinationStation"])] = sts_obj

    return data


class StationToStation:
    """Class to reduce API calls by caching Station To Station information"""

    sts_dict: dict[tuple[str, str], StationToStationInformation]

    def __init__(self):
        # check for existing pickled file
        if os.path.exists(STATION_TO_STATION_SAVE_FILE):
            self.sts_dict = pickle.load(open(STATION_TO_STATION_SAVE_FILE, "rb"))

        # generate new information
        else:
            self.sts_dict = get_all_station_to_stations()
            pickle.dump(self.sts_dict, open(STATION_TO_STATION_SAVE_FILE, "wb"))  # save pickled version

    def station_to_station_predicted_time(self, start_station_code: str, end_station_code: str) -> int:
        """
        Get the WMATA predicted time between stations

        :param start_station_code: Station Code of starting station
        :param end_station_code: Station Code of ending station
        :return: Estimated time between stations in minutes
        """

        return self.sts_dict[(start_station_code, end_station_code)].rail_time
