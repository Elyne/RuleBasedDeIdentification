# -*- coding: utf-8 -*-
'''
Basic infrastructure for the UZA Text Mining engine
Initialisation file to de-identify several types of documents

Copyright (C) 2016 Elyne Scheurwegs, Kim Luyckx

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
Created on 26 jan. 2012

Read in the resources for de-identification

@author: Kim Luyckx
@edited by Elyne on 1 July 2014 for de-id project
'''
import os

from config import PATH_RESOURCES
topFile = os.path.join(PATH_RESOURCES+'lexicon/', "topFiltered.txt")

nameFile = os.path.join(PATH_RESOURCES+'lexicon/', "names.txt")
firstnameFile = os.path.join(PATH_RESOURCES+'lexicon/', "firstnames.txt")
streetFile = os.path.join(PATH_RESOURCES+'lexicon/', "streets.txt")
cityFile = os.path.join(PATH_RESOURCES+'lexicon/', "cities.txt")
countryFile = os.path.join(PATH_RESOURCES+'lexicon/', "countries.txt")
hospFile = os.path.join(PATH_RESOURCES+'lexicon/', "hospitals.txt")
mutFile = os.path.join(PATH_RESOURCES+'lexicon/', "mutinstitutions.txt")
networkFile = os.path.join(PATH_RESOURCES+'lexicon/', "legacynetworks.txt")
natFile = os.path.join(PATH_RESOURCES+'lexicon/', "nationalids.txt")
zipAbroadAZFile = os.path.join(PATH_RESOURCES+'lexicon/', "ZIPs-abroad-az.txt")

def getGazetteers():
	'''List of the 10000 most commonly used words in Dutch'''
	topList = openFile(topFile, typ="top")
	##topList = dict.fromkeys(topList, True)
	#print topList
	'''Read in lists of names etc. extracted from C2M'''
	names=openFile(nameFile,topList)
	firstnames=openFile(firstnameFile,topList)
	streets=openFile(streetFile,topList)
	cities=openFile(cityFile, topList)
	countries=openFile(countryFile,topList)
	hospitals=openFile(hospFile,topList)
	mut=openFile(mutFile,topList)
	networks=openFile(networkFile,topList)
	natids=openFile(natFile,topList)
#	zipazs=openFile(zipAbroadAZFile)
	DEIDlists=[names,firstnames,streets,cities,countries,hospitals,mut,networks,natids]

	return DEIDlists

def openFile(sourceFile,topList=[],typ=""):
	
	if os.path.isfile(sourceFile) and typ == "top":
		with open(sourceFile,"r") as fi:
			topList = fi.readlines()
		itemList = [ removeSpecials(w.lower().strip()) for w in topList ]# if w[0].islower() ]
		itemList = list(set(itemList))
	elif os.path.isfile(sourceFile):
		with open(sourceFile,'r') as fi:
			itemList = fi.readlines()
		if topList == []:
			itemList = [ item.strip() for item in itemList ]
		else:
			itemList = [ item.strip() for item in itemList if item.strip().lower() not in topList ]

	else:
		print(sourceFile)
		raise "Files do not exist. De-identification cannot be executed"
	#changed this to return a set
	#return itemList
	return set(itemList)

def removeSpecials(word):
	word=word.replace("\xc3\xab","e").replace("\xe8","e").replace("\xef","i").replace("\xdd","i").replace("\xe9","e").replace("\xeb","e").replace("\xcd","e")
	return word

if __name__ == "__main__":
	DEIDlists=getGazetteers()