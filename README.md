# IOT Device replacement in a Secure Access Network

One of the big barriers of implementing secure network access in an Industrial environment is the increased risk of device downtime and the high overheads of managing an environment with thousands of devices. 

Our project simplifies the process of adding and removing industrial network-connected devices into a secure network. Non-IT designated staff can use their smartphone or ruggardised tablet to perform this process in a couple of minutes, reducing downtime and lowering IT burden. 

![alt text](https://github.com/cisco-gve/industrial-equipment-onboarding/blob/master/images/UserScenario.jpg "Scenario diagram")

The image above shows a user with their phone updating the MAC address entries in ISE, allowing devices to be replaced on the floor within minutes. 

## How to use this repository


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