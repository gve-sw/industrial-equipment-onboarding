import requests
from lxml import etree 

url = "https://198.19.10.27:9060/ers/config/endpoint"
requests.packages.urllib3.disable_warnings()

headers = {
    'accept': "application/vnd.com.cisco.ise.identity.endpoint.1.0+xml"
    }

user = 'ERSAdmin'
pwd = 'C1sco12345'

response = requests.request("GET", url, auth=(user,pwd), headers=headers, verify=False)

#print(response.text)
root = etree.fromstring(str(response.text))
for resources in root:
	for resource in resources:
		a =resource.attrib
		print a['id']



#print etree.tostring(root, pretty_print=True)