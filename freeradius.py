#script for freeradius

systemctl mask freeradius
/usr/share/untangle/bin/ut-upgrade.py
systemctl unmask freeradius
