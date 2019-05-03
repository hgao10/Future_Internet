import networkx as nx
import itertools
from collections import defaultdict

try:
    from . import util
except (ImportError, SystemError):
    import util
#set_sat_links

satPositions = {}
satPositions = util.read_sat_positions("../input_data/sat_positions.txt")

city_pair_file = "../input_data/city_pairs.txt"
city_pairs = {}
city_pairs = util.read_city_pair_file(city_pair_file)

city_coverage_file = "../input_data/city_coverage.txt"
city_coverage = util.read_coverage(city_coverage_file)
#with open("../output_data/sat_links.txt", 'w') as file:
#	# 40 satellites per orbit, 40 orbits
#	for i in range(40):
#		#in each orbit, connect satellites on same orbit, maximize distance, 0 -> 4, 1 -> 5
#		for j in range(40):
#			sat1 = i*40+j
#			sat2 = (j+4)%(40)+i*40
#			file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))])))
#
#	# connect to satelites in orbit k -3
#	for k in range(40):
#		for l in range(40):
#			sat1 = k*40 + l
#			sat2 = ((k-3)%40)*40 + l
#			file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))])))

G = nx.Graph()
check_graph = nx.Graph()
# -------------------------------
# 1. connect satellites with ISL < 5015, do not count connections per satellite ( no cities included yet)
# 2. for each city pair, add respective coverages and compute shortest path.
# 3. check ISL connections (not exceed 4 per satellite) --> add to ISL file
# 4. remove city coverage after each iteration, such that no link goes over a third city
# -------------------------------
# 1.
sat_pairs = list(itertools.combinations(range(len(satPositions)),2))
for sat1, sat2 in sat_pairs:
    dist = util.compute_isl_length(sat1,sat2,satPositions)
    if(dist < 5015):
        G.add_edge(sat1,sat2,length=float(dist))
# 2.
# sort city pairs such that pairs with highest distance are first evaluated
def take_third(elem):
    return elem['geo_dist']

ranked_city_pairs = [x for x in city_pairs.values()]
ranked_city_pairs.sort(key=take_third, reverse=True)
for elem in ranked_city_pairs:
    city1 = elem["city_1"]
    city2 = elem["city_2"]
    util.add_coverage_for_city(int(city1), city_coverage,G)
    util.add_coverage_for_city(int(city2), city_coverage,G)
    # compute shortest path over graph G
    path = nx.shortest_path(G, city1, city2, weight='length')
    print(city1, city2, nx.shortest_path_length(G, city1, city2, weight='length'), path)
    sats = path[1:-1]
    finished = False
# 3.
    while not finished:
        max_degree = 0
        keep_edges = []
        # check which edges already existed before adding new ones
        for i in range(len(sats)-1):
            if check_graph.has_edge(sats[i],sats[i+1]):
                keep_edges.append((sats[i],sats[i+1]))
            check_graph.add_edge(sats[i],sats[i+1])
        comb = list(check_graph.degree(check_graph.nodes()))
        to_remove = [(x,y) for x,y in comb if y > 4]
        if(len(to_remove) != 0):
            # remove now unused edge from check_graph
            for i in range(len(sats)-1):
                if (sats[i],sats[i+1]) not in keep_edges:
                    check_graph.remove_edge(sats[i],sats[i+1])    
            # check how many edges need to be removed, remove optimal edge (for shortest path of current city pair)
            for sat,isls in to_remove:
                print(sat,isls)
                sats_to_remove = [s for (s,y) in to_remove]
                # at beginning and end of path only one new link was added (for sure) --> remove
                # always check if both ends of an edge are in to_remove before removing the edge and then only remove the edge once
                if sats[0] == sat:
                    # remove this edge from G
                    if sats[1] in sats_to_remove:
                        to_remove.remove((sats[1],5))
                    G.remove_edge(sat, sats[1])
                    path = nx.shortest_path(G,city1,city2,weight='length')
                elif sat == sats[-1]:
                    # remove this edge from G
                    if sats[1] in sats_to_remove:
                        to_remove.remove((sats[1],5))
                    G.remove_edge(sats[-2],sat)
                    path = nx.shortest_path(G,city1,city2,weight='length')
                else:
                    # if deg == 6 remove both new edges
                    index = sats.index(sat)
                    if isls == 6:
                        if sats[index-1] in sats_to_remove:
                            ind = sats_to_remove.index(sats[index-1])
                            deg = to_remove[ind][1] # return number of isls for this satellite
                            if deg == 5:
                                to_remove.remove((sats[index-1],deg))
                            else:
                                to_remove[ind] = (sats[index-1],deg - 1)
                        if sats[index+1] in sats_to_remove:
                            ind = sats_to_remove.index(sats[index+1])
                            deg = to_remove[ind][1] # return number of isls for this satellite
                            if deg == 5:
                                to_remove.remove((sats[index+1],deg))
                            else:
                                to_remove[ind] = (sats[index+1],deg - 1)
                        G.remove_edge(sats[index-1],sat)
                        G.remove_edge(sat,sats[index+1])
                        path = nx.shortest_path(G,city1,city2,weight='length')
                    else: 
                        # find optimal edge to remove
                        min_path_len = 0
                        path_len_1 = 0
                        path_len_2 = 0
                        if G.has_edge(sats[index-1],sat):
                            # test for path length with incoming edge removed
                            G.remove_edge(sats[index-1],sat)
                            path_len_1 = nx.shortest_path_length(G,city1, city2,weight='length')
                            G.add_edge(sats[index-1],sat)
                        if G.has_edge(sat,sats[index+1]):
                            # test for path length with outgoing edge removed
                            G.remove_edge(sat, sats[index+1])
                            path_len_2 = nx.shortest_path_length(G, city1,city2,weight='length')
                            G.add_edge(sat,sats[index+1])
                        # remove optimal edge and compute path anew
                        if path_len_1 == 0:
                            G.remove_edge(sat,sats[index+1])
                            path = nx.shortest_path(G,city1,city2,weight='length')
                        elif path_len_2 == 0:
                            G.remove_edge(sats[index-1],sat)
                            path = nx.shortest_path(G,city1,city2,weight='length')
                        elif path_len_1 <= path_len_2:
                            G.remove_edge(sats[index-1],sat)
                            path = nx.shortest_path(G,city1,city2,weight='length')
                        else:
                            if sats[index+1] in sats_to_remove:
                                ind = sats_to_remove.index(sats[index+1])
                                deg = to_remove[ind][1] # return number of isls for this satellite
                                if deg == 5:
                                    to_remove.remove((sats[index+1],deg))
                                else:
                                    to_remove[ind] = (sats[index+1],deg - 1)
                            G.remove_edge(sat,sats[index+1])
                            path = nx.shortest_path(G,city1,city2,weight='length')
            sats = path[1:-1]
            finished = False
            break;    
        else:
            finished = True
    # add ISLs to file
#       for i in range(len(sats)-1):
#           sat1 = sats[i]
#           sat2 = sats[i+1]
#           file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))])))
# 4.   
    try:
        util.remove_coverage_for_city(int(city1), city_coverage, G)
    except:
        print("upps")
    try:
        util.remove_coverage_for_city(int(city2), city_coverage, G)
    except:
        print("upps 2")

# use edges in check_graph to write ISL file
with open("../output_data/sat_links.txt", "w") as file:
    for sat1,sat2 in check_graph.edges():
        file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))])))




