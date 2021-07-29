#!/bin/bash

# rename sources.list
mv /etc/apt/sources.list /etc/apt/sources.list.copy

# add debian sources
echo -e "deb http://deb.debian.org/debian buster main\ndeb-src http://deb.debian.org/debian buster main" > /etc/apt/sources.list

# install 
apt-get update
apt-get install sysstat -y

# remove new sources file put original back
rm /etc/apt/sources.list
mv /etc/apt/sources.list.copy /etc/apt/sources.list
