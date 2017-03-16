import os

##  Several configured paths on where to find each 
PATH_RESOURCES = './var/libs/'
PATH_TEMP = './temp/'

PATH_IN = './input/'
PATH_OUT = './output/'



def checkMap(mapName):
	if not os.path.exists(mapName):
		os.makedirs(mapName)

def makeFolders():
	checkMap(PATH_RESOURCES)
	checkMap(PATH_TEMP)
	checkMap(PATH_IN)
	checkMap(PATH_OUT)
