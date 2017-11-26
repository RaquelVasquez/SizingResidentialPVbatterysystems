# This code simulates the energy behavior depending on the size of the storage battery
# Autor: Raquel Alejandra Vasquez Torres

import time
import os
import sys
import math
import matplotlib.pyplot as plt
from xlrd import open_workbook
import matplotlib.ticker as plticker

date = time.strftime("%Y%m%d-%H%M%S")

# declare time interval and costs
timeInterval = 0.08333333333 # 5/60 mins conversion factor from kW to kWh of 0.0833 (5 min interval) 
electCost = 0.2670
electPrice = 0.1114

# function to read excel data
def readExcelData():
	global timeInterval
	a, b, c, dataCorrect = False, False, False, True
	consumption, PVgeneration, interval = [], [], []
	while dataCorrect:
		try:
			wb = open_workbook(str(str(raw_input("Write the excel spreadsheet name: ")) + ".xlsx"))
			dataCorrect = False
		except (ValueError, NameError, IOError):
			exit = raw_input('Oops! File name not found. Press Enter to try again or [e] and then Enter to exit: ')
			if exit == "e":
				print ("Verify that the .xlsx file is in the same folder as this code. Enter the file name without .xlsx extension")
				sys.exit(0)
	for s in wb.sheets():
		for col in range(s.ncols):
			col_value = []
			for row in range(s.nrows):
				value  = (s.cell(row,col).value)
				if a == True:
					try : value = (float(value))
					except : pass
					consumption.append((value))
				if value == "Consumption (W)":
					a = True
				if b == True:
					try : value = (float(value))
					except : pass
					PVgeneration.append((value))
				if value == "PV generation":
					b = True
				if c == True:
					try : value = (float(value))
					except : pass
					interval.append((value))
				if (value == "Time" or value == "time"):
					c = True
			a, b, c = False, False, False
	# verify length of data vector
	if ((len(consumption) == len(PVgeneration)) and (len(PVgeneration) == len(interval))):
		timeInterval = float((interval[1] - interval[0])/(0.041666667)) # factor to convert min/24hrs to min/1hr
		print ("Time interval: {} minutes".format((math.ceil(timeInterval * 60))))
		consumption = [i * timeInterval for i in consumption] # convert all data to kWh
		PVgeneration = [i * timeInterval for i in PVgeneration] # convert all data to kWh
		return consumption, PVgeneration
	else:
		print ("The length of the data lists is not the same, review the .xlsx file data")
		sys.exit(0)


# main function
def mainCode(consumption, PVgeneration, BatterySizeMain, folder, flagPlot):
	global date
	# declare battery as 0% of charge (previousCharge)
	batteryCurrentStorage, previousCharge, number = [], 0.0, 0
	# declare varaibles
	Consumption, PVGeneration, Edu, Ebc, Ebd, GridConsumption, selfConsRate = [], [], [], [], [], [], 0.0
	degreeSs, gridFeed_In, electCostBuy, electPriceSell = 0.0, [], [], []
	# for each data in the row
	for a in range(0, len(consumption)):
		# functions to calculate the energy behavior depending on the size of the storage battery
		energyDirCons(consumption[a], PVgeneration[a], Edu)
		energyChargingBattery(consumption[a], PVgeneration[a], Ebc)
		batteryCurrentS(consumption[a], PVgeneration[a], previousCharge, BatterySizeMain, batteryCurrentStorage)
		gridCons(consumption[a], PVgeneration[a], batteryCurrentStorage[a], previousCharge, GridConsumption)
		gridFeedIn(batteryCurrentStorage[a], BatterySizeMain, PVgeneration[a], consumption[a], gridFeed_In)
		previousCharge = energyBatteryDischarge(consumption[a], PVgeneration[a], Ebd, GridConsumption[a], previousCharge, gridFeed_In[a], Edu[a], BatterySizeMain)
		electricityCost(GridConsumption[a], electCost, electCostBuy)
		electricityPrice(gridFeed_In[a], electPrice, electPriceSell)
	selfConsRate = selfConsumptionRate(Edu, Ebc, PVgeneration, selfConsRate)
	degreeSs = degreeSelfSuff(Edu, Ebd, consumption, degreeSs)
	print "Battery Size:", BatterySizeMain," s: ", selfConsRate, " d", degreeSs
	# function to plot data
	if flagPlot:plotData(consumption, PVgeneration, Edu, Ebc, batteryCurrentStorage, GridConsumption, Ebd, gridFeed_In, BatterySizeMain, folder)
	# prepare file to save data
	# write titles
	file = (str(BatterySizeMain)+'kW.txt')
	directory =os.path.join(str(folder)+"/"+file)
	f = open(directory,'a')
	f.write(("Number")+'\t'+("Consumption (W)")+'\t'+("PV generation")+'\t'+ ("Edu")+'\t'+("Ebc")+'\t'+("BatteryCurrentStorage")+'\t'+("Grid Consumption")+'\t'+("Ebd")+'\t'+("Grid Feed-In")+'\t'+("Electricity Cost/Buy[Euro]")+'\t'+("Electricity Profit/Sell[Euro]")+'\t'+("Self-Consumption Rate [s]")+'\t'+("Degree of Self-Sufficiency [d]")+'\n')
	f.close()
	# write summations
	f = open(directory,'a')
	f.write(str(len(consumption))+'\t'+str(sum(consumption))+'\t'+str(sum(PVgeneration))+'\t'+ str(sum(Edu))+'\t'+str(sum(Ebc))+'\t'+str(sum(batteryCurrentStorage))+'\t'+str(sum(GridConsumption))+'\t'+str(sum(Ebd))+'\t'+str(sum(gridFeed_In))+'\t'+str(sum(electCostBuy))+'\t'+str(sum(electPriceSell))+'\t'+str(selfConsRate)+'\t'+str(degreeSs)+'\n')
	f.close()
	# write all data content
	for a in range(0, len(consumption)):
		f = open(directory,'a')
		f.write(str(a + 1)+'\t'+str(consumption[a])+'\t'+str(PVgeneration[a])+'\t'+ str(Edu[a])+'\t'+str(Ebc[a])+'\t'+str(batteryCurrentStorage[a])+'\t'+str(GridConsumption[a])+'\t'+str(Ebd[a])+'\t'+str(gridFeed_In[a])+'\t'+str(electCostBuy[a])+'\t'+str(electPriceSell[a])+'\n')
		f.close()
	return degreeSs, selfConsRate

# function to calculate the Energy Directly Used from PVgeneration (Edu)
def energyDirCons(consumption, PVgeneration, Edu):
	EduTemp = 0.0
	if PVgeneration < consumption:
		EduTemp = PVgeneration
	elif PVgeneration >= consumption:
		EduTemp = consumption
	Edu.append(EduTemp)

# function to calculate the Energy Used for charging the battery (Ebc)
def energyChargingBattery(consumption, PVgeneration, Ebc):
	EbcTemp = 0.0
	if ((PVgeneration == 0.0) or (PVgeneration < consumption)):
		EbcTemp = 0.0
	elif PVgeneration > consumption:
		EbcTemp = (PVgeneration - consumption)
	else:
		EbcTemp = 0.0
	Ebc.append(EbcTemp)

# function to calculate the Battery Current Storage
def batteryCurrentS(consumption, PVgeneration, previousCharge, batterySize, batteryCurrentStorage):
	batteryCurrentStorageTemp = ((PVgeneration - consumption) + previousCharge)
	if batteryCurrentStorageTemp < 0.0:
		batteryCurrentStorageTemp = 0.0
	if batteryCurrentStorageTemp > batterySize:
		batteryCurrentStorageTemp = batterySize
	batteryCurrentStorage.append(batteryCurrentStorageTemp)

# function to calculate the Grid Consumption
def gridCons(consumption, PVgeneration, batteryCurrentStorage, previousCharge, GridConsumption):
	GridConsumptionTemp = 0.0
	GridConsumptionTemp = (consumption - (PVgeneration + batteryCurrentStorage + previousCharge))
	if (PVgeneration + batteryCurrentStorage + previousCharge) > consumption:
		GridConsumptionTemp = 0.0
	GridConsumption.append(GridConsumptionTemp)

# function to calculate the grid feed In
def gridFeedIn(batteryCurrentStorage, batterySize, PVgeneration, consumption, gridFeed_In):
	gridFeedIn = 0.0
	if ((PVgeneration > consumption) & (batteryCurrentStorage >= batterySize)):
		#gridFeedIn = (PVgeneration - consumption) - batteryCurrentStorage
		gridFeedIn = (PVgeneration - batteryCurrentStorage- consumption)
		if gridFeedIn < 0:
			gridFeedIn = 0
	else:
		gridFeedIn = 0.0
	gridFeed_In.append(gridFeedIn)

# function to calculate the Energy Discharge from the Battery (Ebd)
def energyBatteryDischarge(consumption, PVgeneration, Ebd, GridConsumption, previousCharge, gridFeed_In, Edu, BatterySizeMain):
	EbdTemp = 0.0
	# Energy Battery Discharge (revisar)
	if ((consumption > PVgeneration) & (PVgeneration > 0)):
		# EbdTemp = batteryCurrentStorage - consumption
		EbdTemp = (consumption - PVgeneration)
		if EbdTemp < 0.0:
			EbdTemp = 0.0
		if EbdTemp > BatterySizeMain:
			EbdTemp = BatterySizeMain
		if EbdTemp > PVgeneration:
			EbdTemp = PVgeneration
	else:
		EbdTemp = 0.0
	Ebd.append(EbdTemp)
	# previous charge (keep this part at the end of this function)
	previousCharge = PVgeneration - consumption
	if previousCharge < 0.0:
		previousCharge = 0.0
	return previousCharge

# function to calculate the self-Consumption Rate
def selfConsumptionRate(Edu, Ebc, PVgeneration, selfConsRate):
	try:
		s = (sum(Edu) + sum(Ebc))/ sum(PVgeneration)
	except:
		s = 0.0
	selfConsRate = s
	return selfConsRate

# function to calculate degree of self-sufficiency (d)
def degreeSelfSuff(Edu, Ebd, consumption, degreeSs):
	try:
		d = (sum(Edu) + sum(Ebd)) / sum(consumption)
	except:
		d = 0.0
	degreeSs = d
	return degreeSs

# function to calculate the daily electricity cost (buy from grid)
def electricityCost(GridConsumption, electCost, electCostBuy):
	electCostBuy.append(GridConsumption * electCost)

# function to calculate the daily electricity price (sell to grid)
def electricityPrice(gridFeed_In, electPrice, electPriceSell):
	electPriceSell.append(gridFeed_In * electPrice)

# function to plot data
def plotData(consumption, PVgeneration, Edu, Ebc, batteryCurrentStorage, GridConsumption, Ebd, gridFeed_In, BatterySizeMain, folder):
	labels = list(range(-1,25))
	fig, ax = plt.subplots()
	fig.canvas.draw()

	plt.plot(consumption,'b', label="Consumption", linewidth=2)
	plt.plot(PVgeneration,'g', label="PV Generation", linewidth=2)
	plt.plot(Edu,'r', label="Energy directly used", linewidth=2)
	#plt.plot(Ebc,'c', label="Energy Used for charging Battery", linewidth=2)
	plt.plot(batteryCurrentStorage,'m', label="battery Current Storage", linewidth=2)
	plt.plot(GridConsumption,'y', label="Grid Supply", linewidth=2)
	plt.plot(Ebd,'k', label="Energy Battery Discharge", linewidth=2)
	plt.plot(gridFeed_In, 'c', label="Grid Feed-In", linewidth=2)
	plt.legend(loc=9, fontsize="x-small", ncol=3)
	plt.xlabel("Time")
	plt.ylabel("KWh")
	title = "Energy Flows of PV System (Battery Size: {}kW) ".format(BatterySizeMain)
	plt.title(title)
	
	loc = plticker.MultipleLocator(base=(12))
	ax.xaxis.set_major_locator(loc)
	ax.set_xticklabels(labels)
	plt.margins(0.01)
	plt.grid(True)
	fileTitle = str(str(BatterySizeMain)+'kW.png')
	directory =os.path.join(str(folder)+"/"+fileTitle)
	plt.savefig(directory)
	plt.show()
	#plt.show(block=False)
	#time.sleep(1)
	#plt.close()

# function to plot final data
def plotBatteryCapacity(DegreeOfSelfSuf, SelfConsumptionRate, BatterySizeMain, folder):
	#A = [0.654, 0.681, 0.707 ,0.788, 0.822, 0.822, 0.822, 0.822, 0.822] # sample excel calculated
	#B = [0.750, 0.781, 0.812, 0.905, 1.000, 1.000, 1.000, 1.000, 1.000] # sample excel calculated 
	xLabel = [0, 0, 5, 10, 25, 50, 75, 100, 150, 300] # X label scale
	fig, ax = plt.subplots()
	fig.canvas.draw()

	plt.plot(DegreeOfSelfSuf,'b', label="Degree of self-sufficiency (d)", linewidth=2)
	plt.plot(SelfConsumptionRate,'k', label="Degree of self-consumption (s)", linewidth=2)

	plt.legend(loc=9, fontsize="x-small", ncol=3)
	plt.xlabel("Battery Size Capacity [kWh]")
	plt.ylabel("")
	title = "Energy Flows of PV System"
	plt.title(title)

	loc = plticker.MultipleLocator(base=1)
	ax.xaxis.set_major_locator(loc)
	ax.set_xticklabels(xLabel)
	plt.axis([0.0, 8, (min(DegreeOfSelfSuf) - 0.1), (max(SelfConsumptionRate) + 0.1)])
	plt.margins(0.01)
	plt.grid(True)
	fileTitle = str("Energy Flows of PV System.png")
	directory =os.path.join(str(folder)+"/"+fileTitle)
	plt.savefig(directory)
	plt.show()

# function to create folder
def create_folder():
	try:
		# save name of new folder
		fld_name = str(date)
		# if folder name exist, try anotherone
		while os.path.exists(fld_name):
			a, fld_name = 1, str((date + "_" + a))
			a += 1
		# if folder name not exist, save new folder
		if not os.path.exists(fld_name):
			os.makedirs(fld_name)
			print ("New folder created: " + fld_name)
	except OSError as e:
		print (e)
	return fld_name

# initial information
def inputData():
	global electCost, electPrice
	dataCorrect, flagPlot = True, False
	while dataCorrect:
		try:
			electCost = float(raw_input("Write the electricity Cost [0.2670] Euro: "))
			electPrice = float(raw_input("Write the electricity Price [0.1114] Euro: "))
			plot = str(raw_input("To direct process press [Enter]. To see each graph press [g]?: "))
			if plot == "g": flagPlot = True
			dataCorrect = False
			return flagPlot
		except (ValueError, NameError):
			exit = raw_input('Oops! That was no valid character. Press Enter to try again or [e] and then Enter to exit: ')
			if exit == "e":
				print ("Exit")
				sys.exit(0)

# main
if __name__ == "__main__":
	# declare list of batteries size
	BatterySizeMain = [0.0, 0.07, 0.14, 0.35, 0.71, 1.07, 1.42, 2.14, 4.28]
	DegreeOfSelfSuf, SelfConsumptionRate = [], []
	try :
		# function to read excel data
		consumption, PVgeneration = readExcelData()
		# function to ask for data
		flagPlot = inputData()
		# function to create folder
		new_folder = create_folder()
		# main function
		for a in BatterySizeMain:
			degreeSs, selfConsRate = mainCode(consumption, PVgeneration, a, new_folder, flagPlot)
			DegreeOfSelfSuf.append(degreeSs)
			SelfConsumptionRate.append(selfConsRate)
			print "Output files: Data:", str(str(a) + "kW.txt"), " Image: ", str(str(a) + "kW.png")

		plotBatteryCapacity(DegreeOfSelfSuf, SelfConsumptionRate, BatterySizeMain, new_folder)
	except Exception, e:
		print ("Oops!  Something is wrong: ", e)
