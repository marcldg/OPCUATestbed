import datetime
import time
import json
import codecs
import psutil
import Adafruit_DHT
import subprocess
import os, time
from scipy import rand
from opcua import Server, uamethod, ua
from random import randint

DHT_SENSOR = Adafruit_DHT.AM2302
DHT_PIN = 4

def temperature():
    temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return round(float(temperature[1]), 1)

def humidity():
    humidity = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return round(float(humidity[0]), 1)

def display(val):
  return round(float(val),2)

def cpuUse():
    """
    Obtains the system's average CPU load as measured over a period of 500 milliseconds.
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

endpointUrl = "opc.tcp://192.168.4.32:4845"
server.set_endpoint(endpointUrl)
#server.import_xml("test.xml")

serverName = "OPC-UA-SERVER-5"
server.set_server_name(serverName)

#############################################################################
                    #OPC-UA OBJECT NODE & VARIABLE MODELING#
#############################################################################

rootNode = server.get_root_node()
objectNode = server.get_objects_node()
namespaceName = server.register_namespace("OPC-UA-SERVER-5")
edgeGateway = objectNode.add_object(namespaceName, "OPC-UA-SERVER-5")
am2302Sensor = objectNode.add_object(namespaceName, "AM2302-Temp&Humidity")

#initialising variables
host = edgeGateway.add_variable(namespaceName, "HostName", 0, ua.VariantType.String)
ip = edgeGateway.add_variable(namespaceName, "IP-Address", 0, ua.VariantType.Float)
cpuUsage = edgeGateway.add_variable(namespaceName, "CPU-Usage", 0, ua.VariantType.Float)
cpuFreq = edgeGateway.add_variable(namespaceName, "CPU-Frequency", 0, ua.VariantType.Float)
cpuTemp = edgeGateway.add_variable(namespaceName, "CPU-Temperature", 0, ua.VariantType.Float)
totRam = edgeGateway.add_variable(namespaceName, "Ram-Total", 0, ua.VariantType.Float)
usedRam = edgeGateway.add_variable(namespaceName, "Ram-Percentage-Used", 0, ua.VariantType.Float)
availableRam = edgeGateway.add_variable(namespaceName, "Ram-Percentage-Free", 0, ua.VariantType.Float)
storage = edgeGateway.add_variable(namespaceName, "Storage-Total", 0, ua.VariantType.Float)
usedStorage = edgeGateway.add_variable(namespaceName, "Storage-Used", 0, ua.VariantType.Float)
freeStorage = edgeGateway.add_variable(namespaceName, "Storage-Free", 0, ua.VariantType.Float)
upTime = edgeGateway.add_variable(namespaceName, "Running Time", 0, ua.VariantType.Double)
curTime = edgeGateway.add_variable(namespaceName, "Time", 0)

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