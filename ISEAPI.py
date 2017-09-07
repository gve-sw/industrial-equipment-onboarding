#
#   Dan Kirkwood (dkirkwoo@cisco.com)
#       August 2017
#
#       A collection of generic API calls to Cisco Identity Services Engine (ISE) and Spark
#       
#
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

import requests
from lxml import etree
import xmltodict


from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class ISEAPI(object):

	def __init__(self, server, username, password):
		self.server = server
		self.username = username
		self.password = password


	def ISEGETE(self, url, headers):
		"""
		Generic GET request using Etree to parse data
		"""

		try:
			response = requests.request("GET", url, auth=(self.username,self.password), headers=headers, verify=False)
			status_code = response.status_code
			if (status_code == 200):
				root = etree.fromstring(str(response.text))
				return root
			else:
				response.raise_for_status()
				print("Error occured in GET -->"+(response.text))
		except requests.exceptions.HTTPError as err:
			print ("Error in connection -->"+str(err))
		finally:
			if response : response.close()


	def ISEGETX(self, url, headers):
		"""
		Generic GET request using XMLtoDict to parse data
		"""

		try:
			response = requests.request("GET", url, auth=(self.username,self.password), headers=headers, verify=False)
			status_code = response.status_code
			if (status_code == 200):
				root = xmltodict.parse(response.text)
				return root
			else:
				response.raise_for_status()
				print("Error occured in GET -->"+(response.text))
		except requests.exceptions.HTTPError as err:
			print ("Error in connection -->"+str(err))
		finally:
			if response : response.close()


	def ISEPOST(self, url, headers, content):
		"""
		Generic POST
		"""

		try:
			response = requests.request("POST", url, auth=(self.username,self.password), headers=headers, data=content, verify=False)
			status_code = response.status_code
			if (status_code == 201):
				return True
			else:
				response.raise_for_status()
				print("Error occured in POST -->"+(response.text))
		except requests.exceptions.HTTPError as err:
			print ("Error in connection -->"+str(err))
		finally:
			if response : response.close()


	def ISEDELETE(self, url, headers):
		"""
		Generic DELETE
		"""

		try:
			response = requests.request("DELETE", url, auth=(self.username,self.password), headers=headers, verify=False)
			status_code = response.status_code
			if (status_code == 204):
				return True
			else:
				response.raise_for_status()
				print("Error occured in GET -->"+(response.text))
		except requests.exceptions.HTTPError as err:
			print ("Error in connection -->"+str(err))
		finally:
			if response : response.close()


	def GetAllEndpoints(self):
		"""
		Retrieve all endpoints in the ISE deployment
		"""
		myurl = "https://"+self.server+":9060/ers/config/endpoint"
		headers = {'accept': "application/vnd.com.cisco.ise.identity.endpoint.1.0+xml"}
		return self.ISEGETE(myurl, headers)
		


	def GetEndpointByID(self, endpointID):
		"""
		Retrieve specific Endpoint data using the unique ISE ID
		"""
		myurl = "https://"+self.server+":9060/ers/config/endpoint/"+endpointID
		headers = {'accept' : "application/vnd.com.cisco.ise.identity.endpoint.1.0+xml;"}
		return self.ISEGETX(myurl, headers)


	def CreateEndpoint(self, content):
		"""
		Create an endpoint in the ISE deployment
		"""
		myurl = "https://"+self.server+":9060/ers/config/endpoint"
		headers = {'content-type': "application/vnd.com.cisco.ise.identity.endpoint.1.0+xml; charset=utf-8"}
		#print content
		return self.ISEPOST(myurl, headers, content)


	def DeleteEndpoint(self, endpointID):
		"""
		Delete an Endpoint from the ISE deployment
		"""
		myurl = "https://"+self.server+":9060/ers/config/endpoint/"+endpointID
		headers = {'accept': "application/vnd.com.cisco.ise.identity.endpoint.1.0+xml"}
		return self.ISEDELETE(myurl, headers)


	def MacTransform(self, macAddress):
		"""
		Take input MAC address using any delimiter, and transform to the : delimiter with uppercase characters to make suitable for ISE
		"""
		letters = (":" if i % 3 == 0 else char for i, char in enumerate(macAddress.upper(), 1))
		transMac = str(''.join(letters))
		return transMac



class SparkAPI(object):

	"""
	Requires a known bot ID and Room ID for retrieving and creating messages
	"""

	def __init__(self, roomID, botID):
		self.roomID = roomID
		self.botID = botID

	def SparkGET(self, url, headers):
		"""
		Generic Spark GET
		"""
		
		try:
			response = requests.request("GET", url, headers=headers, verify=False)
			status_code = response.status_code
			if (status_code == 200):
				return response.text
			else:
				response.raise_for_status()
				print("Error occured in GET -->"+(response.text))
		except requests.exceptions.HTTPError as err:
			print ("Error in connection -->"+str(err))
		finally:
			if response : response.close()


	def SparkPOST(self, url, headers, payload):
		"""
		Generic Spark POST
		"""
		
		try:
			response = requests.request("POST", url, headers=headers, data=payload, verify=False)
			status_code = response.status_code
			if (status_code == 200):
				return response.text
			else:
				response.raise_for_status()
				print("Error occured in GET -->"+(response.text))
		except requests.exceptions.HTTPError as err:
			print ("Error in connection -->"+str(err))
		finally:
			if response : response.close()



	def GETMessage(self, messageID):
		"""
		Get a message from its unique Spark Message ID
		"""
		
		url = 'https://api.ciscospark.com/v1/messages/'+messageID
		headers = {'content-type' : 'application/json; charset=utf-8', 'authorization' : "Bearer "+self.botID}
		return self.SparkGET(url, headers)

	def POSTMessage(self, payload):
		"""
		Create a message in Spark
		"""

		url = 'https://api.ciscospark.com/v1/messages'
		headers = {'content-type' : 'application/json; charset=utf-8', 'authorization' : "Bearer "+self.botID}
		return self.SparkPOST(url, headers, payload)


