from opcua import Client
import datetime
import time

url = "opc.tcp://192.168.4.37:4842"

client = Client(url)

client.connect()
print("Client connected")

while True:
    #cpuUsageParam = client.get_node("ns=2;i=27")
    #cpuUsage = cpuUsageParam.get_value()
    #print(cpuUsage)
    
    #investigate with opcua ASYCIO
    timeT1Param = client.get_node("ns=2;i=37")
    timeT1 = timeT1Param.get_value()
    timeT2 = datetime.datetime.now()
    print("Time delay= " + str(timeT2-timeT1))
    time.sleep(2)
    
    