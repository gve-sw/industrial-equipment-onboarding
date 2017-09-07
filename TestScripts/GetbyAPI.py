from ISEAPI import ISEAPI
import re

server = "198.19.10.27"
username = "ERSAdmin"
password = "C1sco12345"


r = ISEAPI(server, username, password)
maccheck = re.compile('^([0-9A-Fa-f]{2}[:.-]){5}([0-9A-Fa-f]{2})$')

while True:

	oldmac = raw_input("Please enter the MAC address of the device you would like to replace: ")
#	oldmac = "00:50:56:AA:AA:6A"

	if maccheck.match(oldmac):
		
		oldmac = r.MacTransform(oldmac)

		root =r.GetAllEndpoints()

		deviceFound = False

		for resources in root:
			for resource in resources:
				a =resource.attrib
				if ((a['name'])==(oldmac)):
					deviceID = a['id']
					deviceFound = True
					oldDeviceInfo = r.GetEndpointByID(deviceID)

		if deviceFound == False:
			print "\n"			
			print "The MAC address " "\""+oldmac+ "\"" " was not found in ISE database. Please check the address again or contact your IT department."
			print "\n"

		elif deviceFound == True:
			break


	else:
		print "\n"
		print "\""+oldmac+ "\"" " is not a valid MAC address."
		print  "Please ensure you enter 12 hexadecimal characters in pairs separated by ':'' , '.'' or '-'." 
		print "For example aa:bb:cc:11:22:33 "
		print "\n"



print "\n"
print "Device found."
print "\n"

while True:

	newmac = raw_input("Please enter the MAC address of the new device being installed: ")

	if maccheck.match(newmac):

		newmac = r.MacTransform(newmac)
		
		newDeviceInfo = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<ns4:endpoint description=\"description\" id=\"id\" name=\"name\" xmlns:ers=\"ers.ise.cisco.com\" xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" xmlns:ns4=\"identity.ers.ise.cisco.com\">\n    <groupId>"+str(oldDeviceInfo["ns4:endpoint"]["groupId"])+"</groupId>\n    <identityStore></identityStore>\n    <identityStoreId></identityStoreId>\n    <mac>"+newmac+"</mac>\n    <portalUser></portalUser>\n    <profileId>"+str(oldDeviceInfo["ns4:endpoint"]["profileId"])+"</profileId>\n    <staticGroupAssignment>true</staticGroupAssignment>\n    <staticProfileAssignment>true</staticProfileAssignment>\n</ns4:endpoint>"
		
		doCreate = r.CreateEndpoint(newDeviceInfo)

		if doCreate == True:
			r.DeleteEndpoint(deviceID)
			break


	else:
		print "\n"
		print "\""+newmac+ "\"" " is not a valid MAC address."
		print  "Please ensure you enter 12 hexadecimal characters in pairs separated by ':'' , '.'' or '-'." 
		print "For example aa:bb:cc:11:22:33 "
		print "\n"




