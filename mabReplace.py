#
#   Dan Kirkwood (dkirkwoo@cisco.com)
#       August 2017
#
#       This application uses a Spark chat interface to update the MAC Authentication Bypass (MAB) database in ISE
#       
#
#   REQUIREMENTS:
#       ISE Deployment
#		Flask - flask.pocoo.org
#       Spark account with Bot created. See https://developer.ciscospark.com
#
#   WARNING:
#       This script is meant for educational purposes only.
#       Any use of these scripts and tools is at
#       your own risk. There is no guarantee that
#       they have been through thorough testing in a
#       comparable environment and we are not
#       responsible for any damage or data loss
#       incurred with their use.
#      


"""
Imports
Flask: Listener for webhooks from Spark
json: Manage data from Spark
ISEAPI: Generic API calls for ISE and Spark
re: Regex for checking input towards Spark
io: Store MAC data in local file
os: Check if previous data exists
readSettings: File defining local settings used to run program. See readSettings.py
"""

import requests
from flask import Flask, request, session, redirect 
import json
from ISEAPI import SparkAPI
from ISEAPI import ISEAPI
import re
import io
import os
import settings
from google.cloud import vision
from google.cloud.vision import types
import logging
logging.basicConfig(level=logging.DEBUG)

"""
Load settings from local text file
Requires the following, separated by a new line each:
	ISE server IP
	ISE ERS username
	ISE ERS password
	Spark Room ID
	Spark Bot token
	Spark Bot ID

setList = readSettings.loadSettings("settings.txt")

server = setList[0].rstrip()
username = setList[1].rstrip()
password = setList[2].rstrip()

roomID = setList[3].rstrip()
botToken = setList[4].rstrip()
botID = setList[5].rstrip()
"""

server = settings.server
username = settings.username
password = settings.password

roomID = settings.roomID
botToken = settings.botToken
botID = settings.botID

# Invoke ISEAPI class giving the server IP, username and password
ISEReq = ISEAPI(server, username, password)

sparkCall = SparkAPI(roomID, botToken)

# Check input to ensure it is a valid 48bit hexadecimal MAC address. Valid delimiters are : , . and -
maccheck = re.compile('^([0-9A-Fa-f]{2}[:.-]){5}([0-9A-Fa-f]{2})$')

filename = None


def detect_mac_address(path):
    """Detects MAC address in the file."""
    client = vision.ImageAnnotatorClient()
    MAC = False

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    for text in texts:
        #Match MAC addresses in format aa:bb:cc:dd:ee:ff or aa-bb-cc-dd-ee-ff
        match_regex = re.compile('^' + '[\:\-]'.join(['([0-9A-F]{1,2})']*6) + '$', re.IGNORECASE)
        mac_addresses = match_regex.findall(text.description)
        if len(mac_addresses) > 0:
            MAC = ':'.join(mac_addresses[0])
        else:
            #Match MAC addresses in format aabbccddeeff
            match_regex = re.compile('^' + '([0-9A-F]{2})'*6 + '$', re.IGNORECASE)
            mac_addresses = match_regex.findall(text.description)
            if len(mac_addresses) > 0:
                MAC = ':'.join(mac_addresses[0])

    return MAC



# Function which takes a Mac Address, ensures it is formatted correctly and checks if it exists in the current ISE deployment
def oldMacCheck(macAddress):
	oldMac = macAddress
	# Regex check	
	if maccheck.match(oldMac):
		# Take input MAC and transform to data that ISE will accept
		transMac = ISEReq.MacTransform(oldMac)
		# Get all endpoints currently in ISE database
		root = ISEReq.GetAllEndpoints()
		deviceFound = False
		deviceDict = {}
		for resources in root:
			for resource in resources:
				a =resource.attrib
				deviceDict[a['name']] = a['id']
		# Check if input MAC exists in ISE
		if transMac in deviceDict:
			deviceID = deviceDict[transMac]
			# Use the Device ID to find detailed information about the old device, to be used to help enter the new device
			oldDeviceInfo = ISEReq.GetEndpointByID(deviceID)	
			data = oldDeviceInfo
			with io.open('data.json', 'w', encoding='utf8') as outfile:
				str_ = json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
				outfile.write(str_)				
			payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"Device found with MAC "+transMac+". Please enter the MAC address of the new device being installed.\"\n}"
			sparkCall.POSTMessage(payload)

			# Return HTTP OK code to the webhook to inform that the request was successful
			return "OK"
		else:
			#return 'NOTFOUND'
			payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"The MAC address "+oldMac+" was not found in the ISE database. Please check the address again or contact your IT department.\"\n}"

			sparkCall.POSTMessage(payload)

			return "OK"
				

	else:
		#return 'NOTMAC'
		payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \""+oldMac+" does not appear to be a valid MAC address. Please ensure you enter 12 hexadecimal characters in pairs separated by ':'' , '.'' or '-'. For example aa:bb:cc:11:22:33\"\n}"

		sparkCall.POSTMessage(payload)

# Takes MAC address, creates new endpoint in ISE deployment copying all other data from existing endpoint
def newMacCreate(macAddress, oldDeviceID, oldGroupID, oldProfileID):
	newmac = macAddress
	# Regex check
	if maccheck.match(newmac):
		# Transform MAC into format that ISE prefers
		newmac = ISEReq.MacTransform(newmac)
		# Create XML describing new device, with select data pulled from the old device
		newDeviceInfo = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<ns4:endpoint description=\"description\" id=\"id\" name=\"name\" xmlns:ers=\"ers.ise.cisco.com\" xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" xmlns:ns4=\"identity.ers.ise.cisco.com\">\n    <groupId>"+str(oldGroupID)+"</groupId>\n    <identityStore></identityStore>\n    <identityStoreId></identityStoreId>\n    <mac>"+newmac+"</mac>\n    <portalUser></portalUser>\n    <profileId>"+str(oldProfileID)+"</profileId>\n    <staticGroupAssignment>true</staticGroupAssignment>\n    <staticProfileAssignment>true</staticProfileAssignment>\n</ns4:endpoint>"
		# Call ISE API to create endpoint
		doCreate = ISEReq.CreateEndpoint(newDeviceInfo)

		if doCreate == True:
			# If the create function was successful, remove the old device
			deleter = ISEReq.DeleteEndpoint(oldDeviceID)
			payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"Device with MAC "+newmac+" is now authorised to access the network.\"\n}"
			sparkCall.POSTMessage(payload)
			os.remove('data.json')				
			return "OK"

	else:
		#return 'NOTMAC'
		payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \""+newmac+" does not appear to be a valid MAC address. Please ensure you enter 12 hexadecimal characters in pairs separated by ':'' , '.'' or '-'. For example aa:bb:cc:11:22:33\"\n}"

		sparkCall.POSTMessage(payload)

		return "OK"


# Flask used as listener for webhooks from Spark
app = Flask(__name__)

@app.route('/',methods=['POST'])
def listener():
	# On receipt of a POST (webhook), load the JSON data from the request
	data = json.loads(request.data)
	#print data
	messageID = data['data']['id']
	# If the poster of the message was NOT the bot itself
	if data['actorId'] != botID:

		
		# Get more specific information about the message that triggered the webhook
		message = sparkCall.GETMessage(messageID)

		prettymessage = json.loads(message)
		print prettymessage
		

		
		if 'files' not in prettymessage:
			print "not a file :("
			#return "OK"
			
			# Check if the user is describing the old MAC
			if prettymessage["text"][0] in ("O", "o"):
				
				# Grab only the mac address from the message
				macOnly = (prettymessage["text"][4:21])
				
				# Ensure the MAC was entered correctly, and exists in the ISE deployment
				check = oldMacCheck(macOnly)



			elif prettymessage["text"][0] in ("N", "n"):
				# Strip the MAC address from the message
				macOnly = (prettymessage["text"][4:21])

				# Check that the user has already entered information on the old MAC address
				if os.path.isfile('data.json') == True:
					# If so, load the specific 
					with open('data.json') as data_file:
						data_loaded = json.load(data_file)
				# Otherewise, inform the user that they need to enter the MAC of the old device
				else:
					payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"You have not yet entered data on the device you would like to replace. Identify the old device using \'old AA:BB:CC:11:22:33\'\"\n}"

					sparkCall.POSTMessage(payload)

					return "OK"					

				# Load specific data from the old device that will be used to set up the new device with the same parameters
				oldDeviceID = data_loaded["ns4:endpoint"]["@id"]
				oldGroupID = data_loaded["ns4:endpoint"]["groupId"]
				oldProfileID = data_loaded["ns4:endpoint"]["profileId"]

				# Use the new MAC with the information from the old device to create the new device
				creator = newMacCreate(macOnly, oldDeviceID, oldGroupID, oldProfileID)


		elif 'files' in prettymessage:
			#print "this is a file"
			#return "OK"
		

			print 'I found a file!!'
			image_is_in_Spark = True
	        headers = {
	            'authorization': "Bearer " + botToken,
	            'cache-control': "no-cache"
	        }
	        imageUrl = prettymessage['files'][0]
	        response = requests.request("GET", imageUrl, headers=headers)
	        if response.status_code == 200:

	            # Image is in Spark, filename is retrieved from headers
	            imgHeaders = response.headers
	            print (imgHeaders)

	            if 'image' in imgHeaders['Content-Type']:
	                filename = imgHeaders['Content-Disposition'].replace("attachment; ", "").replace('filename', '').replace('=', '').replace('"', '')
	            	print filename
	            	with open(filename, 'wb') as f:
		            	print "writing file..."
		            	os.chmod(filename, 0o777)
		            	f.write(response.content)
		        print ("\n\nDetecting MAC address from downloaded image:")
		        detectedMac = (detect_mac_address(filename))
		        print detectedMac

		        if detectedMac == False:

			        payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"No MAC address detected in image.\"\n}"
			        sparkCall.POSTMessage(payload)

			        return "OK"

		        if prettymessage["text"][0] in ("O", "o"):
		        	check = oldMacCheck(detectedMac)

		        elif prettymessage["text"][0] in ("N", "n"):
				# Check that the user has already entered information on the old MAC address

					if os.path.isfile('data.json') == True:
						# If so, load the specific 
						with open('data.json') as data_file:
							data_loaded = json.load(data_file)
					# Otherewise, inform the user that they need to enter the MAC of the old device
					else:
						payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"You have not yet entered data on the device you would like to replace. Identify the old device using \'old AA:BB:CC:11:22:33\'\"\n}"

						sparkCall.POSTMessage(payload)

						return "OK"					

					# Load specific data from the old device that will be used to set up the new device with the same parameters
					oldDeviceID = data_loaded["ns4:endpoint"]["@id"]
					oldGroupID = data_loaded["ns4:endpoint"]["groupId"]
					oldProfileID = data_loaded["ns4:endpoint"]["profileId"]

					# Use the new MAC with the information from the old device to create the new device
					creator = newMacCreate(detectedMac, oldDeviceID, oldGroupID, oldProfileID)


	            else:
	                #print(str(filename) + " is not an image")

	                payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"this does not appear to be a valid image.\"\n}"
	                sparkCall.POSTMessage(payload)
	                return "OK"

			
		
		else:
			print "how did u get here"
			return "OK"
			
			
				
			"""
			# Check that the create was successful, if so inform the user and delete the local file describing the old device
			if creator == True:
				payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"Device with mac "+macOnly+" is now authorised to access the network.\"\n}"
				sparkCall.POSTMessage(payload)
				os.remove('data.json')				
				return "OK"
			# If the user has entered an incorrect MAC address, inform the user
			elif creator == 'NOTMAC':
				payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \""+macOnly+" does not appear to be a valid MAC address. Please ensure you enter 12 hexadecimal characters in pairs separated by ':'' , '.'' or '-'. For example aa:bb:cc:11:22:33\"\n}"

				sparkCall.POSTMessage(payload)
			"""


# Runs the listener on port 80
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True)

