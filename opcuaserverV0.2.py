import datetime
import time
from scipy import rand
from opcua import Server, uamethod, ua
from random import randint

#############################################################################
                            #OPC-UA SERVER SETUP#
#############################################################################

server = Server()

#defining the ip address and the port number of the opcua server.
endpointUrl = "opc.tcp://192.168.4.20:4840"
server.set_endpoint(endpointUrl)
#server.import_xml("test.xml")

serverName = "OPC-UA PROJECT"
server.set_server_name(serverName)

#############################################################################
                    #OPC-UA OBJECT NODE & VARIABLE MODELING#
#############################################################################

rootNode = server.get_root_node()
objectNode = server.get_objects_node()
namespaceName = server.register_namespace("OPCUA_MAIN")
object1 = objectNode.add_object(namespaceName, "object1")

#initialising variables
temperature = object1.add_variable(namespaceName, "Temperature", 0, ua.VariantType.Float)
humidity = object1.add_variable(namespaceName, "Humidity", 0, ua.VariantType.Float)
curTime = object1.add_variable(namespaceName, "Time", 0)

#setting variables to write
temperature.set_writable()
humidity.set_writable()
curTime.set_writable()

#############################################################################
                        #STARTING OPC-UA SERVER#
#############################################################################

server.start()
print("Server started at {}".format(endpointUrl))

#publishing random values
while True:
    randTemp = randint(10,50)
    randHumidity = randint(200, 999)
    randTime = datetime.datetime.now()
    
    print(randTemp,randHumidity,randTime)
    
    temperature.set_value(randTemp)
    humidity.set_value(randHumidity)
    curTime.set_value(randTime)
 
    time.sleep(2)