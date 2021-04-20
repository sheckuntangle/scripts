#!/bin/bash

#copy sources.list to sources.list.old
cp /etc/apt/sources.list /etc/apt/sources.list.old

#add debian sources
echo 'deb http://deb.debian.org/debian buster main contrib non-free\ndeb-src http://deb.debian.org/debian buster main contrib non-free' >> /etc/apt/sources.list

#update
apt-get update

#install iperf3
apt-get install iperf3 -y

#remove sources
rm /etc/apt/sources.list

#move original sources back
mv /etc/apt/sources.list.old /etc/apt/sources.list
