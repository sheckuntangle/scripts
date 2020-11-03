import json

with open('/usr/share/untangle/settings/untangle-vm/network.js') as jasondata:
    data = json.load(jsondata) 

for attrs in data()['portForwardRules']['list']['conditions']['list']:
    if item['value'] == "443":

else:
    print('Port Forward on 443 Found')
