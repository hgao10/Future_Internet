# WAN Traffic Engineering Project

### Information

* Group number: 15 
* Student NetIDs: 17-937-392, 13-914-973

### Part C explanation

We used the shortest_simple_paths algorithm from the networkx library over a weighted graph. Between each pair of vertices we computed 10 of these paths and changed the weight of the edges according to the number that they have been used. This should discourage highly used edges to be used in further iterations of our path selection algorithm. This should help in keeping the rates high on all edges.

### Getting started

**Dependencies**

* Python 3.5+
* `pip3 install networkx`
* `pip3 install numpy`
* `pip3 install ortools`
* `pip3 install git+https://gitlab.ethz.ch/kassings/python-ortools-lp-parser.git` (you must authenticate)

**What you have to do in a nutshell**

1. You can verify your solutions yourself locally by running `cd code; python3 evaluator_myself.py`
2. Set your team name by editing team_name.txt
3. Implement code/skeleton_a.py (run via `cd code; python3 skeleton_a.py`)
4. Implement code/skeleton_b.py (run via `cd code; python3 skeleton_b.py`)
5. Implement code/skeleton_c.py (run via `cd code; python3 skeleton_c.py`)

Proper software engineering practices (e.g. splitting off shared functionality between the three parts into separate files) are encouraged. For any other explanation look at wan_te_project.pdf

**Leaderboard**

The output you commit and push into the Git repository in myself/output/c is evaluated every 5 min approximately. You can view the leaderboard at:

http://bach20.ethz.ch/leaderboard.html
