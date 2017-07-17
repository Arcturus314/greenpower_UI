import matplotlib.pyplot as plt
import tty
import sys
import termios
import math
import arduino_interface

screenState = 0 # 0=screen0; 1=screen1; 2=screen2 ... 
alternateScreen = False # False = main screen; True = alternate screen

battery1Volt = [] #list used to store voltage readings across battery 1
battery2Volt = [] #list used to store voltage readings across battery 2
motorCurrent = [] #list used to store motor current readings
motorTemp = [] #list used to store motor temperature readings
motorCTemp = [] #list used to store motor controller temperature readings
timeSample = [] #list used to store time of each sample

#reading data from file (ONLY FOR TESTING PURPOSES)
#formatting:
#   line 1 | battery 1 voltage
#   line 2 | battery 2 voltage
#   line 3 | motor current
#   line 4 | motor temperature
#   line 5 | motor controller temperature
#ALL VALUES PREFACED BY A COMMA
def readData():
    global data
    data = get_ard_data()
    timeSample.append(data[1])
    battery1Volt.append(data[0][3])
    battery2Volt.append(data[0][4])
    motorTemp.append(data[0][5])
    motorCTemp.append(data[0][6])


def printVal(): #printing read values
    print ("Battery 1 Voltage Values            |", battery1Volt)
    print ("Battery 2 Voltage Values            |", battery2Volt)
    print ("Motor Current Values                |", motorCurrent)
    print ("Motor Temperature Values            |", motorTemp)
    print ("Motor Controller Temperature Values |", motorCTemp)

def prepGraph(): #setting up full screen window
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle() #Maximizes plot window

def hideGraph():
    plt.close()

def graphS0(): #Overview graph screen
    current = motorCurrent[len(motorCurrent)-1]
    voltage = battery1Volt[len(battery1Volt)-1]+battery2Volt[len(battery2Volt)-1]
    temp = motorTemp[len(motorTemp)-1]+motorCTemp[len(motorCTemp)-1]

    plt.subplot(131)
    plt.bar(0, current, align='center', alpha=0.5)
    plt.ylabel("Current (A)")

    plt.subplot(132)
    plt.bar(0, voltage, align='center', alpha=0.5)
    plt.ylabel("Voltage (A)")

    plt.subplot(133)
    plt.bar(0, temp, align='center', alpha=0.5)
    plt.ylabel("Temperature (C)")

    plt.show()

def graphS0Alt(): #Alternate text-based overview screen
    #Working values
    current = motorCurrent[len(motorCurrent)-1]
    voltage1 = battery1Volt[len(battery1Volt)-1]
    voltage2 = battery2Volt[len(battery2Volt)-1]
    mTemp = motorTemp[len(motorTemp)-1]
    cTemp = motorCTemp[motorCTemp[len(motorCTemp)-1]]

    ##Standard deviation of last 10 values
    ##Sn = Sum((1/n)(Xi-Xm)^2)
    currentSum = 0.0
    voltage1Sum = 0.0
    voltage2Sum = 0.0
    mTempSum = 0.0
    cTempSum = 0.0

    for i in xrange(9):
        currentSum = currentSum + motorCurrent[len(motorCurrent)-1-i]
        voltage1Sum = voltage1Sum + battery1Volt[len(battery1Volt)-1-i]
        voltage2Sum = voltage2Sum + battery2Volt[len(battery2Volt)-1-i]
        mTempSum = mTempSum + motorTemp[len(motorTemp)-1-i]
        cTempSum = cTempSum + motorCTemp[len(motorCTemp)-1-i]

    currentMean = float(currentSum) / 10.0
    voltage1Mean = float(voltage1Sum) / 10.0
    voltage2Mean = float(voltage2Sum) / 10.0
    mTempMean = float(mTempSum) / 10.0
    cTempMean = float(mTempSum) / 10.0

    currentSOD2 = 0
    voltage1SOD2 = 0
    voltage2SOD2 = 0
    mTempSOD2 = 0
    cTempSOD2 = 0

    for i in xrange(9):
        currentSOD2 = currentSOD2 + (motorCurrent[len(motorCurrent)-1-i]-currentMean) ** 2
        voltage1SOD2 = voltage1SOD2 + (battery1Volt[len(battery1Volt)-1-i]-voltage1Mean) ** 2
        voltage2SOD2 = voltage2SOD2 + (battery2Volt[len(battery2Volt)-1-i]-voltage2Mean) ** 2
        mTempSOD2 = mTempSOD2 + (motorTemp[len(motorTemp)-1-i]-mTempMean) ** 2
        cTempSOD2 = cTempSOD2 + (motorCTemp[len(motorCTemp)-1-i]-cTempMean) ** 2


    currentSD = math.sqrt(currentSOD2/10.0)
    voltage1SD = math.sqrt(voltage1SOD2/10.0)
    voltage2SD = math.sqrt(voltage2SOD2/10.0)
    mTempSD = math.sqrt(mTempSOD2/10.0)
    cTempSD =math.sqrt(cTempSOD2/10.0)

    #Instantiating and filling graphics window
    xTextCoord = 0.33
    yTextCoord = 0.15
    plt.text(0, yTextCoord*6, "Measurement")
    plt.text(xTextCoord, yTextCoord*6, "Current Val")
    plt.text(xTextCoord*2, yTextCoord*6,"St.Dev.")

    plt.text(0, yTextCoord, "B.1 Volt")
    plt.text(xTextCoord, yTextCoord, voltage1)
    plt.text(xTextCoord*2, yTextCoord, round(voltage1SD,2))

    plt.text(0, yTextCoord*2, "B.2 Volt")
    plt.text(xTextCoord, yTextCoord*2, voltage2)
    plt.text(xTextCoord*2, yTextCoord*2, round(voltage2SD,2))

    plt.text(0, yTextCoord*3, "M. Current")
    plt.text(xTextCoord, yTextCoord*3, current)
    plt.text(xTextCoord*2, yTextCoord*3, round(currentSD,2))

    plt.text(0, yTextCoord*4, "M. Temp")
    plt.text(xTextCoord,  yTextCoord*4, mTemp)
    plt.text(xTextCoord*2, yTextCoord*4, round(mTempSD,2))

    plt.text(0, yTextCoord*5, "C. Temp")
    plt.text(xTextCoord, yTextCoord*5, cTemp)
    plt.text(xTextCoord*2, yTextCoord*5, round(cTempSD,2))

    plt.axis('off')

    plt.show()

def graphS1(): #Graph screen 1: Battery voltages on same graph
    plt.plot(timeSample, battery1Volt, 'bo', timeSample, battery2Volt, 'ro')
    plt.title("Battery Voltages")
    plt.xlabel("Time (min)")
    plt.ylabel("Voltage (v)")
    plt.show()

def graphS1Alt(): #Graph screen 1 alt: Battery voltages on different graphs
    plt.subplot(121)
    plt.xlabel("Time (min)")
    plt.ylabel("Voltage (v)")
    plt.title("Battery 1")
    plt.plot(timeSample, battery1Volt, 'bo')

    plt.subplot(122)
    plt.xlabel("Time (min)")
    plt.ylabel("Voltage (v)")
    plt.title("Battery 2")
    plt.plot(timeSample, battery2Volt, 'ro')

    plt.show()

def graphS2(): #Graph screen 2: Temperatures on the same graph
    plt.xlabel("Time (min)")
    plt.ylabel("Temp (C)")
    plt.title("Temperatures")
    plt.plot(timeSample, motorTemp, 'bo', timeSample, motorCTemp, 'ro')
    plt.show()

def graphS2Alt(): #Graph screen 2 alt: Temperatures on different graphs
    plt.subplot(121)
    plt.xlabel("Time (min)")
    plt.ylabel("Temp (C)")
    plt.title("Motor")
    plt.plot(timeSample, motorTemp, 'bo')

    plt.subplot(122)
    plt.xlabel("Time (min)")
    plt.ylabel("Temp (C)")
    plt.title("Motor Cont.")
    plt.plot(timeSample, motorCTemp, 'ro')

    plt.show()

def graphS3(): #Graph screen 3: Motor current draw
    plt.plot(timeSample, motorCurrent, 'g^')
    plt.xlabel("Time (min)")
    plt.ylabel("Current (A)")
    plt.title("Motor Current")
    plt.show()


readData()
#Parsing user input
def updateScreen(x):
    global screenState
    global alternateScreen
    if x=="d":
       if screenState<3:
            screenState = screenState+1
       else:
            screenState = 0
    if x=="a":
        if screenState>0:
            screenState = screenState-1
        else:
            screenState = 3
    if x=="s":
        if alternateScreen == False:
            alternateScreen = True
        else:
            alternateScreen = False
    #Updating view
    hideGraph()
    prepGraph() #delete if you don't want full screen graphs
    if screenState == 0:
        if alternateScreen == True:
            graphS0Alt()
        else:
            graphS0()
    if screenState == 1:
        if alternateScreen == True:
            graphS1Alt()
        else:
            graphS1()
    if screenState == 2:
        if alternateScreen == True:
            graphS2Alt()
        else:
            graphS2()
    if screenState == 3:
        graphS3()

#Actual polling code goes here
while True:
    if data[0][1] == '1':
        updateScreen("d")
    if data[0][0] == '1':
        updateScreen("a")
    if data[0][2] == '1':
        updateScreen("s")


