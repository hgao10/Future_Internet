try:
    from . import util
except (ImportError, SystemError):
    import util
#set_sat_links
from collections import defaultdict
import math
EARTH_RADIUS = 6371  # Kms
MAX_ISL_LENGTH=5014 #km
sat_positions = {}
sat_positions = util.read_sat_positions("../input_data/sat_positions.txt")

# with open("../output_data/sat_links.txt", 'w') as file:
# 	# 40 satellites per orbit, 40 orbits
# 	for i in range(40):
# 		#in each orbit, connect neighboring satellites, 0 -> 1, 1 -> 2
# 		for j in range(40):
# 			sat1 = i*40+j
# 			sat2 = i*40+j+1
# 			if (j==39):
# 				sat2 = i*40
# 			file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))])))

# 	# connect to orbit k -1
# 	for k in range(1,40):
# 		for l in range(40):
# 			sat1 = k*40 + l
# 			sat2 = (k-1)*40 + l
# 			file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))])))


 
# for each satalite see if its in the other cities range, stop searching when it is in range
# otherwise try every other satellite as the next stop (isl < 5K, and rank by dist(next_stop, dest), pick the smallest)

def take_third(elem):
	return elem['geo_dist']

# rank city pairs by distance from max to min
city_pairs = util.read_city_pair_file("../input_data/city_pairs.txt")
ranked_city_pairs = [x for x in city_pairs.values()] # each element is a dictionary city1: city2: geo_dist
ranked_city_pairs.sort(key=take_third, reverse=True)

#print(ranked_city_pairs)
# start from one city's coverage, check for shortest distance, choose top 3


def read_coverage(coverage_file):
    """
        Read satellite coverage for cities

        :param coverage_file: Input file name

        :return: Data structure holding city-satellite coverage mapping
    """
    city_coverage = defaultdict(dict)
    lines = [line.rstrip('\n') for line in open(coverage_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        # if str(val[0]) not in city_coverage.keys():
        # 	city_coverage_dist[str(val[0])+"_"+]
        # 	city_coverage[str(val[0])] = [{

        #     "sat": int(val[1]),
        #     "dist": float(val[2])}]
        # else:
        # 	city_coverage[str(val[0])].append({
        #     "sat": int(val[1]),
        #     "dist": float(val[2])})
        city_coverage[str(val[0])][str(val[1])] = float(val[2]) # city_coverage[city][sat] = distance

        
    return city_coverage
city_coverage = read_coverage("../input_data/city_coverage.txt")
# print(city_coverage['10001']['5'])
# sat_forcity = [ k for k in city_coverage['10001'] ]
# print(sat_forcity)

def read_city_positions(city_pos_file):
    """
        Read satellite positions from file

        :param sat_pos_file: Input file name

        :return: Data structure holding satellite position details
    """
    city_positions = {}
    lines = [line.rstrip('\n') for line in open(city_pos_file)]
    for i in range(len(lines)):
        val = lines[i].split(",")
        city_positions[int(val[0])] = {
            "lat_deg": float(val[2]),
            "lat_rad": math.radians(float(val[2])),
            "long_deg": float(val[3]),
            "long_rad": math.radians(float(val[3])),
            "alt_km": int(0)
        }
    return city_positions

city_positions = read_city_positions("../input_data/cities.txt")
#print(city_positions[10001])


def compute_sat_city_length(sat1, city1, sat_positions, city_positions):
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
    x2 = (EARTH_RADIUS + city_positions[city1]["alt_km"]) * math.cos(city_positions[city1]["lat_rad"]) * math.sin(
        city_positions[city1]["long_rad"])
    y2 = (EARTH_RADIUS + city_positions[city1]["alt_km"]) * math.sin(city_positions[city1]["lat_rad"])
    z2 = (EARTH_RADIUS + city_positions[city1]["alt_km"]) * math.cos(city_positions[city1]["lat_rad"]) * math.cos(
        city_positions[city1]["long_rad"])
    dist = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2) + math.pow((z2 - z1), 2))
    return dist

#print(compute_sat_city_length(1, 10001, sat_positions, city_positions))

# for city_pair in ranked_city_pairs:
# 	city1 = city_pair['city_1'] #city1 ID  
# 	city2 = city_pair['city_2'] #city2 ID
# 	city1_coverage =[ sat for sat in city_coverage[str(city1)] ]# a list of sat that city1 covers
# 	city2_coverage = [ sat for sat in city_coverage[str(city2)] ]
# 	next_sat_list = city1_coverage[:]
# 	path_chosen = []
# 	path_length = {}

# 	previous_node = city1
# 	current_path = [previous_node]
# 	while True:
		
# 		for next_sat in next_sat_list:
# 			# firxt time
# 			current_path_length = 0
# 			next_sat_to_city_dist = compute_sat_city_length(int(next_sat), int(city1), sat_positions, city_positions)
# 			if previous_node == city1:
# 				current_path_length = city_coverage[str(city1)][str(next_sat)] + next_sat_to_city_dist
			
# 			else: #both previous node is a satellite
# 				isl_length = compute_isl_length(int(previous_node), int(next_sat), sat_positions)
# 				if isl_length > MAX_ISL_LENGTH:
# 					break
# 				current_path_length = isl_length + next_sat_to_city_dist

# 			path_length[current_path_length] = next_sat

# 		min_path_length = min([path for path in path_length.values()])
# 		current_path.append(path_length[min_path_length])
# 		if next_sat in city2_coverage:
# 			break

# 		next_sat_list = all_sat + [city1] - [current_path]
# 		previous_node = next_sat

all_sat = [ x for x in range(1200)]

city_pair = city_pairs[0]
city1 = city_pair['city_1'] #city1 ID  
all_sat.append(city1)

city2 = city_pair['city_2'] #city2 ID
print("city1: %s, city2: %s" %(city1, city2))
city1_coverage =[ sat for sat in city_coverage[str(city1)] ]# a list of sat that city1 covers
city2_coverage = [ int(sat) for sat in city_coverage[str(city2)] ]

next_sat_list = city1_coverage[:]
path_chosen = []
path_length = {}

previous_node = city1
current_path = [previous_node]
while True:
	
	for next_sat in next_sat_list:
		# firxt time
		current_path_length = 0
		next_sat_to_city_dist = compute_sat_city_length(int(next_sat), int(city2), sat_positions, city_positions)
		print("next_sat:%s, next_sat to destination dist: %s \n" %(next_sat, next_sat_to_city_dist))
		if previous_node == city1:
			current_path_length = city_coverage[str(city1)][str(next_sat)] + next_sat_to_city_dist
		
		else: #both previous node is a satellite
			isl_length = util.compute_isl_length(int(previous_node), int(next_sat), sat_positions)
			if isl_length > MAX_ISL_LENGTH:
				continue
			current_path_length = isl_length + next_sat_to_city_dist
			print("current_path_length of last isls: %s and current_path_length: %s\n" %(isl_length, current_path_length))
		path_length[current_path_length] = int(next_sat)


	min_path_length = min([path for path in path_length.keys()])

	current_path.append(path_length[min_path_length])
	print("path length dictionary before clearing: %s\n"%(path_length))
	path_length.clear()
	print("path_length should be empty:%s\n" %(path_length))
	print("min_path_length: %s and append sat:%s\n" %(min_path_length, current_path[-1]))
	if next_sat in city2_coverage:
		break

	next_sat_list = set(all_sat) - set(current_path)
	print("next_sat_list")
	previous_node = current_path[-1]
	print("previous_node: %s, current_path:%s\n" %(previous_node, current_path))

print(current_path)






			





