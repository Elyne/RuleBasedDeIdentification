# -*- coding: utf-8 -*-
'''
Basic infrastructure for the Text Mining engine

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

1- read in the data

2- perform processing in the different modules
2a- text segmentation
2b- tokenization
2c- de-identification

@author: Kim Luyckx
@edited by Elyne on 1 July 2014 for de-id project
allows tagging instead of replacing dates


'''

months=["januari", "jan", "februari", "feb", "maart", "mar", "mrt", "april", "apr", "mei", "juni", "jun", "juli", "jul", "augustus", "aug", "september", "sept", "sep", "oktober", "okt", "november", "nov", "december", "dec"]

from DeIdColl.deltaCalculator import deltaCalculator
import re

class DeIdentifier(object):
	def __init__(self,dataPoint,DEIDlists):
		self.dataPoint=dataPoint
		[self.names,self.firstnames,self.streets,self.cities,self.countries,self.hospitals,self.mut,self.networks,self.natids]=DEIDlists
		return

	
	def deidentifyRAW(self,dateTag=0):
		'''frequency counters'''
		freqcnt = dict()
		freqcat = dict()
	
	
		'''De-identify raw text'''
#		print "---RAW---", self.dataPoint
		'''Simple tokenization, but keeping all information'''
		words=re.split(r'(\s|<newline>|\.|<tab>|:|,|;|\?|!|-|\"|\'|\)|\(|<page>|<horline>|<arrowright>|<italic>|<dash>|<registered>|<dotdotdot>|<euro>|<circa>|<lte>|<arrowup>|<micro>|<alpha>|<born>)',self.dataPoint)
#		with open("output.txt","a") as out:
#			out.write(str(words)+"\n")

#		print "---TOK---", words
#		print "---performing DEID---"

		'''1. From Gazetteer lists (generated from C2M): Names, first names, street names, city names, country names, hospital names, mut institution names, legacy network names, month names'''
		words,temp=simpleReplaceWithCount(words,self.names,"<name>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + 1
			except:
				freqcnt[word] = 1
			freqcat[word] = "name"
		words,temp=simpleReplaceWithCount(words,self.firstnames,"<firstname>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + 1
			except:
				freqcnt[word] = 1
			freqcat[word] = "firstname"
		words,temp=simpleReplaceWithCount(words,self.streets,"<street>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + 1
			except:
				freqcnt[word] = 1
			freqcat[word] = "street"
		words,temp=simpleReplaceWithCount(words,self.cities,"<city>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + temp[word]
			except:
				freqcnt[word] = temp[word]
			freqcat[word] = "city"
		words,temp=simpleReplaceWithCount(words,self.countries,"<country>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + temp[word]
			except:
				freqcnt[word] = temp[word]
			freqcat[word] = "country"
		words,temp=simpleReplaceWithCount(words,self.hospitals,"<hospital>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + temp[word]
			except:
				freqcnt[word] = temp[word]
			freqcat[word] = "hospital"
		words,temp=simpleReplaceWithCount(words,self.mut,"<mut>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + temp[word]
			except:
				freqcnt[word] = temp[word]
			freqcat[word] = "mut"
		words,temp=simpleReplaceWithCount(words,self.networks,"<network>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + temp[word]
			except:
				freqcnt[word] = temp[word]
			freqcat[word] = "network"
		words,temp=simpleReplaceWithCount(words,months,"<month>")
		for word in temp:
			try:
				x = freqcnt[word]
				freqcnt[word] = x + temp[word]
			except:
				freqcnt[word] = temp[word]
			freqcat[word] = "month"
		
		'''2. Dates'''
		deltas=deltaCalculator(words)
		deltas.track()
		if dateTag == 1:
			newwords = deltas.tag()
		else:
			deltas.calculateTransformations()
			newwords=deltas.transform()

		'''3. Time indications'''
		text="".join(newwords)
		timeRE=re.compile(r'\d\d?:\d\d\s')
		timeList=timeRE.findall(text)
		for time in timeList:
			text=text.replace(time,"<time>")
	
		'''4. ID numbers'''
		natID=re.compile(r'\d\d\d\d\d\d\s*\d\d\d\s*\d\d')
		natIDs=natID.findall(text)
#	print "------flags for %s------ %s" %("<id>",natIDs)
		if natIDs!=[]:
			for natID in natIDs:
				text=text.replace(natID,"<id>")
		patID=re.compile(r'\d\d\d\d\d\d\d\d\d')
		patIDs=patID.findall(text)
#		print "------flags for %s------ %s" %("<id>",patIDs)
		if patIDs!=[]:
			for patID in patIDs:
				text=text.replace(patID,"<id>")

		'''5. Other types of numeric information'''
#		numberList=[word for word in words if word.isdigit()]
#		print numberList
#		for number in numberList:
#			ind=words.index(number)
#			identifyContext(ind,words)

#		with open("output.txt","a") as out:
#			out.write(str(text)+"\n")

		'''Final postprocessing to make sure no names remain'''
		text=postprocess(text,self.names,self.firstnames)
		return text,freqcnt,freqcat

def postprocess(text,names,firstnames):
	'''Locate any remaining names, possibly missed because of the absence of spaces'''
	
	''''Simple tokenization, but keeping all information'''
	words=re.split(r'(\s|<newline>|\.|<tab>|:|,|;|\?|!|-|\"|\'|\)|\(|<page>|<name>|<firstname>|<street>|<city>|<country>|<hospital>|<mut>|<network>|<month>|<time>|<id>|<horline>|<arrowright>|<italic>|<dash>|<registered>|<dotdotdot>|<euro>|<circa>|<lte>|<arrowup>|<micro>|<alpha>|<born>)',text)

	words = simpleReplace(words,names,"<name>")
	words = simpleReplace(words,firstnames,"<firstname>")
	text= "".join(words)
	return text
	
def simpleReplace(wordList,itemList,code):
	'''Locate and replace items from a list in a set of words
	these are items you can replace without conditions
	
	I assume in this basic version of the DEID that Named Entities are capitalized (names are also capitalized in the list of names and first names)
	Only does complete matches, so no partial matches
	
	FAST version using the dict.fromkeys(itemList,True) trick'''
	
	#disabled since we use a set instead
	#itemList=dict.fromkeys(itemList,True)
	
	flags=[]
	for word in wordList:
		if len(word) > 1:
			if word[0]+"".join(word[1:].lower()) in itemList:
				flags.append(word)
		else:
			if word in itemList:
				flags.append(word)
#	print "------flags for %s------ %s" %(code,flags)
	if flags != []:
		newwords=[]
		for word in wordList:
			if len(word) > 1:
				if word[0].isupper() == True:
					word2check=word[0]+"".join(word[1:].lower())
					if word2check not in itemList:
						newwords.append(word)
					elif word2check in itemList:
						#index=words.index(word)
						#print words[ index-4:index+5 ] #4L, 4R
						newwords.append(code)
				else:
					newwords.append(word)
			else:
				if word in itemList:
					#index=words.index(word)
					#print words[ index-4:index+5 ] #4L, 4R
					newwords.append(code)
				else:
					newwords.append(word)
	else:
		newwords=wordList
	return newwords
	
	
def simpleReplaceWithCount(wordList,itemList,code, log=False):
	'''Locate and replace items from a list in a set of words
	these are items you can replace without conditions
	
	I assume in this basic version of the DEID that Named Entities are capitalized (names are also capitalized in the list of names and first names)
	Only does complete matches, so no partial matches
	
	FAST version using the dict.fromkeys(itemList,True) trick'''
	freq = dict()
	
	#disabled this, as itemList already is a set
	#itemList=dict.fromkeys(itemList,True)
	
	flags=[]
	for word in wordList:
		if len(word) > 1:
			if word[0]+"".join(word[1:].lower()) in itemList:
				flags.append(word)
				if (log):
					try:
						x = freq[word]
						freq[word] = x + 1
					except:
						freq[word] = 1
		else:
			if word in itemList:
				flags.append(word)
				if (log):
					try:
						x = freq[word]
						freq[word] = x + 1
					except:
						freq[word] = 1
#	print "------flags for %s------ %s" %(code,flags)
	if flags != []:
		newwords=[]
		for word in wordList:
			if len(word) > 1:
				if word[0].isupper() == True:
					word2check=word[0]+"".join(word[1:].lower())
					if word2check not in itemList:
						newwords.append(word)
					elif word2check in itemList:
						#index=words.index(word)
						#print words[ index-4:index+5 ] #4L, 4R
						newwords.append(code)
				else:
					newwords.append(word)
			else:
				if word in itemList:
					#index=words.index(word)
					#print words[ index-4:index+5 ] #4L, 4R
					newwords.append(code)
				else:
					newwords.append(word)
	else:
		newwords=wordList
	return newwords,freq

def identifyContext(index,words):
	'''To be used as input for machine learning algorithm'''
	basket=["","","",words[index],"","",""]
	i=0
	for x in range(index-3,index+4):
		if x >= 0:
			try:
				if words[x] != '':
					basket[i]=words[x].lower()
			except:
				basket[i]=""
		i+=1
	print("===", basket)

if __name__ == "__main__":
	import sys

	'''Collect and read in all resources'''
	import DeIdColl.importDEIDresources as importDEIDresources
	
	DEIDlists = importDEIDresources.getGazetteers()

	dataPoint=sys.stdin.read()
	DEID=DeIdentifier(dataPoint, DEIDlists)
	DEIDtext=DEID.deidentifyRAW()
	print(DEIDtext)
