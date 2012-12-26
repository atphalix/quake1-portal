#!/bin/sh

# compile a q1 map from Q3A format 

map=$2
type=$1

#mapconvert="g:/quake/id1/utils/mapconvertor/mapconv.exe"
mapconvert="java -jar g:/quake/id1/utils/javamapconvert/mapcon.jar -q1 -chars -groups"
qbsppath="g:/quake/id1/utils/compilers/Qbsp.exe"
vispath="g:/quake/id1/utils/compilers/Vis.exe"
radpath="g:/quake/id1/utils/compilers/tyrlite.exe"
mapworkpath="g:/quake/id1/utils/working/q1maps"
idmappath="g:/quake/id1/maps"
quakepath="g:/quake"
batchfile="industri.bat"
debugapp="debug.bat"

# ----------------------
# functions
leaked () {

	echo "============================="
	echo " Map has a LEAKED!!!!!!!!!!!"
	echo "============================="
	echo -n "Run the game with a LEAKED map? (y/n)[n]"
	read ans
	if [ "$ans" = "n" -o "$ans" = "" ] 
	then
		exit 1
	else
		mv -fv "$mapworkpath/q1$map.bsp" "$idmappath/q1$map.bsp"
		cp -fv "$mapworkpath/q1$map.pts" "$idmappath/q1$map.pts"
		debugMap	
	fi
}

debugMap () {
	echo "---- debug the map ---"
	thisPath=`pwd`
	cd "$quakepath" 
	./$debugapp q1$map
	cd $thisPath
	exit 0
}

startGame () {
	echo "---------------------"
	echo -n " Starting map in "
	i=3
	while [ $i -ne 0 ]
	do
		echo -n ".$i"
		sleep 1
		i=`expr $i - 1`
	done
	#echo "---- start the map ---"
	thisPath=`pwd`
	cd "$quakepath" 
	./$batchfile q1$map
	cd $thisPath
	exit 0
}

# some help to get started 
usage () {

	echo "$0 [compile type | clean-up] [map file]"
	echo ""
	echo "'compile type' can be;"
	echo " ents  : qbsp -entsonly"
	echo " qbsp  : qbsp, then stop"
	echo " fast  : rvis -fast"
	echo " full  : rvis -level 4"
	echo ""
	echo "'clean up' can be:"
	echo " notbak : Remove all temp files except *.map and *.bak"
	echo " store  : Move all temp files except *.map to ./BAK/" 
	echo " all    : Remove all temp files except *.map"
	echo ""
	echo "Example: To do a full compile of 'MyMap.map'"
	echo " $0 full MyMap"
}

# end functions
# ------------------

# check that mapper has set there tool paths
if [ "$mapworkpath" = "" ]
then
	echo "Open this file in a text editor and edit the tool paths"
 	echo "before anything else."	
	exit 0
fi

if [ "$type" = "notbak" -o "$type" = "store" -o "$type" = "all" ] 
then	# its a clean up
	if [ "$type" = "store" ]
	then # only mv the files
		if [ ! -d $mapworkpath/BAK  ]
		then
			mkdir $mapworkpath/BAK 
			if [ ! -d $mapworkpath/BAK ]
			then	# can not make folder, so exit
				echo "I can not make a back-up folder to store the file in, sorry."
				echo "The folder I want to make is called:"
				echo "  $mapworkpath/BAK"
				echo ""
				echo "Maybe you can make it for me?"
				echo "-----"
				exit 1
			fi
		fi	
		#folder is here, mv the files
		mv -fv $mapworkpath/*.h1 $mapworkpath/BAK/ 
		mv -fv $mapworkpath/*.h2 $mapworkpath/BAK/  
		mv -fv $mapworkpath/*.prt $mapworkpath/BAK/ 
		mv -fv $mapworkpath/*.pts $mapworkpath/BAK/ 
		mv -fv $mapworkpath/*.bak $mapworkpath/BAK/ 
		echo "-----"
		echo "Finished clean up, files now found in:"
		echo " $mapworkpath/BAK/"
		echo "-----"
		exit 1

	else	# its a clean out 
		rm -fv  $mapworkpath/*.h1 
		rm -fv  $mapworkpath/*.h2 
		rm -fv  $mapworkpath/*.prt 
		rm -fv  $mapworkpath/*.pts 
		if [ $type = "all" ]
		then
			rm -fv  $mapworkpath/*.bak 
		fi
		echo "-----"
		echo "Finished clean, files have been removed"
		echo "-----"	
		exit 0
	fi
fi

if [ "$map" = "" ]
then
	usage
	exit 1
fi

echo "--------------------"
echo "starting a $type compile of $map"
echo "--------------------"
echo ""

$mapconvert "$mapworkpath/$map.map" "$mapworkpath/q1$map.map"

echo "--------------------"
echo "map converted to q1$map.map, starting qbsp"
echo "--------------------"
if [ "$type" = "ents" ]
then
	# need the bsp if its ents only compile
	mv -fv "$idmappath/q1$map.bsp" "$mapworkpath/q1$map.bsp" 
	./$qbsppath -verbose -onlyents "$mapworkpath/q1$map.map"
	mv -fv "$mapworkpath/q1$map.bsp" "$idmappath/q1$map.bsp"
	
	startGame	

	exit 0 
else
	#./$qbsppath -verbose -alternateaxis -leakspace 2 "$mapworkpath/q1$map.map"
	./$qbsppath -verbose -transwater -oldaxis "$mapworkpath/q1$map.map"
fi

if [ -s "$mapworkpath/q1$map.pts" ]
then # its a leaked file, do not go further
	leaked	
fi 

if [ "$type" = "qbsp" ]
then
	# exit after qbsp
	echo "-----------------"
	echo "QBSP only compile finished"
	echo "-----------------"
	exit 
fi

echo "--------------------"
echo "QBSP finished, starting light pass"
echo "--------------------"
if [ "$type" = "fast" ]
then
	./$radpath "$mapworkpath/q1$map.bsp"
else
	./$radpath -extra "$mapworkpath/q1$map.bsp"
fi

echo "--------------------"
echo "Light finished, vis ($type) starting"
echo "--------------------"
if [ "$type" = "full" ]
then
	./$vispath -level 4 "$mapworkpath/q1$map.bsp"
else
	./$vispath -fast "$mapworkpath/q1$map.bsp"
fi

echo "--------------------"
echo "vis finished, cleaning up now"
echo "--------------------"
mv -fv "$mapworkpath/q1$map.bsp" "$idmappath/q1$map.bsp"


if [ -s $idmappath/q1$map.bsp ]
then
	startGame

else
	echo "Compile problem, will not start the game"
	exit 0
fi



