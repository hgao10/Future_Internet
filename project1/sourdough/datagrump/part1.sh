echo "" > score_part1
for ((n=10; n<20; n+=2));
do 
	echo "#define WINDOW_SIZE $n" > windowsize.hh
	make
	printf "$n \n" >> score_part1
	for ((i=0; i<1; i +=1));
	do 
		./run-contest >> score_part1 2>&1
	done
done
