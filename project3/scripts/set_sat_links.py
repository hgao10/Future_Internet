try:
    from . import util
except (ImportError, SystemError):
    import util
#set_sat_links
from collections import defaultdict
import math
import itertools
import subprocess
import random
#from optimize_test import permute_city_pairs

EARTH_RADIUS = 6371  # Kms
MAX_ISL_LENGTH=5014 #km
sat_positions = {}
sat_positions = util.read_sat_positions("../input_data/sat_positions.txt")

def take_third(elem):
	return elem['geo_dist']
# rank city pairs by distance from max to min

# city_pairs = util.read_city_pair_file("../input_data/city_pairs.txt")
# ranked_city_pairs = [x for x in city_pairs.values()] # each element is a dictionary city1: city2: geo_dist

#city_pairs_all = list(itertools.permutations(ranked_city_pairs))
#ranked_city_pairs.sort(key=take_third, reverse=True)

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

def check_score():
	MyOut = subprocess.Popen(['./check_score.sh'], 
	            stdout=subprocess.PIPE, 
	            stderr=subprocess.STDOUT)
	stdout,stderr = MyOut.communicate()
	str_stdout = stdout.decode("utf-8") 
	stdout_list = str_stdout.split("\n")
	score = float(stdout_list[-2].split(":")[1].lstrip())
	print(score)
	return score

def compute_sat_links(city_pairs_chosen):
	chosen_sat_list = {}
	all_sat = [ x for x in range(1601)]
	overflow_sat_list = []
	chosen_isls = []
	for i in all_sat:
		chosen_sat_list[i] = 0
	for city_pair in city_pairs_chosen:
		city1 = city_pair['city_1'] #city1 ID  
		city2 = city_pair['city_2'] #city2 ID
		

		all_sat[-1] = city1

		#print("city1: %s, city2: %s" %(city1, city2))
		city1_coverage =[ sat for sat in city_coverage[str(city1)] ]# a list of sat that city1 covers
		city2_coverage = [ int(sat) for sat in city_coverage[str(city2)] ]

		next_sat_list = city1_coverage[:]
		path_chosen = []
		path_length = {}

		previous_node = city1
		current_path = [previous_node]
		
		while True:
			#for k in range(2):	
			for next_sat in next_sat_list:
				# firxt time
				current_path_length = 0
				next_sat_to_city_dist = compute_sat_city_length(int(next_sat), int(city2), sat_positions, city_positions)
				#print("next_sat:%s, next_sat to destination dist: %s \n" %(next_sat, next_sat_to_city_dist))
				if previous_node == city1:
					#current_path_length = city_coverage[str(city1)][str(next_sat)] + next_sat_to_city_dist
					print("previous_node is city")
				else: #both previous node is a satellite
					isl_length = util.compute_isl_length(int(previous_node), int(next_sat), sat_positions)
					if isl_length > MAX_ISL_LENGTH:
						continue
					#current_path_length = isl_length + next_sat_to_city_dist
					#print("current_path_length of last isls: %s and current_path_length: %s\n" %(isl_length, current_path_length))
				path_length[next_sat_to_city_dist] = int(next_sat)


			min_path_length = min([path for path in path_length.keys()])
			chosen_sat = path_length[min_path_length]
			#print("chosen_sat: %d" %(chosen_sat))

			if (chosen_sat in city2_coverage) and (current_path[-1] == city1):
				#print("two cities are only one sat apart") #no need to update isls or chosen sat
				current_path.append(chosen_sat)
				path_length.clear()
				break
			if current_path[-1] == city1:
				#print("update path but no need to update chosen sat links or chosen sat counts\n")
				current_path.append(chosen_sat)
			elif ((current_path[-1], chosen_sat) in chosen_isls) or ((chosen_sat, current_path[-1]) in chosen_isls): #chosen path is already there
				#print("chosen isls :%s and current isl in examination is :%s\n" %(chosen_isls, ",".join([str(current_path[-1]), str(chosen_sat)])))
				current_path.append(chosen_sat)
				#print("chosen isl already exist\n")
			elif (chosen_sat_list[current_path[-1]] < 4) and (chosen_sat_list[chosen_sat] <4): #chosen isl not there, check if could be a valid isl
				chosen_isls.append((current_path[-1], chosen_sat))
				chosen_sat_list[current_path[-1]] += 1
				chosen_sat_list[chosen_sat] +=1
				current_path.append(chosen_sat)
				#print("adding chosen isls and update chosen sat list\n")
				if int(current_path[-1]) in city2_coverage:
					#print("In the radar")
					path_length.clear()
					break
			elif (chosen_sat_list[current_path[-1]] >= 4):
				if (current_path[-1] not in overflow_sat_list):
					overflow_sat_list.append(current_path[-1])
					#print("update overflow list, add current_path[-1] %s\n" %(current_path[-1]))
				#remove previous node
				del current_path[-1]
				#print("delete last item in the list, current path is :%s\n" %(current_path))

			if chosen_sat_list[chosen_sat] >= 4 and (chosen_sat not in overflow_sat_list):
				overflow_sat_list.append(chosen_sat)
				#print("append chosen_sat %d to overflow list and the list is now: %s\n" %(chosen_sat, overflow_sat_list))

			path_length.clear()
			next_sat_list = set(all_sat) - set(current_path) - set(overflow_sat_list) 
			#print("next_sat_list: %s" %(next_sat_list))
			previous_node = current_path[-1]
			#print("previous_node: %s, current_path:%s\n" %(previous_node, current_path))

		print("final chosen path for %s and %s is %s\n" %(city1,city2,current_path))

	for sat in chosen_sat_list:

		if chosen_sat_list[sat] > 4:
			print ("ERROR")

	with open("../output_data/sat_links.txt", 'w') as file:
		for isl in chosen_isls:
			sat1 = isl[0]
			sat2 = isl[1]
			file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, sat_positions))])))
	return


city_pairs = util.read_city_pair_file("../input_data/city_pairs.txt")
ranked_city_pairs = [x for x in city_pairs.values()] # each element is a dictionary city1: city2: geo_dist
# ranked_city_pairs.sort(key=take_third, reverse=True)
# PermuteCount = 3
# permute_city_pairs_partial = list(itertools.permutations(ranked_city_pairs[:PermuteCount]))

ShuffleCount = 20
score_board = {}
ranked_city_pairs_dic = {}
# for i in range(len(permute_city_pairs_partial)):
# 	permute_city_pairs = list(permute_city_pairs_partial[i])
# 	permute_city_pairs.extend(ranked_city_pairs[PermuteCount:])
# 	compute_sat_links(permute_city_pairs)
# 	score_board[i] = check_score()

min_score_a = 0
min_city_pairs=[]

for i in range(ShuffleCount):
	random.shuffle(ranked_city_pairs)
	compute_sat_links(ranked_city_pairs)

	score_board[i] = check_score()
	if i == 0:
		min_score_a = score_board[i]
		min_city_pairs = ranked_city_pairs[:]
	if score_board[i] < min_score_a:
		min_score_a = score_board[i]
		with open("../output_data/city_file","w") as city_file:
			city_file.write("%s\n" % (ranked_city_pairs))
		min_city_pairs = ranked_city_pairs[:]

score_board_values = [x for x in score_board.values()]
min_score = min(score_board_values)

print("min_score: %f and min_score_a: %s and score_board : %s\n" %(min_score, min_score_a,score_board_values ))

# print("min_city_pairs: %s\n" %(min_city_pairs))
compute_sat_links(min_city_pairs)
print("final min score : %f" %(check_score()))





			





