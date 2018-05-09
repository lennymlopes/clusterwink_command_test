import RPi.GPIO as GPIO
import spidev
import time


class ReadCRCError(Exception):
	pass

class ReadNoAck(Exception):
	pass

def CRC8(dataList,initial=0,poly=0x07):
	crc = 0x00
	for inByte in dataList:
		for i in range(8):
			temp = (crc^inByte)&0x80
			crc <<= 1
			if temp != 0:
				crc ^=poly
			inByte <<= 1
		crc &= 0xFF
	return crc

def writeCommand(dataList):
	dataList = [len(dataList)+2]+dataList
	dataList.append(CRC8(dataList))
	# print("spi packet: ",[hex(x) for x in dataList])
	GPIO.output(8,GPIO.LOW)
	spi.xfer(dataList,100000,10,8)
	GPIO.output(8,GPIO.HIGH)

def readCommand(command):
	dataList = [1,command,0,0]
	recList = []
	GPIO.output(8,GPIO.LOW)
	recList = spi.xfer(dataList,100000,10,8)
	if recList[2] != 0x01:
		raise ReadNoAck("Slave did not react to the read command! (No acknowledge)")
	if recList[3] < 0x03:
		raise ReadCRCError("Data length byte is too short!")
	length = recList[3]
	recList = [length]
	dataList = [0]*(length-1)
	recList = recList + spi.xfer(dataList,100000,10,8)
	GPIO.output(8,GPIO.HIGH)

	if (CRC8(recList) != 0) or (recList[1] != command):
		raise ReadCRCError("Transmission errors detected!")
	return recList[2:-1]



spi = spidev.SpiDev()
spi.open(0,1)
spi.max_speed_hz = 100000
spi.mode = 0b00

GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.OUT,initial=GPIO.HIGH)
GPIO.setup(8,GPIO.OUT,initial=GPIO.HIGH)
# GPIO.setup(7,GPIO.OUT,initial=GPIO.HIGH)


try:
	while True:
		print("[0] PLED enable")
		print("[1] PLED disable")
		print("[2] PLED dutycycle")
		print("[3] PLED animation stop")
		print("[4] PLED fade")
		print("[5] PLED strobe")
		print("[6] Audio enable")
		print("[7] Audio disable")
		print("[8] Audio volume")
		print("[9] RGB off")
		print("[10] RGB single color")
		print("[11] RGB mirrored gradient")
		print("[12] RGB animation off")
		print("[13] RGB fade")
		print("[14] RGB gradient fade")
		print("[15] Read status")
		print("[16] Read duty")
		print("[17] Read temperature")
		print("[18] Read PLED fade")

		commNo = int(input("Select the command: "))

		if commNo == 0:
			writeCommand([0x11])
		elif commNo == 1:
			writeCommand([0x12])
		elif commNo == 2:
			duty = int(input("Specify the dutycycle in percent: "))
			writeCommand([0x13,duty])
		elif commNo == 3:
			writeCommand([0x14])
		elif commNo == 4:
			start = int(input("Specify the dutycycle in percent at the beginning: "))
			stop = int(input("Specify the dutycycle in percent at the end: "))
			timespan = int(input("Specify the timespan (will be multiplied by 30): "))
			writeCommand([0x15,start,stop,timespan])
		elif commNo == 5:
			duty = int(input("Specify the dutycycle in percent: "))
			on = int(input("Specify the on time in ms (will be multiplied by 10): "))
			off = int(input("Specify the off time in ms (will be multiplied by 10): "))
			writeCommand([0x16,duty,on,off])
		elif commNo == 6:
			writeCommand([0x21])
		elif commNo == 7:
			writeCommand([0x22])
		elif commNo == 8:
			volume = int(input("Specify the volume [0-64]: "))
			writeCommand([0x23,volume])
		elif commNo == 9:
			writeCommand([0x31])
		elif commNo == 10:
			red = int(input("Red value: "))
			green = int(input("Green value: "))
			blue = int(input("Blue value: "))
			writeCommand([0x32,red,green,blue])
		elif commNo == 11:
			startRed = int(input("Red start value: "))
			startGreen = int(input("Green start value: "))
			startBlue = int(input("Blue start value: "))
			stopRed = int(input("Red stop value: "))
			stopGreen = int(input("Green stop value: "))
			stopBlue = int(input("Blue stop value: "))
			writeCommand([0x33,startRed,startGreen,startBlue,stopRed,stopGreen,stopBlue])
		elif commNo == 12:
			writeCommand([0x41])
		elif commNo == 13:
			startRed = int(input("Red start value: "))
			startGreen = int(input("Green start value: "))
			startBlue = int(input("Blue start value: "))
			stopRed = int(input("Red stop value: "))
			stopGreen = int(input("Green stop value: "))
			stopBlue = int(input("Blue stop value: "))
			time = int(input("Time in seconds: "))
			bounce = int(input("Bounce [off:1/on:2]: "))
			writeCommand([0x42,startRed,startGreen,startBlue,stopRed,stopGreen,stopBlue,time,bounce])
		elif commNo == 14:
			startRed = int(input("Red start value: "))
			startGreen = int(input("Green start value: "))
			startBlue = int(input("Blue start value: "))
			startMiddleRed = int(input("Red middle start value: "))
			startMiddleGreen = int(input("Green middle start value: "))
			startMiddleBlue = int(input("Blue middle start value: "))
			
			stopRed = int(input("Red stop value: "))
			stopGreen = int(input("Green stop value: "))
			stopBlue = int(input("Blue stop value: "))
			stopMiddleRed = int(input("Red middle stop value: "))
			stopMiddleGreen = int(input("Green middle stop value: "))
			stopMiddleBlue = int(input("Blue middle stop value: "))
			
			time = int(input("Time in seconds: "))
			bounce = int(input("Bounce [off:1/on:2]: "))
			
			writeCommand([0x43,startRed,startGreen,startBlue,startMiddleRed,startMiddleGreen,startMiddleBlue,stopRed,stopGreen,stopBlue,stopMiddleRed,stopMiddleGreen,stopMiddleBlue,time,bounce])
			
		elif commNo == 15:
			recList = readCommand(0xF1)
			print("Status: {:02X}".format(recList[0]))
		elif commNo == 16:
			recList = readCommand(0xF2)
			print("Dutycycle: {}%".format(recList[0]))
		elif commNo == 17:
			recList = readCommand(0xF3)
			print("Temperature: {}°C".format(recList[0]))
		elif commNo == 18:
			recList = readCommand(0xF4)
			print(recList)

		print()

except KeyboardInterrupt:
	spi.close()
	GPIO.cleanup()
	print()
