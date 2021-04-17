cp /etc/nano/sources.list > /etc/nano/sources.list.old
touch /etc/nano/sources.list
echo 'deb http://deb.debian.org/debian buster main contrib non-free' >> /etc/nano/sources.list
echo 'deb-src http://deb.debian.org/debian buster main contrib non-free' >> /etc/nano/sources.list
apt-get update
apt-get install qemu-guest-agent
rm /etc/nano/sources.list 
mv /etc/nano/sources.list.old /etc/nano/sources.list
rm /usr/share/untangle/conf/uid
