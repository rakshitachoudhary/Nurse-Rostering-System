N=$1
D=$1

for m in `seq 0 $N`
do
	for a in `seq 0 $N`
	do
		for e in `seq 0 $N`
		do
			if [ $N -gt `expr $m + $a + $e` ]; then
				printf "N,D,m,a,e\n$N,$D,$m,$a,$e" > gen.csv
				printf "$m $a $e\n"
				python A2.py gen.csv > /dev/null
				python checker.py solution.json gen.csv
				python format_checker.py
			fi
		done
	done
done
