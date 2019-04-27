try:
    from . import util
except (ImportError, SystemError):
    import util
#set_sat_links

satPositions = {}
satPositions = util.read_sat_positions("../input_data/sat_positions.txt")

with open("../output_data/sat_links.txt", 'w') as file:
	# 40 satellites per orbit, 40 orbits
	for i in range(40):
		#in each orbit, connect neighboring satellites, 0 -> 1, 1 -> 2
		for j in range(40):
			sat1 = i*40+j
			sat2 = i*40+j+1
			if (j==39):
				sat2 = i*40
			file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))])))

	# connect to orbit k -1
	for k in range(1,40):
		for l in range(40):
			sat1 = k*40 + l
			sat2 = (k-1)*40 + l
			file.write("%s\n" %(",".join([str(sat1), str(sat2), str(util.compute_isl_length(sat1, sat2, satPositions))])))


