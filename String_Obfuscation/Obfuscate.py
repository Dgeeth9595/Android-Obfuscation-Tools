import sys
import os
from collections import OrderedDict
from itertools import izip, repeat
from string import ascii_lowercase
import itertools
counter=0
count=1
smaliPath = sys.argv[1]+"/smali"
#smaliPath = "/root/Desktop/Testing/output/test1/smali"
def FileClassRenaming():
	#Declaration
	global counter #counter
	classfile=[] # Arraylist of file names
	V7files=['/v7/view','/v7/widget'] # restricted folders
	Ignorelist=['AlertController','ActionBarContainer','ActionMenuView','ActivityChooserView','AlertDialogLayout','ButtonBarLayout','ContentFrameLayout','DialogTitle','FitWindowsFrameLayout','FitWindowsLinearLayout','GridLayoutManager','LinearLayoutManager','SearchView','Toolbar','ViewStubCompat','ActionMenuItemView','ExpandedMenuView','ListMenuItemView','NavigationMenuItemView','NestedScrollView','NavigationMenuView','SnackbarContentLayout','AppBarLayout','BottomNavigationView','BottomSheetBehavior','CheckableImageButton','CoordinatorLayout','FloatingActionButton','Snackbar','Keep','MainActivity']#restricted files
	#Search for files	
	for dirs,subdirs,files in os.walk(smaliPath): #Finding all directory and files
		for fileName in files: #Taking out each file capture
			for V7 in range(0, len(V7files)): #Condition for non V7 files
				if V7files[V7] not in dirs:
					if ".smali" in fileName: #Only smali files will be renamed
						fileName = fileName.replace('.smali','') #Remove .smali left with name
						classfile.append(fileName) #Append into arraylist

	#Normalizing c
	classfile = list(OrderedDict(izip(classfile, repeat(None)))) #Remove duplicates
	classfile = [w.replace(' \n','')for w in classfile] #Remove space and next line
	classfile.sort(key=len,reverse=True) #Sorting from longest to shortest

	#Execute Renaming
	for alpha in iter_all_strings(): #Calling other functions
		for Ignore in range(0, len(Ignorelist)): # Loop for ignorelist
			if Ignorelist[Ignore] not in classfile[counter]: #Check for ignore list
				if '$' not in classfile[counter]: #Dollar sign condition check
					if Ignore+1 == len(Ignorelist): #Break off point condition
						DolReplace = "find "+sys.argv[1]+" -type f -exec sed -i 's/\\b"+classfile[counter]+"\\b/"+alpha+"/g'  {} +"
						DolRename = "find "+sys.argv[1]+" -type f -exec rename 's/"+classfile[counter]+".smali/"+alpha+".smali/g'   {} +"				
						os.system(DolReplace) #Execute command
						os.system(DolRename)  #Execute command
						#print classfile[counter],'\nObfuscated class name : ',alpha," ",counter+1,"/",len(classfile),' Files\n'
						counter = counter + 1
				else:				#Else without dollar sign
					if Ignore+1 == len(Ignorelist):  #Break off point condition
						NonDolReplace = "find "+sys.argv[1]+" -type f -exec sed -i 's/"+classfile[counter].replace("$","\$")+"/"+alpha+"/g'  {} +"
						NonDolRename = "find "+sys.argv[1]+" -type f -exec rename 's/"+classfile[counter].replace("$","\$")+".smali/"+alpha+".smali/g'   {} +"	
						os.system(NonDolReplace)  #Execute command
						os.system(NonDolRename)   #Execute command
						#print classfile[counter],'\nObfuscated class name : ',alpha," ",counter+1,"/",len(classfile),' Files\n'	
						counter = counter + 1
    		if counter == len(classfile):# break condition
        		break

#---------------------------------------------BREAK POINT-------------------------------------------------
def FolderRenaming():
	names=[] #folder rename names list
	roots=[] #folder rename dir list  
	for root, dirs, files in os.walk(smaliPath,topdown=False):# loop for folders
		for name in dirs:
			if "annotation" != name:# main files
				if "graphics" != name:
					if "v7" != name:
						if "v4" != name:
							if "graphics" not in root:
								if "v7" not in root:
									if "v4" not in root:
										names.append(name)#rename name all files
										roots.append(os.path.join(root, name))# add into roots
	i=0
	for alpha in iter_all_strings():# a to z loop function
		replace= "find "+sys.argv[1]+" -type f -exec sed -i 's/\\b"+names[i]+"\\b/"+alpha+"/g'  {} +" # search and replace folder name	
		rename = "mv " + roots[i] + " " + roots[i].replace(names[i],alpha)# rename of folder name
		os.system(replace) # execute
		os.system(rename)# execute
		#print 'Obfuscated folder directory name : ',names[i]," ",i+1,"/",len(names),' Folders\nRename to : '+alpha
		i+=1 # print result
		if i==len(names):# break condition
			break
		

#---------------------------------------------BREAK POINT-------------------------------------------------
def iter_all_strings():# A to z replacement method
    size = 1
    while True:
        for s in itertools.product(ascii_lowercase, repeat=size):
            yield "".join(s)
        size +=1


if __name__ == '__main__':
	FileClassRenaming()
	FolderRenaming()
	print sys.argv[1]


