# IOT Device replacement in a Secure Access Network

One of the big barriers of implementing secure network access in an Industrial environment is the increased risk of device downtime and the high overheads of managing an environment with thousands of devices. 

Our project simplifies the process of adding and removing industrial network-connected devices into a secure network. Non-IT designated staff can use their smartphone or ruggardised tablet to perform this process in a couple of minutes, reducing downtime and lowering IT burden. 

![alt text](https://github.com/cisco-gve/industrial-equipment-onboarding/blob/master/images/UserScenario.jpg "Scenario diagram")

The image above shows a user with [Spark](http://cisco.com/go/spark) on their phone updating MAC address entries in the [Identity Services Engine (ISE)](http://cisco.com/go/ise), allowing devices to be replaced on the floor within minutes. 
MAC Addresses can be entered manually as text, or can be uploaded as an image taken by the phone's camera. 

## How to use this repository

### Pre-requisites
* [Cisco Spark](https://www.ciscospark.com/) account. 
* Spark Bot - See [here](https://developer.ciscospark.com/bots.html) to create your bot. You will need two pieces of information from your bot once it is created: The Bot Token and the Bot ID (more on these below).  
* [Docker](https://docs.docker.com/engine/installation/) - The main application and supporting applications, as well as their dependencies are defined as containers. You could run all scripts on their own without Docker if you like a challenge :)
* [Docker Compose](https://docs.docker.com/compose/install/) - This is included in the Docker install package linked above for Mac and Windows, but must be installed separately on Linux. 
* [Google Cloud Platform](https://cloud.google.com/) account - Used to analyse images and extract the MAC address for this project. You will need to do two things once you have signed up for an account. 
	1. [Enable](https://cloud.google.com/vision/docs/before-you-begin) the vision API
	1. [Create](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) a service account key. This will be used to allow the application to authenticate to the Google cloud. When you create this key you will receive a JSON file. Keep hold of it - we will use it soon. 



See ISEAPI.py for generic API calls to ISE and Spark

See mabReplace.py for the main program logic

Note currently this script requires a settings file containing the following: 
* ISE Server IP
* ISE ERS username
* ISE ERS password
* The Spark Room ID
* The Spark Bot token
* The Spark Bot ID

In future revisions the process of retrieving this data and creating the settings file will be automated. 