import sys
import os
import io
import re

class Obfuscate():

	def AddDecryptionCode(self,filePath):
		command5 = "cat "+ filePath +" | grep -w '.line' | sort -k2n | tail -1 | awk '{print $NF}'"
		os.system(command5 + " > out")
		lastLineNum = open("out","r").read().rstrip()

		if lastLineNum == "":
			s = open("InputMethod_SE.in","r").read()
			for i in range(1,16): 
				s = s.replace(".line xxx"+str(i)+" ", "")
			
		else:
			s = io.open("InputMethod_SE.in","r").read()
			for i in range(1,16):
				lastLineNum=int(lastLineNum)				
				lastLineNum+=1
				s = s.replace("xxx"+str(i)+" ",str(lastLineNum))
			
		f = open(filePath,"r").read()
		open(filePath,"w").write(f+"\n\n"+s)


	def EncryptStrings(self,filePath):

		filePathThing = re.split("/",filePath)
		insFilePath = ""
		count = 0
		
		for i in filePathThing:
		    count+=1
		    if count == len(filePathThing):
			insFilePath += i
        	    elif count > 3:
			insFilePath += i +"/"
		insFilePath=insFilePath.replace(".smali","")
		

		StrDic = {}
		fileHeaders=""	
		fileContent=""
		fileContentBool = False	
		with open(filePath) as s:	
		   for line in s:				
			if ".method" in line:
				fileContentBool=True
				fileContent+=line
			elif fileContentBool:
				fileContent+=line
			else:
				fileHeaders+=line

		#Get Strings in MainActivity File
		command2 = 'cat '+ filePath +' | awk "/.method/{f=1} /.end method/{f=0;print} f" |grep "const-string" > out'
		
		os.system(command2)
		lines = open('out').readlines()



		if len(lines) != 0:			
			print "Num of Strings: ", len(lines), "...\n"
			for line in lines:
				words=line.rstrip().lstrip().split(" ")

				#print "Variable Num: ", words[1].replace(",","")			

				orgStr = ""
				for i in range (2,len(words)): orgStr += words[i] + " "
				orgStr = orgStr.lstrip().rstrip()
				#print "UnEncrypted OrgStr: ", orgStr

				if "(" in orgStr or "`" in orgStr or orgStr == "":
					pass
				else:					
					#Encrypt Orginal String
					command3 = "java JavaStrEnc " + orgStr
					os.system(command3 + " > out")
					encStr = '"'+open("out","r").read().rstrip()+'"'
					StrDic[orgStr] = encStr
					
					
					insFilePath=insFilePath.split("smali/")[-1]
					if int(words[1][1:len(words[1])-1]) > 15:
						encStr += '\n\n    invoke-static/range {'+ words[1].replace(",","") +" .. "+words[1].replace(",","")+'}, L'+insFilePath+';->decrypt(Ljava/lang/String;)Ljava/lang/String;\n    move-result-object '+ words[1].replace(",","")				
					else:
						encStr += '\n\n    invoke-static {'+ words[1].replace(",","") +'}, L'+insFilePath+';->decrypt(Ljava/lang/String;)Ljava/lang/String;\n    move-result-object '+ words[1].replace(",","")
					NewOrgStr = "const-string "+words[1]+" "+orgStr 
					encStr = "const-string "+words[1]+" "+encStr
					
					fileContent = fileContent.replace(NewOrgStr,encStr)
			
			with open(filePath, "w") as f:
				f.write(fileHeaders+"\n"+fileContent+"\n")

		        self.AddDecryptionCode(filePath)		



		
	def FindActivityClass(self):
		#Get Activity File
		command1 = 'grep -l -rnw '+ self.directory +' -e "***Activity***"'
		os.system(command1 + " > out")
		lines = open("out","r").readlines()		
		for line in lines:
			if "smali/android/support" not in line:
				ActivityClass = line.rstrip().replace("$","\$")
				self.TransversePath.append(ActivityClass)

	def FindMainActivityClass(self):
		#Get MainActivity File
		command1 = 'grep -l -rnw '+ self.directory +' -e "***AppCompatActivity***"'
		os.system(command1 + " > out")
		mainActivity = open("out","r").readline().rstrip()
		if "smali/android/support" in mainActivity:
			lines = open("out","r").readlines()		
			for line in lines:
				if "smali/android/support" not in line:
					mainActivity = line.rstrip()
		self.TransversePath.append(mainActivity)

	
	def __init__(self):
		if(len(sys.argv) > 1):
			self.directory=sys.argv[1]
			self.TransversePath= []
			self.FindMainActivityClass()

			self.FindActivityClass()
			print "Done searching for files..."
			print "Num of files: ", len(self.TransversePath),"...\n"


			for filePath in self.TransversePath:
			    if filePath != "":
				filePath=filePath.replace("\\","")
				print "Working on file ", filePath, "..."
				self.EncryptStrings(filePath)
				
				print "\n"


		else:
			print "Please input decompiled apk path"


Obfuscate()
