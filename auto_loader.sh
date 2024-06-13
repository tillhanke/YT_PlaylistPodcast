#!/bin/zsh

# This script automatically downloads new podcast episodes from the Youtube playlist
# and adds them to the podcast feed.

YTPLAYLIST="https://www.youtube.com/playlist?list=PLNFzXaeUR0EE1qkHn-onByhgrbu8_IiGD"

# this updates the content of cwd to the latest version of the playlist
# only run this if -d arg is set
if [ $# -ge 2 ] && [ $1 == "-d" ];
then
    echo "Downloading latest version of the playlist"
    yt-dlp --yes-playlist -x --audio-format=mp3 --write-info-json $YTPLAYLIST
fi

# create backup of feed.xml
cp feed.xml feed.xml.$(date +%Y%m%d%H).bckp

# this checks, if there are new files, that are not yet in the archive directory, i.e. not in the podcast feed yet
IFS=$'\n'
for MP3YTFILE in $(ls|grep mp3);   
do 
    MP3FILE=$(echo $MP3YTFILE |sed "s/.*\([0-9]\{3\}\) \[.*mp3/\1.mp3/g")
    JSONFILE=$(echo $MP3YTFILE |sed "s/mp3/info.json/g")
    echo "using $MP3FILE $JSONFILE $MP3YTFILE"
    if [ -e archive/$MP3FILE ];
    then 
        echo "File $MP3FILE already in feed";
    else
        echo "Adding $MP3FILE to the podcast feed";
        ./json_to_item.py $JSONFILE || exit 1
        cp $MP3YTFILE archive/$MP3FILE
    fi;
done



