cp /etc/apt/sources.list > /etc/apt/sources.list.old
touch /etc/apt/sources.list
echo 'deb http://deb.debian.org/debian buster main contrib non-free' >> /etc/apt/sources.list
echo 'deb-src http://deb.debian.org/debian buster main contrib non-free' >> /etc/apt/sources.list
apt-get update
apt-get install qemu-guest-agent
rm /etc/apt/sources.list 
mv /etc/apt/sources.list.old /etc/apt/sources.list
rm /usr/share/untangle/conf/uid
