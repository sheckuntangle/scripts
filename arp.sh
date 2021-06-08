#!/bin/bash
while true
do
 read -r default intf <<<$(ip route show table `grep "uplink" /etc/iproute2/rt_tables | awk '{print $1}'` | awk '{print $3" "$5}')
 wanaddr=$(ip a show dev $intf | grep inet | awk '{print $2}' | awk -F / '{print $1}')
 arping -A -c 2 -I $intf $wanaddr
 arping -c 2 -U $wanaddr -I $intf
 arping -c 2 -s $wanaddr -I $intf $default
 sleep 3600
done
