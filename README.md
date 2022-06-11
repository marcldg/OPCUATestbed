# OPCUATestbed

These are all the versions of the OPC UA Server used for the creation of the test bed. 

opcuaserverV0.1.py --> First version of the program that served as a platform to learn more about the basics of opc ua servers. 
 
 opcuaserverV0.2.py --> Builds on top of the version and adds slightly more functionalities. 

opcuaserverSyncronous.py --> The final version of the OPC UA Syncronous Server. This can be used to replicate the experiments as it is a stable released version. (Only compatible with Raspberry Pi Model 4B) 

opcuaserverRBPI3BV0.1.py --> The final version of the OPC UA Syncronous Server. This can be used to replicate the experiments as it is a stable released version. (Compatible with any Raspberry Pi Model)

opcuaserverAsyncronous.py --> The final version of the OPC UA Asyncronous Server. THIS IS THE VERSIION USED IN THE THESIS EVALUATION . It can be used to replicate the experiments as it is a stable released version. (Only compatible with Raspberry Pi Model 4B)

opcuaserverAsyncronous3B.py --> The final version of the OPC UA Asyncronous Server. THIS IS THE VERSIION USED IN THE THESIS EVALUATION . It can be used to replicate the experiments as it is a stable released version. (Compatible with any Raspberry Pi Model)

To replicate the test bed, download the desired version of the python program. Ensure that all the libraries are properly imported. Replace the IP address in the code with the local IPV4 address of the device. Then it is as easy as running the code. 

To visualise the data, it is recommended that you use The Prosys OPC UA Browser as the OPC UA Client of choice. Once the server started copy the endpoint URL in the address field of OPC UA Browser and click connect. 
