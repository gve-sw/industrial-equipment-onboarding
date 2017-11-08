# IOT Device replacement in a Secure Access Network

One of the big barriers of implementing secure network access in an Industrial environment is the increased risk of device downtime and the high overheads of managing an environment with thousands of devices. 

Our project simplifies the process of adding and removing industrial network-connected devices into a secure network. Non-IT designated staff can use their smartphone or ruggardised tablet to perform this process in a couple of minutes, reducing downtime and lowering IT burden. 

![alt text](https://github.com/cisco-gve/industrial-equipment-onboarding/blob/master/images/UserScenario.jpg "Scenario diagram")

The image above shows a user with [Spark](http://cisco.com/go/spark) on their phone updating MAC address entries in the [Identity Services Engine (ISE)](http://cisco.com/go/ise), allowing devices to be replaced on the floor within minutes. 
MAC Addresses can be entered manually as text, or can be uploaded as an image taken by the phone's camera. 

## How to use this repository

### Before you begin - what do you need?
* [Cisco Spark](https://www.ciscospark.com/) account. 
* Spark Bot - See [here](https://developer.ciscospark.com/bots.html) to create your bot. You will need two pieces of information from your bot once it is created: The Bot Token and the Bot ID (more on these below).  
* ISE Server - Your ISE deployment must have the ERS API [enabled](https://communities.cisco.com/docs/DOC-66297#jive_content_id_Enable_the_ERS_APIs). It is disabled by default. You must also have a user with ERSAdmin privileges. The application will use this user's credentials. 
* [Docker](https://docs.docker.com/engine/installation/) - The application environment for this project is defined in Docker containers. You could run all the scripts outside of Docker if you like a challenge. 
* [Docker Compose](https://docs.docker.com/compose/install/) - This is included in the Docker install package linked above for Mac and Windows, but must be installed separately on Linux. 
* [Google Cloud Platform](https://cloud.google.com/) account - Used to analyse images and extract MAC addreses for this project. You will need to do two things once you have signed up for an account. 
	1. [Enable](https://cloud.google.com/vision/docs/before-you-begin) the vision API
	1. [Create](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) a service account key. This will be used to allow the application to authenticate to the Google cloud. When you create this key you will receive a JSON file. Keep hold of it - we will use it soon. 


### Instructions

1. Ensure you have performed all the prerequisite actions in the 'Before you begin' section above

1. Populate the `settingsTemplate.py` file with your ISE IP Address, ISE ERS API admin username and password, your Spark Bot Token and your Spark Bot ID. 

1. Save the resulting file as `/python/settings.py` and `createWebhook/settings.py`

1. Copy the Google Cloud Platform service account key JSON file into `/python`

1. Edit /python/Dockerfile and change the line: `ENV GOOGLE_APPLICATION_CREDENTIALS gcp-project-name-54645fvcsdf43.json` where the .json filename matches the name of the file you copied into /python.

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