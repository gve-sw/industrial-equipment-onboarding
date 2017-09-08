



from flask import Flask, request, session
import json
from ISEAPI import SparkAPI
from ISEAPI import ISEAPI
import re



ISEReq = ISEAPI(server, username, password)
maccheck = re.compile('^([0-9A-Fa-f]{2}[:.-]){5}([0-9A-Fa-f]{2})$')


def oldMacCheck(macAddress):
	oldmac = macAddress
	if maccheck.match(oldmac):
		oldmac = ISEReq.MacTransform(oldmac)
		root = ISEReq.GetAllEndpoints()
		print root

		for resources in root:
			for resource in resources:
				a =resource.attrib
				if ((a['name'])==(oldmac)):
					deviceID = a['id']
					oldDeviceInfo = ISEReq.GetEndpointByID(deviceID)
					return oldDeviceInfo
				else:
					return 'NOTFOUND'

	else:
		return 'NOTMAC'


#def newMac()



app = Flask(__name__)

@app.route('/',methods=['POST'])
def listener():
	data = json.loads(request.data)
	messageID = data['data']['id']

	if data['actorId'] != botID:
		sparkCall = SparkAPI(roomID, botToken)
		message = sparkCall.GETMessage(messageID)

		prettymessage = json.loads(message)
		print prettymessage["text"]
		check = oldMacCheck(prettymessage["text"])
		
		if check == 'NOTMAC':
			
			payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"Please ensure you enter 12 hexadecimal characters in pairs separated by ':'' , '.'' or '-'. For example aa:bb:cc:11:22:33.\"\n}"
			#print payload
			sparkCall.POSTMessage(payload)

		elif check == 'NOTFOUND':
			

			payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"The MAC address "+prettymessage["text"]+" was not found in ISE database. Please check the address again or contact your IT department.\"\n}"
			print payload
			sparkCall.POSTMessage(payload)

		else:
			
			payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"Device found. Please enter the MAC address of the new device being installed.\"\n}"
			sparkCall.POSTMessage(payload)


		return "OK"
	else:
		return "OK"








if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)




