#!/usr/bin/env python3
#
# This script attempts to read the current network settings file,
# determines the current http and https service ports, and then
# checks to see if there are any port forwards for those ports
#
import json
import urllib.request
import urllib3

def check_condition(conditions_list, conditionType, invert, value):
    for condition in conditions_list:
        if condition['conditionType'] == conditionType and \
           condition['invert'] == invert and \
           condition['value'] == value:
               return True

    return False

def check_port(forward, port):
    if forward['enabled'] and \
       check_condition(forward['conditions']['list'], "DST_PORT", False, str(port)) and \
       check_condition(forward['conditions']['list'], "PROTOCOL", False, "TCP") and \
       check_condition(forward['conditions']['list'], "DST_LOCAL", False, "true"):
           return True

    return False

def main():
    with open('/usr/share/untangle/settings/untangle-vm/network.js', 'r') as network_settings_json:
        network_settings = json.load(network_settings_json)
        http_port = network_settings['httpPort']
        https_port = network_settings['httpsPort']
        for forward in network_settings['portForwardRules']['list']:
            if check_port(forward, http_port):
                   print("Port forward on HTTP port " + str(http_port) + " found")
            if check_port(forward, https_port):
                   print("Port forward on HTTPS port " + str(https_port) + " found")

if __name__ == "__main__":
    main()
