#!/bin/bash


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


#USAGE: ./check_score.sh

#File locations
city_file="../input_data/cities.txt"
city_pair_file="../input_data/city_pairs.txt"
sat_positions_file="../input_data/sat_positions.txt"
isl_file="../output_data/sat_links.txt"

#List known values
NUM_ORBITS=40
NUM_SATS_PER_ORBIT=40
MAX_ISL_LENGTH=5014 #km


##########################################################################################
#Verify solution and check score
##########################################################################################
rm -r temp
mkdir temp

#Validate link length for all links
echo "Validating ISL lengths for all ISLs"
python3.6 satellitePairDistanceCalculator.py $sat_positions_file $isl_file >> temp/sat_links_verified.txt
invalidLinks=0
invalidLinksDesc=""
IFS=","
while read f1 f2 f3
do
	if (( $(echo "$f3 > $MAX_ISL_LENGTH" |bc -l) )); then
		invalidLinks=1
		invalidLinksDesc=$invalidLinksDesc""$f1"-"$f2","
		break
	fi
done < temp/sat_links_verified.txt

#Validate ISL constraint (no satellite node should have more than 4 ISLs; each ISL should be with a different satellite)
counter=0
#sats=""
TOTAL_SATS=$(( NUM_ORBITS * NUM_SATS_PER_ORBIT ))
if [ "$invalidLinks" -eq  "0" ]
then
	echo "Checking if any satellite has more than the maximum number of ISLs"
	for (( i=0; i<$TOTAL_SATS; i++ ))
	do
		link_count_1=$(grep "^$i," temp/sat_links_verified.txt | wc -l)
		link_count_2=$(grep ",$i," temp/sat_links_verified.txt | wc -l)
		links=$(( link_count_1 + link_count_2 ))
		if (( links > 4 ))
		then
			counter=$(( counter + 1 ))
			#sats=$sats","$i
		fi
	done
fi
echo "sats with more than 4 links: "$counter

#Compute objective metric
if (( $counter > 0 ))
then
	echo "Number of ISLs exceed 4 for "$counter" sats"
	echo "Number of ISLs exceed 4 for "$counter" sats" >> temp/error.log
elif (( $invalidLinks > 0 ))
then
	echo "Invalid link with length greater than "$MAX_ISL_LENGTH" kms found: "$invalidLinksDesc
	echo "Invalid link with length greater than "$MAX_ISL_LENGTH" kms found: "$invalidLinksDesc >> temp/error.log
else
	echo "Computing shortest paths for each city pair"
	./find_citypairwise_data.sh $city_pair_file temp/sat_links_verified.txt

	city_count=$(cat $city_file| wc -l)
	temp_var=$(( city_count - 1 ))
	temp_var=$(( city_count * temp_var ))
	expected_shortest_path_count=$(( temp_var / 2 ))
	shortest_path_count=$(cat temp/metrics.txt | wc -l)
	if (( $shortest_path_count < $expected_shortest_path_count ))
	then
		echo "Expected number of shortest paths: "$expected_shortest_path_count"; Shortest paths found: "$shortest_path_count
		echo "Expected number of shortest paths: "$expected_shortest_path_count"; Shortest paths found: "$shortest_path_count >> temp/error.log
	else
		city_pair_count=$(cat temp/metrics.txt | wc -l)
		stretch_sum=$(cat temp/metrics.txt | awk '{sum += $3} END {print sum}')
		hopCount_sum=$(cat temp/metrics.txt | awk '{sum += $4} END {print sum}')

		avg_stretch=$(echo "scale=2; $stretch_sum/$city_pair_count" | bc)
		avg_hopCount=$(echo "scale=2; $hopCount_sum/$city_pair_count" | bc)


		METRIC=$(echo "scale=2; 5 * $avg_stretch + $avg_hopCount" | bc)
		echo "Average stretch: "$avg_stretch
		echo "Average hop count: "$avg_hopCount
		echo "Objective function value: "$METRIC
		echo "$avg_stretch,$avg_hopCount,$METRIC" >> temp/results.txt
	fi
fi

