import datetime
import asyncio
import csv
import psutil
import random
import adafruit_dht
import board
import subprocess
import os, time
import sys
sys.path.insert(0, "..")
from asyncua import ua, Server
from asyncua.common.methods import uamethod

# Defining the duration of the experiment in seconds.
experimentDuration = 600
simulatedOutput = []

# Getting the time at which the experiment was started. 
startTime = time.time()
# Configurating the adafruit library to detect and use the DHT22 sensor connected to pin D17.
dht22 = adafruit_dht.DHT22(board.D17, use_pulseio=False)

# Creating a CSV file and populating it with the corresponding headings 
file = open("performanceEvaluation.csv", "w", newline="")
heading = ["Time-Stamp", "CPU-Usage", "CPU-Frequency", "CPU-Temperature", "Ram-Percentage-Used", "Number-Of-Nodes"]
cursObj = csv.writer(file)
cursObj.writerow(heading)
file.close()

async def simulateData():
    """
    Asyncronous function that loops through a list of previously generated variables and
    populates each of them with a random value ranging between 0 - 100.
    """
    for variable in simulatedOutput:
        await variable.write_value(round(random.uniform(0,100), 2))

async def temperature(variable):
    """
    Asyncronous function that attempts to get the temperature value reading from the sensor 
    and assigns the value to the parameter - variable passed to the function.
    :returns: Value 0 if it fails to get the temperature reading.
    :rtype: Int
    """ 
    try:
        temperature = dht22.temperature
        await variable.write_value(temperature)
    
    except RuntimeError:
        return 0

async def humidity(variable):
    """
    Asyncronous function that attempts to get the humidity value reading from the sensor 
    and assigns the value to the parameter - variable passed to the function.
    :returns: Value 0 if it fails to get the humidity reading.
    :rtype: Int
    """ 
    try:
        humidity = dht22.humidity
        await variable.write_value(humidity)
    
    except RuntimeError:
        return 0

def display(val):
  """
  Rounds off the value passed in as a parameter to 2 d.p and converts that value to a float.
  :returns: Converted float value to 2 d.p
  :rtype: float
  """
  return round(float(val),2)

async def getTime(variable):
    """
    Asyncronous function that gets the current date & time value and writes this value to
    the parameter - variable passed.
    """
    currentTime = datetime.datetime.now()
    await variable.write_value(currentTime)

async def cpuUse(variable):
    """
    Asyncronous function that obtains the system's average CPU load measured as a percentage
    and writes this value to the parameter - variable passed.
    """
    cpuUse = (round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
    await variable.write_value(cpuUse)

async def cpuFrequency(variable):
    """
    Asyncronous function that obtains the real-time value of the current CPU frequency 
    measured in MHz and writes this value to the parameter - variable passed.
    """
    cpuFreq = float((psutil.cpu_freq().current))
    await variable.write_value(cpuFreq)

async def cpuTemperature(variable):
    """
    Asyncronous function that obtains the current value of the CPU temperature in degrees celsius 
    if successful, zero value otherwise. It then writes this value to the parameter - 
    variable passed.
    """  
    thermal = round(float(subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp", shell=True).rstrip())/1000,2)
    await variable.write_value(thermal)
    
async def runTime(variable):
    """
    Asyncronous function that obtains the duration in hours since the device has been last
    powered on. It then writes this value to the parameter - variable passed.
    """  
    runningTime = round(display(subprocess.check_output("cat /proc/uptime | awk '{print $1}'", shell=True).rstrip())/60/60,2)
    await variable.write_value(runningTime)

async def totalRam(variable):
    """
    Asyncronous function that obtains the total amount of RAM in Gigabytes available 
    to the system. It then writes this value to the parameter - variable passed.
    """
    ramTotal = round(display(subprocess.check_output("free | awk 'FNR == 2 {print $2/1000000}'", shell=True).rstrip()))
    await variable.write_value(ramTotal)

async def usageRam(variable):
    """
    Asyncronous function that obtains the absolute number of RAM in Gigabytes currently 
    in use by the system. It then writes this value to the parameter - variable passed.
    """
    usage = display(subprocess.check_output("free | awk 'FNR == 2 {print $3/($3+$4)*100}'", shell=True).rstrip())
    await variable.write_value(usage)

async def freeRam(variable):
    """
    Asyncronous function that obtains the absolute number of RAM in Gigabytes currently free to
    be used by the system. It then writes this value to the parameter - variable passed.
    """
    freeRam = 100 - (display(subprocess.check_output("free | awk 'FNR == 2 {print $3/($3+$4)*100}'", shell=True).rstrip()))
    await variable.write_value(freeRam)

async def storageTotal(variable):
    """
    Asyncronous function that obtains the total amount of Storage Memory in Gigabytes available 
    to the system. It then writes this value to the parameter - variable passed.
    """
    totalStorage = float((subprocess.check_output("df -H --si | awk '/root/ {print $2}'", shell=True).rstrip()).decode('UTF-8')[:2])
    await variable.write_value(totalStorage)
    
async def storageUsed(variable):
    """
    Asyncronous function that obtains the total amount of Storage Memory in Gigabytes currently 
    in use by the system. It then writes this value to the parameter - variable passed.
    """
    usedStorage = float((subprocess.check_output("df -H --si | awk '/root/ {print $3}'", shell=True).rstrip()).decode('UTF-8')[:3])
    await variable.write_value(usedStorage)
  
async def storageFree(variable):
    """
    Asyncronous function that obtains the total amount of Storage Memory in Gigabytes currently 
    free to be used by the system. It then writes this value to the parameter - variable passed.
    """
    freeStorage = float((subprocess.check_output("df -H --si | awk '/root/ {print $4}'", shell=True).rstrip()).decode('UTF-8')[:2])
    await variable.write_value(freeStorage) 

async def hostName(variable):
    """
    Asyncronous function that obtains hostname of the system.
    It then writes this value to the parameter - variable passed.
    """
    hostName = str(subprocess.check_output("hostname", shell=True).decode("utf-8"))
    await variable.write_value(hostName)
    
async def ipAddress(variable):
    """
    Asyncronous function that obtains the ip address of the system.
    It then writes this value to the parameter - variable passed.
    """
    ip = subprocess.check_output("hostname -I | cut -d\' \' -f1", shell=True).decode("utf-8")
    await variable.write_value(ip)

async def main():
    """
    Asyncronous function that sets up the OPC UA Server, 
    Populates the address space with object nodes and variables, 
    Sets the respective variables to writable and 
    Starts the OPC UA Server. 
    """
    simulatedVariables = []
    objectNodes = []

#############################################################################
                            #OPC-UA SERVER SETUP#
#############################################################################

    server = Server()

    # Setting up the server name.
    serverName = "OPC-UA-SERVER-2"
    server.set_server_name(serverName)
    
    # Getting the number of Nodes to be simulated from the user.
    simulationNumber = int(input("How many Nodes would you like to simulate ? "))

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

    # Creating the number of Nodes requested by the user. 
    for num in range(simulationNumber):
        objectNodes.append("Node" + str(num + 1))
    for idx, nodes in enumerate(objectNodes):
        for var in random.sample(variablesList, 10):
            simulatedVariables.append("NODE-" + str(idx + 1) + "-" + var)

    await server.init()
    
    # Setting up the build information. 
    await server.set_build_info(
    product_uri="https://github.com/marcldg/OPCUATestbed",
    product_name="OPC UA Testbed",
    manufacturer_name="Jordan Marc Ladegourdie",
    software_version="Development Phase",
    build_number="0.0.9",
    build_date=datetime.datetime.now(),
    )
    
    # Defining the ip address and the port number of the opcua server.
    endpointUrl = "opc.tcp://192.168.4.37:4844"
    server.set_endpoint(endpointUrl)
    
    # Defining the address space.
    namespaceName = await server.register_namespace("OPC-UA-SERVER-2")

#############################################################################
                    #OPC-UA OBJECT NODE & VARIABLE MODELING#
#############################################################################

    # Populating the address space.
    # The server.nodes, contains links to common nodes like objects and root.
    opcUaServerPerf = await server.nodes.objects.add_object(namespaceName, "OPC-UA-SERVER-2")
    dht22Sensor = await server.nodes.objects.add_object(namespaceName, "DHT22-Temp&Humidity")

    # Generating and populating each Node with 10 random variables. 
    for idx, nodes in enumerate(objectNodes):
        nodes = await server.nodes.objects.add_object(namespaceName, "NODE-" + str(idx + 1))
        for simVar in simulatedVariables[:10]:
            simVar = await nodes.add_variable(namespaceName, simVar , 0, ua.VariantType.Double)
            simulatedOutput.append(simVar)
            simulatedVariables.pop(0)
    
    # Initialising variables.
    host = await opcUaServerPerf.add_variable(namespaceName, "HostName", 0, ua.VariantType.String)
    ip = await opcUaServerPerf.add_variable(namespaceName, "IP-Address", 0, ua.VariantType.String)
    cpuUsage = await opcUaServerPerf.add_variable(namespaceName, "CPU-Usage", 0, ua.VariantType.Double)
    cpuFreq = await opcUaServerPerf.add_variable(namespaceName, "CPU-Frequency", 0, ua.VariantType.Double)
    cpuTemp = await opcUaServerPerf.add_variable(namespaceName, "CPU-Temperature", 0, ua.VariantType.Double)
    totRam = await opcUaServerPerf.add_variable(namespaceName, "Ram-Total", 0)
    usedRam = await opcUaServerPerf.add_variable(namespaceName, "Ram-Percentage-Used", 0, ua.VariantType.Double)
    availableRam = await opcUaServerPerf.add_variable(namespaceName, "Ram-Percentage-Free", 0, ua.VariantType.Double)
    storage = await opcUaServerPerf.add_variable(namespaceName, "Storage-Total", 0, ua.VariantType.Double)
    usedStorage = await opcUaServerPerf.add_variable(namespaceName, "Storage-Used", 0, ua.VariantType.Double)
    freeStorage = await opcUaServerPerf.add_variable(namespaceName, "Storage-Free", 0, ua.VariantType.Double)
    upTime = await opcUaServerPerf.add_variable(namespaceName, "Running Time", 0, ua.VariantType.Double)
    curTime = await opcUaServerPerf.add_variable(namespaceName, "Time", 0, ua.VariantType.DateTime)
    temp = await dht22Sensor.add_variable(namespaceName, "Temperature", 0, ua.VariantType.Double)
    humi = await dht22Sensor.add_variable(namespaceName, "Humidity", 0, ua.VariantType.Double)

    # Setting each variables to be writable.
    await curTime.set_writable()
    await cpuUsage.set_writable()
    await cpuFreq.set_writable()
    await cpuTemp.set_writable()
    await upTime.set_writable()
    await totRam.set_writable()
    await usedRam.set_writable()
    await availableRam.set_writable()
    await storage.set_writable()
    await usedStorage.set_writable()
    await freeStorage.set_writable()
    await host.set_writable()
    await ip.set_writable()
    await temp.set_writable()
    await humi.set_writable()
    
#############################################################################
                        #STARTING OPC-UA SERVER#
#############################################################################

    async with server:
        
        print("Server started at {}".format(endpointUrl))
        
        while True:
            currentTime = time.time()
            elapsedTime = currentTime - startTime

            # Checking that the time elapsed has not exceeded the experiment time frame.
            if elapsedTime >= experimentDuration:
                print("End of experiment")
                break 

            await asyncio.sleep(0.5)
            await temperature(temp)
            await humidity(humi)

            # Running all the asynchronous functions concurrently for maximum single thread performance.
            asyncio.gather(
                getTime(curTime),
                cpuUse(cpuUsage), 
                cpuFrequency(cpuFreq),
                cpuTemperature(cpuTemp),
                runTime(upTime),
                totalRam(totRam),
                usageRam(usedRam),
                freeRam(availableRam),
                storageTotal(storage),
                storageUsed(usedStorage),
                storageFree(freeStorage),
                hostName(host),
                ipAddress(ip),
                simulateData()
            )

            # Gather the performance data required for the evaluation. 
            performanceData = [(await curTime.get_value()), (await cpuUsage.get_value()), (await cpuFreq.get_value()), (await cpuTemp.get_value()), (await usedRam.get_value()), (simulationNumber+1)]

            # Insert the performance data into a csv file for further evaluation.
            with open("performanceEvaluation.csv", "a", newline="") as filePointer:
                writerObj = csv.writer(filePointer)
                writerObj.writerow(performanceData)

if __name__ == '__main__':

    asyncio.run(main())
