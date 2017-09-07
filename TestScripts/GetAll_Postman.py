import requests
from lxml import etree 

url = "https://198.19.10.27:9060/ers/config/endpoint"
requests.packages.urllib3.disable_warnings()

headers = {
    'authorization': "Basic RVJTQWRtaW46QzFzY28xMjM0NQ==",
    'accept': "application/vnd.com.cisco.ise.identity.endpoint.1.0+xml",
    'cache-control': "no-cache",
    'postman-token': "7ed70337-a701-9550-d5f1-73f8a9f3bf69"
    }

response = requests.request("GET", url, headers=headers, verify=False)

#print(response.text)
root = etree.fromstring(str(response.text))
for resources in root:
	for resource in resources:
		a =resource.attrib
		print a['id']



#print etree.tostring(root, pretty_print=True)