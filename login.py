printf "UID: "; cat /usr/share/untangle/conf/uid &&
printf "Hostname: "; hostname &&
printf "Version: "; dpkg -l | awk '{print $2 "  :  " $3  }' | grep untangle-vm
printf "Serial: "; cat /sys/devices/virtual/dmi/id/product_serial
printf "OpenVPN Certificate: "; openssl x509 -text -in /usr/share/untangle/settings/openvpn/server.crt | grep "Sig"
