#
#       
#        Dan Kirkwood (dkirkwoo@cisco.com) & Hantzley Tauckoor (htauckoo@cisco.com)
#       August 2017
#
#       This application uses a Spark chat interface to update the MAC Authentication Bypass (MAB) database in ISE
#       
#
#   REQUIREMENTS:
#       ISE Deployment
#        Flask - flask.pocoo.org
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
Settings: Settings file containing: 
    ISE server IP
    ISE ERS username
    ISE ERS password
    Spark Room ID
    Spark Bot token
    Spark Bot ID
google.cloud.vision: For image recognition
logging: for debug

"""


from flask import Flask, request, session, redirect 
import json
from ISEAPI import SparkAPI
from ISEAPI import ISEAPI
import re
import io
import os
import requests
import settings
from google.cloud import vision
from google.cloud.vision import types
import logging
import pymongo
from pymongo import MongoClient
logging.basicConfig(level=logging.DEBUG)


# Assign variables from settings file
server = settings.server
username = settings.username
password = settings.password

#roomID = settings.roomID
botToken = settings.botToken
botID = settings.botID

# DNS address of the mongo DB with default port of 27017
mongoAddr = 'database:27017'


# Invoke ISEAPI class giving the server IP, username and password
ISEReq = ISEAPI(server, username, password)

# Invoke Spark API giving the Room that will be used and the Spark Token for the Bot
sparkCall = SparkAPI(botToken)

# Check input to ensure it is a valid 48bit hexadecimal MAC address. Valid delimiters are : , . and -
maccheck = re.compile('([0-9A-Fa-f]{2}[:.-]){5}([0-9A-Fa-f]{2})')
oldCheck = re.compile('old')
newCheck = re.compile('new')
helpCheck = re.compile('help')

# Create variable for the file which will be downloaded from Spark
filename = None

client = MongoClient(mongoAddr)

stateDB = client.stateDB
stateTable = stateDB.stateTable







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


def grabImage(messageDict, roomID):

    image_is_in_Spark = True
    headers = {
        'authorization': "Bearer " + botToken,
        'cache-control': "no-cache"
    }
    imageUrl = messageDict['files'][0]
    response = requests.request("GET", imageUrl, headers=headers)
    if response.status_code == 200:

        # Image is in Spark, filename is retrieved from headers
        imgHeaders = response.headers
        print (imgHeaders)

        if 'image' in imgHeaders['Content-Type']:
            # Strip extra data to record just the file name
            filename = imgHeaders['Content-Disposition'].replace("attachment; ", "").replace('filename', '').replace('=', '').replace('"', '')
            # Download the file locally
            with open(filename, 'wb') as f:
                print ('writing file...')
                os.chmod(filename, 0o777)
                f.write(response.content)
            print ("\n\nDetecting MAC address from downloaded image:")
            detectedMac = (detect_mac_address(filename))
            return detectedMac

        else:
            payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"This does not appear to be a valid image.\"\n}"
            sparkCall.POSTMessage(payload)
            return "OK"


# Function which takes a Mac Address, ensures it is formatted correctly and checks if it exists in the current ISE deployment
def oldMacCheck(justText, roomID):
    
    # Regex check    
    macFind = maccheck.search(justText)

    if macFind:


        oldMac = macFind.group(0)
        # Take input MAC and transform to data that ISE will accept
        transMac = ISEReq.MacTransform(oldMac)
        print (transMac)
        # Get all endpoints currently in ISE database
        root = ISEReq.GetAllEndpoints()
        deviceFound = False
        deviceDict = {}

        for endpoint in root['SearchResult']['resources']:
            deviceDict[endpoint['name']] = endpoint['id']

        """
        for resources in root:
            for resource in resources:
                a =resource.attrib
                deviceDict[a['name']] = a['id']
        """
        # Check if input MAC exists in ISE
        if transMac in deviceDict:
            print (transMac)
            deviceID = deviceDict[transMac]
            # Use the Device ID to find detailed information about the old device, to be used to help enter the new device
            oldDeviceInfo = ISEReq.GetEndpointByID(deviceID)    
            data = oldDeviceInfo

            #Remove any prior entries in the DB to ensure only one state at a time
            stateDB.stateTable.delete_many({})

            #Add the detail about the old device to the DB
            stateTable.insert_one(data)
            """
            with io.open('data.json', 'w', encoding='utf8') as outfile:
                str_ = json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
                outfile.write(str_)
            """

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
        # Inform user that they have not input a valid MAC address
        payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"The MAC address you have typed does not appear to be valid. Please ensure you enter 12 hexadecimal characters in pairs separated by ':'' , '.'' or '-'. For example aa:bb:cc:11:22:33\"\n}"

        sparkCall.POSTMessage(payload)

# Takes MAC address, creates new endpoint in ISE deployment copying all other data from existing endpoint
def newMacCreate(justText, oldDeviceID, oldGroupID, oldProfileID, roomID):
    #newmac = macAddress
    # Regex check
    macFind = maccheck.search(justText)

    if macFind:
    #if maccheck.match(newmac):
        newmac = macFind.group(0)
        # Transform MAC into format that ISE prefers
        newmac = ISEReq.MacTransform(newmac)
        # Create XML describing new device, with select data pulled from the old device
        newDeviceInfo = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<ns4:endpoint description=\"description\" id=\"id\" name=\"name\" xmlns:ers=\"ers.ise.cisco.com\" xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" xmlns:ns4=\"identity.ers.ise.cisco.com\">\n    <groupId>"+str(oldGroupID)+"</groupId>\n    <identityStore></identityStore>\n    <identityStoreId></identityStoreId>\n    <mac>"+newmac+"</mac>\n    <portalUser></portalUser>\n    <profileId>"+str(oldProfileID)+"</profileId>\n    <staticGroupAssignment>true</staticGroupAssignment>\n    <staticProfileAssignment>true</staticProfileAssignment>\n</ns4:endpoint>"
        # Call ISE API to create endpoint
        doCreate = ISEReq.CreateEndpoint(newDeviceInfo)

        if doCreate == True:
            # If the create function was successful, remove the old device
            deleter = ISEReq.DeleteEndpoint(oldDeviceID)
            payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"Device with MAC "+newmac+" can now access the network.\"\n}"
            sparkCall.POSTMessage(payload)
            #os.remove('data.json')                
            return "OK"

    else:
        # Inform user that the MAC address was not input correctly
        payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \""+newmac+" does not appear to be a valid MAC address. Please ensure you enter 12 hexadecimal characters in pairs separated by ':'' , '.'' or '-'. For example aa:bb:cc:11:22:33\"\n}"

        sparkCall.POSTMessage(payload)

        return "OK"


# Flask used as listener for webhooks from Sparkss
app = Flask(__name__)

@app.route('/',methods=['POST'])
def listener():
    # On receipt of a POST (webhook), load the JSON data from the request
    data = json.loads(request.data)
    print (data)
    messageID = data['data']['id']
    roomID = data['data']['roomId']
    print (roomID)
    # If the poster of the message was NOT the bot itself
    if data['actorId'] != botID:

        
        # Get more specific information about the message that triggered the webhook
        message = sparkCall.GETMessage(messageID)

        messageDict = json.loads(message)
        print (messageDict)
 
        justText = messageDict['text']

        if oldCheck.search(justText):

            if 'files' not in messageDict:
                oldMacCheck(justText, roomID)


            elif 'files' in messageDict:
                detectedMac = grabImage(messageDict, roomID)

                if detectedMac == False:
                    # If the image recognition did not find a MAC, inform the user
                    payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"No MAC address detected in image.\"\n}"
                    sparkCall.POSTMessage(payload)

                    return "OK"

                else:
                    oldMacCheck(detectedMac, roomID)




        elif newCheck.search(justText):

            if 'files' not in messageDict:

                dataCheck = stateTable.find_one()
                if dataCheck is not None:
                    data_loaded = dataCheck
                #if os.path.isfile('data.json') == True:
                    # If so, load the specific 
                #    with open('data.json') as data_file:
                #        data_loaded = json.load(data_file)
                # Otherewise, inform the user that they need to enter the MAC of the old device
                else:
                    payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"You have not yet entered data on the device you would like to replace. Identify the old device using \'old AA:BB:CC:11:22:33\'\"\n}"

                    sparkCall.POSTMessage(payload)

                    return "OK"                    

                # Load specific data from the old device that will be used to set up the new device with the same parameters
                oldDeviceID = data_loaded["ERSEndPoint"]["id"]
                oldGroupID = data_loaded["ERSEndPoint"]["groupId"]
                oldProfileID = data_loaded["ERSEndPoint"]["profileId"]

                # Use the new MAC with the information from the old device to create the new device
                newMacCreate(justText, oldDeviceID, oldGroupID, oldProfileID, roomID)


            elif 'files' in messageDict:
                detectedMac = grabImage(messageDict, roomID)

                dataCheck = stateTable.find_one()
                if dataCheck is not None:
                    data_loaded = dataCheck

                # Otherewise, inform the user that they need to enter the MAC of the old device
                else:
                    payload = "{\n  \"roomId\" : \""+roomID+"\",\n  \"text\" : \"You have not yet entered data on the device you would like to replace. Identify the old device using \'old AA:BB:CC:11:22:33\'\"\n}"

                    sparkCall.POSTMessage(payload)

                    return "OK"                    

                # Load specific data from the old device that will be used to set up the new device with the same parameters
                
                oldDeviceID = data_loaded["ERSEndPoint"]["id"]
                oldGroupID = data_loaded["ERSEndPoint"]["groupId"]
                oldProfileID = data_loaded["ERSEndPoint"]["profileId"]

                # Use the new MAC with the information from the old device to create the new device
                creator = newMacCreate(detectedMac, oldDeviceID, oldGroupID, oldProfileID, roomID)


        elif helpCheck.search(justText):

            botDetails = sparkCall.GETPerson(botID)
            botDetailsDict = json.loads(botDetails)

            botName = botDetailsDict['displayName']

            helpmsg = "Do you need to get a device onto the network? I can help! \
            \n Simply first tell me the MAC address of the device you are replacing, and then the MAC address of the new device. \
            \n\n For example: **_@"+botName+" old 11:22:33:44:55:66_** \
            \n\n You can also take a picture of the MAC address label on your device! Simply put it in this room addressed to @"+botName+" and make sure you let me know whether it is the old or new device. \
            \n Having problems? Check out my [\[GitHub\]](https://github.com/cisco-gve/industrial-equipment-onboarding) "
            
            payload = {"roomId":roomID,"markdown":helpmsg}
            sparkCall.POSTMarkdownMessage(payload)

        else:
            emptyMsg = "Hi! Looks like you are trying to use me but dont know how. \
            \n Type help for some help!"
            
            payload = {"roomId":roomID,"markdown":emptyMsg}
            sparkCall.POSTMarkdownMessage(payload)            


# Runs the listener on port 808
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

