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
import networkx as nx
import sys

try:
    from . import util
except (ImportError, SystemError):
    import util

G = nx.Graph()
city_coverage = {}
city_pairs = {}


def get_shortest_path_between_cities():
    """
        Compute paths between pairs of cities.
        At each step, add city coverage, compute path, and remove city coverage
        in order to ensure no path passes through a third city.
    """
    global G
    for i in range(len(city_pairs)):
        city1 = city_pairs[i]["city_1"]
        city2 = city_pairs[i]["city_2"]
        try:
            util.add_coverage_for_city(city1, city_coverage, G)
            util.add_coverage_for_city(city2, city_coverage, G)
            print(city1, city2, nx.shortest_path_length(G, city1, city2, weight='length'), nx.shortest_path(G, city1, city2, weight='length'))
            util.remove_coverage_for_city(city1, city_coverage, G)
            util.remove_coverage_for_city(city2, city_coverage, G)
        except:
            print(999999)

sat_links_file = sys.argv[1]
city_coverage_file = sys.argv[2]
city_pair_file = sys.argv[3]

util.read_links(sat_links_file, G)
city_coverage = util.read_coverage(city_coverage_file)
city_pairs = util.read_city_pair_file(city_pair_file)
get_shortest_path_between_cities()
