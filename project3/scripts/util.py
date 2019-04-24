# The MIT License (MIT)
#
# Copyright (c) 2019 Debopam Bhattacherjee
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import math

EARTH_RADIUS = 6371  # Kms


def compute_isl_length(sat1, sat2, sat_positions):
    """
        Compute ISL length between pairs of satellites

        :param sat1: ID of first satellite
        :param sat2: ID of the other satellite
        :param sat_positions: Data structure holding satellite position details

        :return: Distance in KM between satellites (ISL length)
    """
    x1 = (EARTH_RADIUS + sat_positions[sat1]["alt_km"]) * math.cos(sat_positions[sat1]["lat_rad"]) * math.sin(
        sat_positions[sat1]["long_rad"])
    y1 = (EARTH_RADIUS + sat_positions[sat1]["alt_km"]) * math.sin(sat_positions[sat1]["lat_rad"])
    z1 = (EARTH_RADIUS + sat_positions[sat1]["alt_km"]) * math.cos(sat_positions[sat1]["lat_rad"]) * math.cos(
        sat_positions[sat1]["long_rad"])
    x2 = (EARTH_RADIUS + sat_positions[sat2]["alt_km"]) * math.cos(sat_positions[sat2]["lat_rad"]) * math.sin(
        sat_positions[sat2]["long_rad"])
    y2 = (EARTH_RADIUS + sat_positions[sat2]["alt_km"]) * math.sin(sat_positions[sat2]["lat_rad"])
    z2 = (EARTH_RADIUS + sat_positions[sat2]["alt_km"]) * math.cos(sat_positions[sat2]["lat_rad"]) * math.cos(
        sat_positions[sat2]["long_rad"])
    dist = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2) + math.pow((z2 - z1), 2))
    return dist


def read_sat_positions(sat_pos_file):
    """
        Read satellite positions from file

        :param sat_pos_file: Input file name

        :return: Data structure holding satellite position details
    """
    sat_positions = {}
    lines = [line.rstrip('\n') for line in open(sat_pos_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        sat_positions[int(val[0])] = {
            "lat_deg": float(val[3]),
            "lat_rad": math.radians(float(val[3])),
            "long_deg": float(val[4]),
            "long_rad": math.radians(float(val[4])),
            "alt_km": int(val[5])
        }
    return sat_positions


def read_links(links_file, G):
    """
        Read ISLs and populate graph edges

        :param links_file: Input file name
        :param G: Graph to be populated
    """
    lines = [line.rstrip('\n') for line in open(links_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        if int(val[0]) < 10000 and int(val[1]) < 10000:
            G.add_edge(int(val[0]), int(val[1]), length=float(val[2]))


def read_links_compute(links_file, sat_positions, G):
    """
        Read ISLs, compute ISL lengths, and populate graph edges

        :param links_file: Input file name
        :param sat_positions: Data structure holding satellite position details
        :param G: Graph to be populated
    """
    lines = [line.rstrip('\n') for line in open(links_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        if int(val[0]) < 10000 and int(val[1]) < 10000:
            G.add_edge(int(val[0]), int(val[1]), length=compute_isl_length(int(val[0]), int(val[1]), sat_positions))


def read_city_positions(city_pos_file):
    """
        Read city positions from file

        :param city_pos_file: Input file name

        :return: Data structure holding city coordinates
    """
    city_positions = {}
    lines = [line.rstrip('\n') for line in open(city_pos_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        city_positions[int(val[0])] = {
            "lat_deg": float(val[2]),
            "long_deg": float(val[3])
        }
    return city_positions


def read_coverage(coverage_file):
    """
        Read satellite coverage for cities

        :param coverage_file: Input file name

        :return: Data structure holding city-satellite coverage mapping
    """
    city_coverage = {}
    lines = [line.rstrip('\n') for line in open(coverage_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        city_coverage[i] = {
            "city": int(val[0]),
            "sat": int(val[1]),
            "dist": float(val[2])
        }
    return city_coverage


def add_coverage_for_city(city, city_coverage, G):
    """
        Add coverage for a specific city to the graph

        :param city: City ID
        :param city_coverage: Data structure holding city-satellite coverage mapping
        :param G: Graph to be populated
    """
    for i in range(len(city_coverage)):
        if city_coverage[i]["city"] == city:
            G.add_edge(city_coverage[i]["city"], city_coverage[i]["sat"], length=city_coverage[i]["dist"])


def remove_coverage_for_city(city, city_coverage, G):
    """
        Remove coverage for a specific city from the graph

        :param city: City ID
        :param city_coverage: Data structure holding city-satellite coverage mapping
        :param G: Graph in context
    """
    for i in range(len(city_coverage)):
        if city_coverage[i]["city"] == city:
            G.remove_edge(city_coverage[i]["city"], city_coverage[i]["sat"])


def read_city_pair_file(city_pair_file):
    """
        Read pairs of cities with traffic between them

        :param city_pair_file: Input file name

        :return: Data structure holding city pair mapping
    """
    city_pairs = {}
    lines = [line.rstrip('\n') for line in open(city_pair_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        city_pairs[i] = {
            "city_1": int(val[0]),
            "city_2": int(val[1]),
            "geo_dist": float(val[2])
        }
    return city_pairs
