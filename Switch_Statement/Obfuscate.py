#LATEST UPDATE: 310717

import sys
import os
import re


smaliPath = sys.argv[1]+"/smali" 
smaliFile = 0 # Determine no.of smali files obfuscated
headerCount = 0
obfTechCounter = 0 # Determine no.of obfuscation completed
avoidList = ["invoke-virtual", "invoke-super","invoke-direct", "move-result-object", "invoke-static", "move-result-wide", "move-object", "move-result", "move-exception", "return", "monitor-enter","monitor-exit","check-cast","invoke-polymorphic","invoke-custom","catch","goto","throw","0x",":pswitch",":sswitch",".annotation"]

avoidList2 = [".array-data",".annotation","try_start"]
switchList = [] #To keep track which switch has been inserted


def RepresentsInt(s): # Check if it's an int
	try:
		int(s)
		return True

	except ValueError:
		return False

def checkTotalRegisterUsed(x,y): # Check if no. of register used is less than 15
	totalNoUsed = int(x) + y 

	if totalNoUsed < 15:
		return True

	else:
		return False



def createFile(fileName, counterLine, headerCount): #Create a file to store details [Which smali files are modified]
	 

	try:
		f1 = open("switchObfuscation.txt", "a")

	except FileNotFoundError:

		f1 = open("switchObfuscation.txt", "w")
		
	if headerCount == 0:
		f1.write("%-40s %50s\n" %("Smali File Inserted ","On Line Number"))
		f1.write("%-40s %50s\n" % ("=====================", "==============\n"))
		headerCount+= 1

	f1.write("%s %-80s\n" % (fileName,counterLine))

	f1.close()

	return headerCount




for dirs,subdirs,files in os.walk(smaliPath):
	if "android" not in dirs:
	    for fileName in files:
	
		if ".smali" in fileName: #To determine all the smali files


			tmpPath = dirs +"/"+fileName #APK File

			isMethod = False
			endMethod = False
			localModified = False
			switchStatement = False
			check = False
			arrayStatement = False
		

			with open(tmpPath,"r") as in_file:
				buf = in_file.readlines() #For writing
				tmpBuf = buf #For reading no. of .locals & parameters

				methodLine = -2 #No. of lines in a method, dont include, .method & .locals
				noOfRegister = 0 #Keep track of no. of register


				deductOneValue = 0

				counterLine = 0 # Count no. of lines in smali
				countToDivide = 0 # Determine no. of times already inserted code
				methodLine6 = -1 # Determine if 6 lines of codes is "executed"
				countPswitch = 0 #Count if second switch statement to inside goto
				innerSwitchCounter = 0 #count no.of statement inserted
				switchInserted = False #Check if got insert any statements in or not


			#To Insert Switch Statement Codes in Between the Codes
			with open(tmpPath,"w") as out_file:
			
				for i, line in enumerate(buf): # i = count no.of lines, start from 1

					canInsert = False # Check if can increase register & insert code
					counterLine += 1
				
					if line != "\n" and (localModified is True and endMethod is False and arrayStatement is False):

						methodLine6 += 1
					

					if localModified is True and endMethod is False:				
						for l in avoidList2:
							if l in line:
								#switchStatement = True
								arrayStatement = True
								localModified = False
								methodLine6 -= 2
								break
								

					if switchStatement is True: #Switch Statement is found, dont add in 
						
						endMethod = True


					if ".method" in line: # Determine if it's a method
					
						isMethod = True
						endMethod = False

						highestPValue = 0 # Track total no. of parameter used



						for x in range (len(tmpBuf)): # Used to determine no.of parameter used

							if x > i:#once hit over the line no.

								pIndex1 = 0 #p index for 1 digit
								pIndex2 = 0 #p index for 2 digit
								stringNo = ""



								if ".end method" in tmpBuf[x]:
								
									highestPValue += 1
									noOfParameters = highestPValue

									break

								elif ".packed-switch" in tmpBuf[x] or ".sparse-switch" in tmpBuf[x]:

									switchStatement = True
									break
								else:
								
									if tmpBuf[x] != "\n" or ".locals" not in line:
										methodLine += 1


									pIndex = 0


									for p in range (len(tmpBuf[x])): #To find the index of "p" in the line
								
										if tmpBuf[x][p] is "p" and p < ((len(tmpBuf[x])) - 2):
											pIndex1 = p + 1
											pIndex2 = p + 2

											if RepresentsInt(tmpBuf[x][pIndex1]) is True and RepresentsInt(tmpBuf[x][pIndex2]) is True: #Determine if 2 digit

											
												stringNo = tmpBuf[x][pIndex1] + tmpBuf[x][pIndex2]
												pIndex = int(tmpBuf[x][pIndex1] + tmpBuf[x][pIndex2])
											


											elif RepresentsInt(tmpBuf[x][pIndex2]) is False and RepresentsInt(tmpBuf[x][pIndex1]) is True: #Determine if 1 digit

											
												stringNo = tmpBuf[x][pIndex1]
												pIndex = int(tmpBuf[x][pIndex1])

											

											#Find highest no. of parameter used
											if pIndex > highestPValue:
												highestPValue = pIndex





					if ".locals" in line and isMethod is True: 

						stringNo2 = line[12] + line[13]
						stringNo2 = int(stringNo2)
					


						if int(line[12]) in range (1,9) and line[13].isspace() and checkTotalRegisterUsed(line[12], highestPValue) is True: # single digit value & more than 0
						
										
							lineValue = int(line[12]) + 1
							noOfRegister = highestPValue + lineValue
							lineValue = str(lineValue)

							if noOfRegister <= 15:
								canInsert = True

							else:
								canInsert = False


						if stringNo2 > 9 and checkTotalRegisterUsed(stringNo2,highestPValue) is True:

						
							lineValue = stringNo2 + 1
							noOfRegister = highestPValue + lineValue
							lineValue = str(lineValue)


							if noOfRegister <= 15:
								canInsert = True

							else:
								canInsert = False

				
			

						if canInsert is True: #Modify the .locals values
					
							#pointToStop += methodLine #To know where to stop

							out_file.write("    .locals " + lineValue + "\n\n")


							lineValue = int(lineValue)

							#deductTwoValue = lineValue - 2
							deductOneValue = lineValue - 1

							#deductTwoValue = str(deductTwoValue)
							deductOneValue = str(deductOneValue)
					
						
							i += 1
							buf.insert(i, "\n    const/4 v" +  deductOneValue + ", 0x0\n\n")
				
									
							counterLine += 2

							headerCount = createFile(tmpPath, counterLine, headerCount)
	
							i-= 2
							obfTechCounter += 1


							line = " "
							localModified = True
							canInsert = False
							isMethod = False
							endMethod = False

				


					if ".end method" in line and localModified is True: 

						if switchStatement is False and switchInserted is True:
							out_file.write("\n    :pswitchObf" + str(obfTechCounter) + "_data_0" + "\n")
							out_file.write("    .packed-switch 0x0\n")

							for switches in switchList:
								out_file.write("        "+ switches + "\n")


					
							out_file.write("    .end packed-switch\n")

						del switchList[:]
					
						endMethod = True
						localModified = False
						arrayStatement = False
						switchInserted = False
				
						methodLine = -2
						countToDivide = 0
						methodLine6 = 0
						countPswitch = 0 
						innerSwitchCounter = 0
						obfTechCounter += 1
				


					if localModified is True and endMethod is False and methodLine6 == 10 and arrayStatement is False:

						for a in avoidList:
							if a in line:
							
								methodLine6 -= 2
								check = True

								break
						




						if methodLine6 == 10 and arrayStatement is False and check is True and localModified is True: # If after check still 6

							timesToDivide = methodLine // 10
							listValue = ""
						

							if countToDivide < timesToDivide:

								switchInserted = True
							
								if countPswitch == 0:							
								
									i += 1
									buf.insert(i,"\n    packed-switch v" + deductOneValue + ", :pswitchObf" +str(obfTechCounter)  +"_data_0\n\n")
									i += 1
									buf.insert(i,"\n    :pswitchObf" + str(obfTechCounter) + "_" + str(innerSwitchCounter)) 
									listValue = ":pswitchObf" + str(obfTechCounter) + "_" + str(innerSwitchCounter)
									#switchList.append(listValue)
						
												
									i+= 2
									headerCount = createFile(tmpPath, i, headerCount)
									i-= 4

									countPswitch += 1

								else: 


									i += 1
									buf.insert(i,"\n    goto :pswitchObf" + str(obfTechCounter) + "_" + str(innerSwitchCounter)+"\n\n    :pswitchObf" + str(obfTechCounter) + "_" + str(innerSwitchCounter))
									
									listValue = ":pswitchObf" + str(obfTechCounter) + "_" + str(innerSwitchCounter)
								
												
									i+= 1
									headerCount = createFile(tmpPath, i, headerCount)
									i-= 4


							
								
								countToDivide += 1
								#obfTechCounter += 1
								methodLine6 = -1
								innerSwitchCounter += 1
								switchList.append(listValue)
							

							elif countToDivide >= timesToDivide:
								countToDivide = 0
								methodLine6 = -1
								localModified = False 
								switchStatement = False
							
				
					if arrayStatement is True and localModified is False and endMethod is False:

					
							if ".end sparse-switch" in line or ".end packet-switch" in line or ".end array-data" in line or ".end annotation" in line or "try_end" in line:
							
								arrayStatement = False
								localModified = True
								countToDivide = 0
							



				



					out_file.write(line)




			

