from opcua import Server
from random import randint
import datetime
import time
from scipy import rand

server = Server()

# Defining the ip address and the port number of the opcua server.
url = "opc.tcp://192.168.91.129:4840"
server.set_endpoint(url)

# Defining the address space.
name = "OPCUA_SIMULATION_SERVER"
addSpace = server.register_namespace(name)
node = server.get_objects_node()
Param = node.add_object(addSpace, "Parameters")

#initialising variables
temp = Param.add_variable(addSpace, "Temperature", 0)
pressure = Param.add_variable(addSpace, "Pressure", 0)
curTime = Param.add_variable(addSpace, "Time", 0)

#setting variables to write
temp.set_writable()
pressure.set_writable()
curTime.set_writable()

#starting server
server.start()
print("Server started at {}".format(url))

#publishing random values
while True:
    randTemp = randint(0,5)
    randPressure = randint(0, 10)
    randTime = datetime.datetime.now()
    
    print(randTemp,randPressure,randTime)
    
    temp.set_value(randTemp)
    pressure.set_value(randPressure)
    curTime.set_value(randTime)
    
    time.sleep(2)