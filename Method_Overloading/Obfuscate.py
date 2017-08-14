from collections import Counter
import argparse
import os

smaliPath = ""

def mainMethod(tmpPath):
    filteredInvoke = []
    filteredInvokeDetails = []
    fullInvokeDetails = []
    newMethodNames = []
    filteredMethodNames = []
    comb = []
    varC = []
    dictionary = {}

    filename = findFilename(tmpPath)

    print "\n<<< Obfuscating " + filename + ".smali... >>>"

    fileCodes = fileToCode(tmpPath)
    
    totalMethods = findMethods(fileCodes)
    returnTypes,parameters,method,originalInvoke,varC = findInfo(filename,totalMethods)
    fullInvokeDetails = formatInvoke(method,parameters,returnTypes,varC)
    filteredInvoke = filterInvoke(originalInvoke)
    filteredInvokeDetails = filterInvokeDetails(fullInvokeDetails)


    newMethodNames = findDups(fullInvokeDetails, filteredInvokeDetails)

    filteredMethodNames = filterNewMethods(newMethodNames)

    replaceMethodNames(filename,tmpPath,newMethodNames)

    makeDummy(tmpPath, originalInvoke, filteredInvoke, fullInvokeDetails, filteredInvokeDetails, filteredMethodNames)

    print "\n=================================================="
    print filename + ".smali obfuscated."
    print "==================================================\n\n"


def findFilename(tmpPath):
    with open(tmpPath) as f :
        filename = f.name.split("/")[len(f.name.split("/"))-1].split(".")[0]
    return filename


def findPosition(lst,item):
    i = 0
    for position in range(len(lst)):
        if lst[position] == item:
            i = position
        else:
            continue
    return i


def fileToCode(tmpPath):
    codes = []
    with open(tmpPath) as f :
        for line in f:
            codes.append(line)
    return codes    


def formatInvoke(method,parameters,returnTypes,varC):
    newList = []
    for i in range(len(method)):
        newList.append(method[i] + "@" + parameters[i] + "@" + returnTypes[i] + "@" + str(varC[i]))

    return newList


def filterInvokeDetails(detailList):
    filteredDetails = []
    for item in detailList:
        if item in filteredDetails:
            continue
        else:
            filteredDetails.append(item)
                    
    return filteredDetails
        


def filterInvoke(invokeList):
    filteredInvoke = []
    for item in invokeList:
        if item in filteredInvoke:
            continue
        else:
            filteredInvoke.append(item)
                    
    return filteredInvoke


def filterNewMethods(newMethods):
    temp = []
    filteredMethods = []
    for item in newMethods:
        if item.split("&")[0] in temp:
            continue
        else:
            temp.append(item.split("&")[0])
            filteredMethods.append(item)
    return filteredMethods


def findExistName(lst, tag):
    exist = 0
    for item in lst:
        if tag.split("@")[0] ==  item.split("@")[0]:
            exist = 1
        else:
            continue
    return exist

def findExistComb(lst, tag):
    exist = 0
    taggedList = []
    for i in range(len(lst)):
        if (tag.split("@")[1] + tag.split("@")[2]) ==  (lst[i].split("@")[1] + lst[i].split("@")[2]):
            taggedList.append(i)
            exist = exist + 1
        else:
            continue
    return exist, taggedList


def findDups(fullInvokeDetails, filteredInvokeDetails):
    alist = []
    rtnList = []
    for item in fullInvokeDetails:
        tag = ""
        exist, tagged = findExistComb(alist, item)
        if findExistName(alist, item) == 1:
            if exist != 0:
                if tagged:
                    tag = tagged[0]
                alist.append(item)
                rtnList.append(item + "&" + "" + "&" + str(tag))
            else:
                if tagged:
                    tag = tagged[0]
                alist.append(item)
                rtnList.append(item + "&" + "testing" + "&" + str(tag))
        else:
            if exist != 0:
                if tagged:
                    tag = tagged[0]
                alist.append(item)
                rtnList.append(item + "&" + "testing" + str(exist) + "&" + str(tag))
            else:
                if tagged:
                    tag = tagged[0]
                alist.append(item)
                rtnList.append(item + "&" + "testing" + "&" + str(tag))
    return rtnList




def replaceMethodNames(filename,tmpPath,newMethodList):
    codes = []
    count = 0
    with open(tmpPath) as f :
        for line in f:
            if "invoke-virtual " in line:
                if filename == line.split(";")[0].split("/")[len(line.split(";")[0].split("/"))-1]:
                    if newMethodList[count].split("&")[1] != "":
                        print "Renaming " + line.split("->")[1].split("(")[0] + " ----------> " + newMethodList[count].split("&")[1]
                        line = line.split("->")[0] + "->" + newMethodList[count].split("&")[1] + "(" + line.split("(")[1]
                        codes.append(line)
                    else:
                        line = line.split("->")[0] + "->" + newMethodList[int(newMethodList[count].split("&")[2])].split("&")[1] + "(" + line.split("(")[1]
                        codes.append(line)
                    count = count + 1
                else:
                    codes.append(line)
            else:
                codes.append(line)

    with open(tmpPath, "w") as f :
        for line in codes:
            f.write(line)

    
##    with open(tmpPath) as f :
##        for line in f:
##             if "invoke-virtual " in line:
##                if "Landroid/" not in line.split("}, ")[1].split("->")[0]:
##                    if "Ljava" not in line.split("}, ")[1].split("->")[0]:
##                        line = line.split("->")[0] + "->testing(" + line.split("(")[1]
##                        codes.append(line)
##                    else:
##                        codes.append(line)
##                else:
##                    codes.append(line)
##             else:
##                codes.append(line)
##    with open(tmpPath, "w") as f :
##        for line in codes:
##            f.write(line)     


def loopForParameters(parameters):
    returnPara = ""
    for parameter in parameters:
        if returnPara is "":
            returnPara = returnPara + parameter                         #Loop thru list of parameters
        elif returnPara is not "":
            returnPara = returnPara + parameter
    return returnPara



def findMethods(newCode):
    totalMethods = []
    method = []      
    for line in newCode:
        if ".method" in line:
           method.append(line)
        elif ".end method" in line:                                 #Find the methods in each smali file
            method.append(line)
            totalMethods.append(method)
            method = []
        else:
            method.append(line)
    return totalMethods


def findInfo(filename,totalMethods):
    returnTypes = []
    parameters = []
    method = []
    originalInvoke = []
    varC = []
    for methods in totalMethods:
        for line in methods:
            if "invoke-virtual " in line:
                if filename == line.split(";")[0].split("/")[len(line.split(";")[0].split("/"))-1]:
                    info = line.split("L")[1].split(";")[0].split("/")[len(line.split("L")[1].split(";")[0].split("/")) - 1]
                    #Find the return types and parameters of the invocations
                    returnTypes.append(line.split(")")[1])
                    parameters.append(line.split("(")[1].split(")")[0])
                    method.append(line.split("->")[1].split("(")[0]) 
                    varC.append(len(line.split("{")[1].split("}")[0].split(", ")))
                    originalInvoke.append(line)
                
    return returnTypes,parameters,method,originalInvoke,varC


def splitParams(string):

    objectP = ""
    params = []
    jump = 0
    skip = 0
    for letter in range(len(string)):
        if skip is 1:
            print string[letter]
            skip = 0
            continue
        if jump is 0:
            if string[letter] is "[":
                if string[letter+1] is "L":
                    for i in range(letter,len(string)):
                        if string[i] is not ";":
                            objectP = objectP + string[i]
                        elif string[i] is ";":
                            objectP = objectP + string[i]
                            jump = 1
                            params.append(objectP)
                            objectP = ""
                            break
                else:
                    if string[letter+1] is "I":
                        params.append(string[letter] + string[letter+1])
                        skip = 1
                    else:
                        params.append(string[letter] + string[letter+1])
                        params.append("DO NOT PRINT")
                        skip = 1
            elif string[letter] is "D":
                params.append(string[letter])
                params.append("DO NOT PRINT")
            elif string[letter] is "J":
                params.append(string[letter])
                params.append("DO NOT PRINT")
            elif string[letter-1] is "[":
                continue
                    
            elif string[letter] is "L":
                for i in range(letter,len(string)):
                    if string[i] is not ";":
                        objectP = objectP + string[i]
                    elif string[i] is ";":
                        objectP = objectP + string[i]
                        jump = 1
                        params.append(objectP)
                        objectP = ""
                        break
            else:
                params.append(string[letter])
        elif jump is 1:
            if string[letter] is ";":
                jump = 0
                continue
            else:
                continue
    return params


def makeDummy(tmpPath, originalInvoke, filteredInvoke, fullInvokeDetails, filteredInvokeDetails, newMethodNames):
    parameters = []
    returnType = []
    methodName = []
    varC = []
    
    for i in range(len(filteredInvokeDetails)):
        newPara = []
        paralist = []
        dummy = []
        
        methodName.append(filteredInvokeDetails[i].split("@")[0])
        parameters.append(filteredInvokeDetails[i].split("@")[1])
        returnType.append(filteredInvokeDetails[i].split("@")[2])
        varC.append(fullInvokeDetails[i].split("@")[3])
        
        for invoke in filteredInvoke:
            if methodName[i] == invoke.split("->")[1].split("(")[0]:
                newPara.append(len(invoke.split("{")[1].split("}")[0].split(", ")))


        paramType = splitParams(parameters[i])


        for k in range(len(paramType)):
            if paramType[k] != "DO NOT PRINT":
                paralist.append("p" + str(k + 1))
            else:
                paralist.append("#p" + str(k + 1))
        
        params = "p0"
        for j in range(len(paramType)):
            if paralist[j][0] != "#":
                
                params = params + ", " + paralist[j]
            else:
                params = params + ", " + paralist[j].strip("#")

        if newMethodNames[i].split("&")[1] != "":
            for invoke in filteredInvoke:
                needLocal = 0
                if methodName[i] == invoke.split("->")[1].split("(")[0]:
                    if returnType[i].split("\n")[0] is "D":
                        needLocal = 1
                    else:
                        for m in paramType:
                            if m == "DO NOT PRINT":
                                needLocal = 1
                                break
                    
                    if needLocal == 1:
                        print "Creating dummy method: " + '"' + newMethodNames[i].split("&")[1] + '"....'
                        dummy.append("\n\n\n.method public " + newMethodNames[i].split("&")[1] + "(" + parameters[i] + ")" + returnType[i].split("\n")[0] + "\n")
                        dummy.append( "    .locals 4\n")
                    elif needLocal == 0:
                        print "Creating dummy method: " + '"' + newMethodNames[i].split("&")[1] + '"....'
                        dummy.append("\n\n\n.method public " + newMethodNames[i].split("&")[1] + "(" + parameters[i] + ")" + returnType[i].split("\n")[0] + "\n")
                        dummy.append( "    .locals 0\n")
                    for j in range(len(paralist)):
                        if paralist[j][0] != "#":
                            dummy.append ("    .param " + paralist[j] + ' , "var' + str(j + 1) + '"   # ' + paramType[j] + "\n")
                        else:
                            continue
                    newInvoke = invoke.split("{")[0] + "{" + params + "}" + invoke.split("{")[1].split("}")[1]
                    dummy.append( newInvoke + "\n")
                    break


            if returnType[i].split("\n")[0] is "V":
                dummy.append( "    return-void\n")
                dummy.append( "\n.end method\n\n")
            elif returnType[i].split("\n")[0] is "I":
                dummy.append( "    move-result v0\n")
                dummy.append( "    return v0\n")
                dummy.append( "\n.end method\n\n")
            elif returnType[i].split("\n")[0] is "Z":
                dummy.append( "    move-result v0\n")
                dummy.append( "    return v0\n")
                dummy.append( "\n.end method\n\n")
            elif returnType[i].split("\n")[0] is "D":
                dummy.append( "    move-result-wide v0\n")
                dummy.append( "    return-wide v0\n")
                dummy.append( "\n.end method\n\n")
            elif returnType[i].split("\n")[0] is "J":
                dummy.append( "    move-result-wide v0\n")
                dummy.append( "    return-wide v0\n")
                dummy.append( "\n.end method\n\n")
            else:
                dummy.append( "    move-result-object v0\n")
                dummy.append( "    return-object v0\n")
                dummy.append( "\n.end method\n\n")

            
            for line in dummy:
                tmp = open(tmpPath,"r").read()
                open(tmpPath,"w").write(tmp + line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("direct", help="LOL")
    args = parser.parse_args()
    print args.direct
    smaliPath = args.direct

    for dirs,subdirs,files in os.walk(smaliPath):
        for fileName in files:
            if ".smali" in fileName:
                tmpPath = dirs +"/"+fileName
                tmp = open(tmpPath,"r").read()
                mainMethod(tmpPath)


