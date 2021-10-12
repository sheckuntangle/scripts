#!/bin/bash

#mv pve-enterprise to .old
mv /etc/apt/sources.list.d/pve-enterprise.list...http://download.proxmox.com/debian/pve buster pve-no-subscription' >> /etc/apt/sources.list

#update
apt-get update

#install ifupdown2 (allows networks to be created without rebooting
apt-get install ifupdown2 -y

#upgrade and dist-upgrade
apt-get upgrade -y && apt-get dist-upgrade -y
