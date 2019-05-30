import os
try:
    from . import util
except (ImportError, SystemError):
    import util
import itertools
import subprocess 
global permute_city_pairs


city_pairs = util.read_city_pair_file("../input_data/city_pairs.txt")
ranked_city_pairs = [x for x in city_pairs.values()] # each element is a dictionary city1: city2: geo_dist

permute_city_pairs_partial = list(itertools.permutations(ranked_city_pairs[:2]))

score_board = {}

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

for i in range(len(permute_city_pairs_partial)):
	permute_city_pairs = list(permute_city_pairs_partial[i])
	permute_city_pairs.extend(ranked_city_pairs[2:])
	
	score_board[i] = check_score()


min_score = min([x for x in score_board.values()])
print("min_score: %f" %(min_score))

	






