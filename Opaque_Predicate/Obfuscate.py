#LATEST UPDATE: 240717

import sys
import os
import re


smaliPath = sys.argv[1]+"/smali"
smaliFile = 0 # Determine no.of smali files obfuscated
headerCount = 0
obfTechCounter = 0 # Determine no.of obfuscation completed
avoidList = ["invoke-virtual", "invoke-super","invoke-direct", "move-result-object", "invoke-static", "move-result-wide", "move-object", "move-result", "move-exception", "return", "monitor-enter","monitor-exit","check-cast","invoke-polymorphic","invoke-custom","catch","goto","throw","0x",":pswitch",":sswitch",".annotation"]

avoidList2 = [".sparse-switch",".packed-switch",".array-data",".annotation","try_start"]


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
		f1 = open("opaquepredicate.txt", "a")

	except FileNotFoundError:

		f1 = open("opaquepredicate.txt", "w")
		
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

			with open(tmpPath,"r") as in_file:
				buf = in_file.readlines() #For writing
				tmpBuf = buf #For reading no. of .locals & parameters

				methodLine = -2 #No. of lines in a method, dont include, .method & .locals
				noOfRegister = 0 #Keep track of no. of register


				deductTwoValue = 0
				deductOneValue = 0

				counterLine = 0 # Count no. of lines in smali
				countToDivide = 0 # Determine no. of times already inserted code
				methodLine6 = -1 # Determine if 6 lines of codes is "executed"
	

			#To Insert Opaque Predicate Codes in Between the Codes
			with open(tmpPath,"w") as out_file:
			
				for i, line in enumerate(buf): # i = count no.of lines, start from 1

					canInsert = False # Check if can increase register & insert code
					counterLine += 1
				
					if line != "\n" and (localModified is True and endMethod is False and switchStatement is False):

						methodLine6 += 1

					if localModified is True and endMethod is False:				
						for l in avoidList2:
							if l in line:
								switchStatement = True
								localModified = False
								methodLine6 -= 2
								break
								


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
						
										
							lineValue = int(line[12]) + 2
							noOfRegister = highestPValue + lineValue
							lineValue = str(lineValue)

							if noOfRegister <= 15:
								canInsert = True

							else:
								canInsert = False


						if stringNo2 > 9 and checkTotalRegisterUsed(stringNo2,highestPValue) is True:

						
							lineValue = stringNo2 + 2
							noOfRegister = highestPValue + lineValue
							lineValue = str(lineValue)


							if noOfRegister <= 15:
								canInsert = True

							else:
								canInsert = False

				
			

						if canInsert is True: #Modify the .locals values
					
						
							out_file.write("    .locals " + lineValue + "\n\n")


							lineValue = int(lineValue)

							deductTwoValue = lineValue - 2
							deductOneValue = lineValue - 1

							deductTwoValue = str(deductTwoValue)
							deductOneValue = str(deductOneValue)
					
						
							i += 1
							buf.insert(i, "\n    const/4 v" +  deductTwoValue + ", 0x2\n    const/4 v"+ deductOneValue +", 0x4\n\n\n")
				
									
							i += 1
							buf.insert(i, "\n    if-lt v"+ deductTwoValue +",v"+ deductOneValue + ", :obftech" + str(obfTechCounter) + "\n\n    :obftech" + str(obfTechCounter)) # ALWAYS TRUE
	

							counterLine += 8

							headerCount = createFile(tmpPath, counterLine, headerCount)
	
							i-= 2
							obfTechCounter += 1


							line = " "
							localModified = True
							canInsert = False
							isMethod = False
							endMethod = False



					if ".end method" in line:
					
						endMethod = True
						localModified = False
						switchStatement = False
				
						methodLine = -2
						countToDivide = 0
						methodLine6 = 0



					
				

					if localModified is True and endMethod is False and methodLine6 == 10 and switchStatement is False:

						for a in avoidList:
							if a in line:
							
								methodLine6 -= 2
								check = True

								break
						




						if methodLine6 == 10 and switchStatement is False and check is True and localModified is True: # If after check still 6

							timesToDivide = methodLine // 10
						

							if countToDivide < timesToDivide:
							
								i+=1
								buf.insert(i,"\n    if-gt v"+ deductOneValue +",v"+ deductTwoValue + ", :obftech" + str(obfTechCounter) + "\n\n    :obftech" + str(obfTechCounter) + "\n") # ALWAYS TRUE
						
												
								i+= 2
								headerCount = createFile(tmpPath, i, headerCount)
								i-= 3

								countToDivide += 1
								obfTechCounter += 1
								methodLine6 = -1

							elif countToDivide >= timesToDivide:
								countToDivide = 0
								methodLine6 = -1
								localModified = False
								switchStatement = False



					if switchStatement is True and localModified is False and endMethod is False:

					
							if ".end sparse-switch" in line or ".end packet-switch" in line or ".end array-data" in line or ".end annotation" in line or "try_end" in line:
							
								switchStatement = False
								localModified = True
								countToDivide = 0
							






					out_file.write(line)




			
#Returns the decompiled filePath
print sys.argv[1]
