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

import sys

try:
    from . import util
except (ImportError, SystemError):
    import util

satPositions = {}


def compute_actual_lengths(file_name):
    """
        Compute ISL length between pairs of satellites in order to validate the link file provided

        :param file_name: input file
    """
    lines = [line.rstrip('\n') for line in open(file_name)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        sat1 = int(val[0])
        sat2 = int(val[1])
        if sat1 < 10000 and sat2 < 10000:
            print(','.join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))]))


sat_pos_file = sys.argv[1]
sat_links_file = sys.argv[2]

satPositions = util.read_sat_positions(sat_pos_file)
compute_actual_lengths(sat_links_file)
