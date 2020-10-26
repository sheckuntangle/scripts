printf "UID: "; cat /usr/share/untangle/conf/uid &&
printf "Hostname: "; hostname &&
printf "Version: "; dpkg -l untangle-vm | awk '/^ii/ {print $3}'
printf "Serial: "; cat /sys/devices/virtual/dmi/id/product_serial
printf "HttpPort: "; grep -i httpport /usr/share/untangle/settings/untangle-vm/network.js | awk '{print $2}'
printf "HttpsPort: "; grep -i httpsport /usr/share/untangle/settings/untangle-vm/network.js | awk '{print $2}'
printf "OpenVPN Certificate: "; openssl x509 -text -in /usr/share/untangle/settings/openvpn/server.crt | awk '/Signature Algorithm:/ {print $3 ; exit}'
