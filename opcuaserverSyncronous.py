import datetime
import time
import json
import codecs
import csv
import psutil
import random
import adafruit_dht
import board
import subprocess
import os, time
from scipy import rand
from opcua import Server, uamethod, ua

simulatedOutput = []
dht22 = adafruit_dht.DHT22(board.D17, use_pulseio=False)

file = open("performanceEvaluation.csv", "w", newline="")
heading = ["Time-Stamp", "CPU-Usage", "CPU-Frequency", "CPU-Temperature", "Ram-Percentage-Used"]
cursObj = csv.writer(file)
cursObj.writerow(heading)
file.close()

def createObjectNode(simulationNumber):
    simulatedVariables = []
    objectNodes = []
    variablesList = ["length", "area", "volume", "angle", "solid-angle", "time", 
                     "frequency", "sound", "momentum", "speed", "acceleration", "position",
                     "mass", "density", "linear-density", "weight", "force", "torque", 
                     "energy", "power", "pressure", "stress", "temperature", "amount-of-heat", 
                     "luminous-intensity", "luminance", "luminous-flux", "illuminance", 
                     "light-quantity", "refractive-index", "current", "electric charge", 
                     "voltage", "resistance", "capacitance", "conductance", "inductance", 
                     "magnetic-flux", "magnetic-flux-density", "radioactive-decay", "half-life",
                     "amount-of-substance", "quantity", "humidity", "moisture", "turbidity", "TDS",
                     "pH", "GH", "KH"]

    for num in range(simulationNumber):
        objectNodes.append("Node" + str(num + 1))
        
    for idx, nodes in enumerate(objectNodes):
        for var in random.sample(variablesList, 10):
            simulatedVariables.append("NODE-" + str(idx + 1) + "-" + var)
            

    for idx, nodes in enumerate(objectNodes):
        nodes = objectNode.add_object(namespaceName, "NODE-" + str(idx + 1))
        for simVar in simulatedVariables[:10]:
            simVar = nodes.add_variable(namespaceName, simVar , 0)
            simulatedOutput.append(simVar)
            simulatedVariables.pop(0)
            
    for y in objectNodes:
        print(y)      
          
    for x in simulatedVariables:
        print(x)

def temperature():
    try:
        temperature = dht22.temperature
        return temperature
    
    except RuntimeError:
        return 0

def humidity():
    try:
        humidity = dht22.humidity
        return humidity
    
    except RuntimeError:
        return 0

def display(val):
  return round(float(val),2)

def cpuUse():
    """
    
    :returns: System CPU load as a percentage.
    :rtype: float
    """
    cpuUse =(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
    return float(cpuUse)

def cpuFrequency():
    """
    Obtains the real-time value of the current CPU frequency.
    :returns: Current CPU frequency in MHz.
    :rtype: int
    """
    return int(psutil.cpu_freq().current)

def cpuTemperature():
    """
    Obtains the current value of the CPU temperature.
    :returns: Current value of the CPU temperature if successful, zero value otherwise.
    :rtype: float
    """
    thermal = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp", shell=True).rstrip()
    return round(float(thermal)/1000,2)
    
def runTime():
    runningTime = subprocess.check_output("cat /proc/uptime | awk '{print $1}'", shell=True).rstrip()
    return round(display(runningTime)/60/60,2)

def totalRam():
    """
    Obtains the total amount of RAM in bytes available to the system.
    :returns: Total system RAM in bytes.
    :rtype: int
    """
    ramTotal = subprocess.check_output("free | awk 'FNR == 2 {print $2/1000000}'", shell=True).rstrip()
    return round(display(ramTotal))

def usageRam():
    """
    Obtains the absolute number of RAM bytes currently in use by the system.
    :returns: System RAM usage in bytes.
    :rtype: int
    """
    usage = subprocess.check_output("free | awk 'FNR == 2 {print $3/($3+$4)*100}'", shell=True).rstrip()
    return display(usage)

def freeRam():
    """
    Obtains the total amount of RAM in bytes available to the system.
    :returns: Total system RAM in bytes.
    :rtype: int
    """
    freeRam = 100 - usageRam()
    return freeRam

def storageTotal():
    totalStorage = subprocess.check_output("df -H --si | awk '/root/ {print $2}'", shell=True).rstrip()
    return totalStorage.decode('UTF-8')[:2]
    
def storageUsed():
    usedStorage = subprocess.check_output("df -H --si | awk '/root/ {print $3}'", shell=True).rstrip()
    return usedStorage.decode('UTF-8')[:3]
  
def storageFree():
    freeStorage = subprocess.check_output("df -H --si | awk '/root/ {print $4}'", shell=True).rstrip()
    return freeStorage.decode('UTF-8')[:2]

def hostName():
    hostName = subprocess.check_output("hostname", shell=True).decode("utf-8")
    return hostName
    
def ipAddress():
    ip = subprocess.check_output("hostname -I | cut -d\' \' -f1", shell=True).decode("utf-8")
    return ip

#############################################################################
                            #OPC-UA SERVER SETUP#
#############################################################################

server = Server()

#defining the ip address and the port number of the opcua server.
endpointUrl = "opc.tcp://192.168.4.37:4842"
server.set_endpoint(endpointUrl)

serverName = "OPC-UA-SERVER-2"
server.set_server_name(serverName)
simulationNumber = int(input("How many Nodes would you like to simulate ? "))

#############################################################################
                    #OPC-UA OBJECT NODE & VARIABLE MODELING#
#############################################################################

rootNode = server.get_root_node()
objectNode = server.get_objects_node()

#defining the address space.
namespaceName = server.register_namespace("OPC-UA-SERVER-2")
opcUaServerPerf = objectNode.add_object(namespaceName, "OPC-UA-SERVER-2")
am2302Sensor = objectNode.add_object(namespaceName, "AM2302-Temp&Humidity")
createObjectNode(simulationNumber)

#initialising variables
host = opcUaServerPerf.add_variable(namespaceName, "HostName", 0, ua.VariantType.String)
ip = opcUaServerPerf.add_variable(namespaceName, "IP-Address", 0, ua.VariantType.Float)
cpuUsage = opcUaServerPerf.add_variable(namespaceName, "CPU-Usage", 0, ua.VariantType.Float)
cpuFreq = opcUaServerPerf.add_variable(namespaceName, "CPU-Frequency", 0, ua.VariantType.Float)
cpuTemp = opcUaServerPerf.add_variable(namespaceName, "CPU-Temperature", 0, ua.VariantType.Float)
totRam = opcUaServerPerf.add_variable(namespaceName, "Ram-Total", 0, ua.VariantType.Float)
usedRam = opcUaServerPerf.add_variable(namespaceName, "Ram-Percentage-Used", 0, ua.VariantType.Float)
availableRam = opcUaServerPerf.add_variable(namespaceName, "Ram-Percentage-Free", 0, ua.VariantType.Float)
storage = opcUaServerPerf.add_variable(namespaceName, "Storage-Total", 0, ua.VariantType.Float)
usedStorage = opcUaServerPerf.add_variable(namespaceName, "Storage-Used", 0, ua.VariantType.Float)
freeStorage = opcUaServerPerf.add_variable(namespaceName, "Storage-Free", 0, ua.VariantType.Float)
upTime = opcUaServerPerf.add_variable(namespaceName, "Running Time", 0, ua.VariantType.Double)
curTime = opcUaServerPerf.add_variable(namespaceName, "Time", 0)

temp = am2302Sensor.add_variable(namespaceName, "Temperature", 0, ua.VariantType.Float)
humi = am2302Sensor.add_variable(namespaceName, "Humidity", 0, ua.VariantType.Float)

#setting variables to write
#cpuUsage.set_writable()

#############################################################################
                        #STARTING OPC-UA SERVER#
#############################################################################

server.start()
print("Server started at {}".format(endpointUrl))
#publishing random values
while True:
    for var in simulatedOutput:
        var.set_value(round(random.uniform(0,100), 2))
        
    currentTime = datetime.datetime.now()
    currentTemperature = temperature()
    currentHumidity = humidity()
    percentageCpuUse = cpuUse()
    freqCpu = cpuFrequency()
    cpuThermal = cpuTemperature()
    totalStorage = storageTotal()
    usedSto = storageUsed()
    freeSto = storageFree()
    ram = totalRam()
    pctUsedRam = usageRam()
    pctFreeRam = freeRam()
    runningTime = runTime()
    hostID = hostName()
    ipv4 = ipAddress()
    
    performanceData = [currentTime, percentageCpuUse, freqCpu, cpuThermal, pctUsedRam]
    
    with open("performanceEvaluation.csv", "a", newline="") as filePointer:
        writerObj = csv.writer(filePointer)
        writerObj.writerow(performanceData)
    
    print(hostID, ipv4, currentTime, runningTime, cpuThermal, freqCpu, percentageCpuUse, ram, pctUsedRam, pctFreeRam, totalStorage, usedSto, freeSto, currentTemperature, currentHumidity)
    
    host.set_value(hostID)
    ip.set_value(ipv4)
    cpuTemp.set_value(cpuThermal)
    cpuFreq.set_value(freqCpu)
    cpuUsage.set_value(percentageCpuUse)
    storage.set_value(totalStorage)
    usedStorage.set_value(usedSto)
    freeStorage.set_value(freeSto)
    totRam.set_value(ram)
    usedRam.set_value(pctUsedRam)
    availableRam.set_value(pctFreeRam)
    curTime.set_value(currentTime)
    upTime.set_value(runningTime)
    temp.set_value(currentTemperature)
    humi.set_value(currentHumidity)
    
    time.sleep(2)