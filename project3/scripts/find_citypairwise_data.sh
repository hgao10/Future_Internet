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


#For each city pair, compute stretch and hop-count
IFS=","

city_pair_file=$1
isl_file=$2

python get_shortest_path.py $isl_file ../input_data/city_coverage.txt ../input_data/city_pairs.txt >> temp/shortest_paths.txt

while read f1 f2 f3 f4 f5 f6
do
	lat=$(cat temp/shortest_paths.txt| awk -F' ' -v node1="$f1" -v node2="$f2" '{if ((($1 == node1) && ($2 == node2)) || (($1 == node2) && ($2 == node1))) print $0}')
	#echo $lat
	dist=$(echo $lat | awk -F' ' '{print $3}')
	latency=$(echo "scale=2; $dist/300" | bc)

	stretch_shortest_path=$(echo "scale=2; $dist/$f3" | bc)
	#echo $f1" "$f2" "$dist" "$f3" "$stretch_shortest_path
	path_t=$(echo $lat | awk -F'[' '{print $2}')
	path=${path_t::-1}
	IFS=' ' read -a nodes <<< $path
	hopCount_shortest_path=$(echo ${#nodes[@]})
	hopCnt=$(( hopCount_shortest_path - 1 ))
	echo "$f1 $f2 $stretch_shortest_path $hopCnt" >> temp/metrics.txt

done < $city_pair_file

rm temp/shortest_paths.txt
