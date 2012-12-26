# convert *tga in directory to *jpg using imagemagick
# usge: ./convert.sh [directory path]
# $1 is the dir path
# $1 is image format

for img in $1*$2; do
   base=`basename $img .$2`
   echo "converting "$img
   convert $img $1$base.jpg
done
