# MAB device-replacement using Cisco Identity Services Engine (ISE) + Spark

This project uses a Spark chat interface to give non-IT personnel the ability to replace network-connected devices that require MAC Authentication Bypass (MAB) in a secure network access environment.

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