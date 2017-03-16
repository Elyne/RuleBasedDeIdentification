'''
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

Created on 28 may 2016
@author elyne
'''

import codecs
import re
import DeIdColl.DeIdentifier
import config
'''Collect and read in all resources'''
import DeIdColl.importDEIDresources

gazet = DeIdColl.importDEIDresources.getGazetteers()

freqcnt = dict()
freqcat = dict()

def convert_surrogates(data, errors='strict'):
	handler = None
	p = re.compile('[\ud800-\uefff]+')
	pos = 0
	res = []
	
	m = p.search(data, pos)
	if m:
		if handler is None:
			handler = codecs.lookup_error(errors)
		res.append(data[pos: m.start()])
		try:
			repl, pos = handler(UnicodeTranslateError(data, m.start(), m.end(),'lone surrogates'))
			res.append(repl)
		except:
			print("[CONVERSION ERROR] Unable to convert characters, skipping them")
			return re.sub(p,'',data)
	elif pos:
		res.append(data[pos:])
		return ''.join(res)
	else:
		return data
		
##  Procedure to call Kim's code with gazetteering
def deId(doc):
	DEID= DeIdColl.DeIdentifier.DeIdentifier(doc, gazet)
	DEIDtext = DEID.deidentifyRAW(1)[0]
	
	'''DEIDtext, tempcnt, tempcat = DEID.deidentifyRAWwithCount(1)
	
	for word in tempcnt:
		try:
			x = freqcnt[word]
			freqcnt[word] = x + tempcnt[word]
		except:
			freqcnt[word] = tempcnt[word]
			freqcat[word] = tempcat[word]'''
	return DEIDtext
	

def correctChars(doc):
	#doc = doc.encode('UTF8')
	fr = [	(u'Ã«', u'ë'),
					(u'Ã¯', u'ï')]
	for couple in fr:
		doc = doc.replace(couple[0],couple[1])
	return doc

##  Function to read in custom detection markers for certain files
def readCustomSettings(docType):
	preBin = []
	senBin = []
	endBin = []
	startBin = []
	
	##  Read in library
	mode = 0
	fi = open(config.PATH_RESOURCES + 'structure/'+ docType + 'Markers.dat','r')
	for line in fi:
		## Get mode
		line = line.replace('\n','')
		if (line == '#PREFIX'):
			mode = 1
		elif (line == '#SENTENCE'):
			mode = 2
		elif (line == '#ENDOFLINE'):
			mode = 3
		elif (line == '#STARTOFLINE'):
			mode = 4
		elif (line != ''):
			if (mode == 1):
				preBin.append(line)
			elif (mode == 2):
				senBin.append(line)
			elif (mode == 3):
				endBin.append(line)
			elif (mode == 4):
				startBin.append(line)
	return preBin, senBin, endBin, startBin

def isDate(date):
	if date.strip() != '':
		p1 = re.compile(r'(\d\d?[/-]\d\d?[/-]\d\d\d\d)(?![\d/-])')
		p2 = re.compile(r'(\d\d\d\d[/-]\d\d?[/-]\d\d?)(?![\d/\-\.])')
		p3 = re.compile(r'(\d\d?[/-]\d\d?[/-]\d\d)(?![\d/-])')
		m1 = p1.match(date)
		m2 = p2.match(date)
		m3 = p3.match(date)
		if (m1 == None) & (m2 == None) & (m3 == None):
			return False
		else:
			return True
	return False
	
## settings for types of documents
oksettings = readCustomSettings('okverslag')
briefsettings = readCustomSettings('brief')
aanvraagsettings = readCustomSettings('aanvraag')
protocolsettings = readCustomSettings('protocol')


##  Procedure to process 'okverslag'
def processOK(doc, summary):
	'''
	Process operational 
	'''
	##  Reading settings, because I can
	prefixBin, sentenceBin, endFileBin, sf = oksettings
	
	##  Splitting up the content in individual lines
	oc = doc.split('\n')				#Original Content
	nc = ''													#New Content
	
	inactive = 0
	firstLine = 1
	
	##  Going through each line individually, 'Change?'
	for i, line in enumerate(oc):
		## Filtering out first line, except when it concerns a single date
		if (firstLine == 1):
			if not (isDate(line)):
				line = '<Headid>'
		if (line != ''):
			firstLine = 0
				
		## filtering lines starting with prefixes from sentenceLine 'Yes, we can'
		for beg in sentenceBin:
			if line.upper().startswith(beg.upper()):
				line = beg + ': <heading> '
								
		## At two/thirds of a files length, start checking for endfilethings
		if (i > ((len(oc) / 3) * 2)):
			## if endOfFile is found, all following is not recorded
			for beg in endFileBin:
				if line.upper().startswith(beg.upper()):
					inactive = 1
			
		##  Adding the line to the new text (when endfile has not been found)		
		if (inactive == 0):
			nc += line + '\n'
			
	##  Reconstructing the content		
	nc = deId(correctChars(nc + '\n' +summary))
	return convert_surrogates(nc)

def processBrief(doc, summary):
	'''
	The de-identification of 'brief' starts inactively, then activates when a cue on the start of the letter starts
	(Example: Geachte heer Peeters,)
	
	It 
	'''
	##  Reading settings
	_, sentenceBin, endFileBin, startBin = briefsettings
	
	if (True):
		##  Splitting up the content in individual lines
		oc = doc.split('\n')				#Original Content
		nc = ''													#New Content
		inactive = 1
		dateLine = 0
	
		##  Going through line individually
		for i, line in enumerate(oc):
			line = line.strip()
			##  First, no record until #startofline markers are detected except when it's a date in the first line
			##  Check for 'bijlage' as well
			for beg in startBin:
				if line.upper().startswith(beg.upper()):
					inactive = 0
			if isDate(line):
				dateLine = 1
			
			##  Removing lines in sentence
			for beg in sentenceBin:
				if line.upper().startswith(beg.upper()):
					line = beg + ': <heading> '
			
			##  Checking for #endofline
			if ((inactive == 0)):
				for beg in endFileBin:
					if line.upper().startswith(beg.upper()):
						inactive = 1
						
			##  Finally, dependent on our two markers, we decide if we are going to write the line
			if ((inactive == 0) | (dateLine == 1)):
				nc += line + '\n'
				dateLine = 0
				
	##  Reconstructing the content		
	nc = deId(correctChars(nc + '\n' +str(summary)))
	return convert_surrogates(nc)
	
def processProtocol(doc,summary):
	##  Reading settings
	prefixBin, sentenceBin, endFileBin, startBin = protocolsettings
	
	if True:
		##  Splitting up the content in individual lines
		oc = doc.split('\n')				#Original Content
		nc = ''													#New Content
		inactive = 0
		dateLine = 0
		firstLineTrigger = 0
	
		##  Going through line individually
		for i, line in enumerate(oc):
			line = line.strip()
			##  When a startOfLine is found, we delete all current content
			##  Only activating this once (when firstLineTrigger first gets found
			if firstLineTrigger == 0:
				for beg in startBin:
					if line.upper().startswith(beg.upper()):
						firstLineTrigger = 1
						##  Resetting current content
						nc = ''
			if isDate(line):
				dateLine = 1
			
			##  Removing lines in sentence
			for beg in sentenceBin:
				if line.upper().startswith(beg.upper()):
					line = beg + ': <heading> '
			
			##  Checking for #endofline
			if ((inactive == 0)):
				for beg in endFileBin:
					if line.upper().startswith(beg.upper()):
						inactive = 1
						
			##  Finally, dependent on our two markers, we decide if we are going to write the line
			if ((inactive == 0) | (dateLine == 1)):
				nc += line + '\n'
				dateLine = 0
				
	##  Reconstructing the content		
	nc = deId(correctChars(nc + '\n' +summary))
	return convert_surrogates(nc)
	
def processOther(doc, summary):
	return convert_surrogates(deId(correctChars(doc + '\n' +summary)))
	
def processAanvraag(doc, summary):
	##  Reading settings
	prefixBin, sentenceBin, endFileBin, startBin = aanvraagsettings
	
	if True:
		##  Splitting up the content in individual lines
		oc = doc.split('\n')				#Original Content
		nc = ''													#New Content
		temp = ''												#stored content before patient marker, when this one is found
		patMark = 0
		inactive = 0
		dateLine = 0
		firstLineTrigger = 0
	
		##  Going through line individually
		for i, line in enumerate(oc):
			line = line.strip()
			##  When a startOfLine is found, we delete all current content
			##  Only activating this once (when firstLineTrigger first gets found
			if firstLineTrigger == 0:
				for beg in startBin:
					if line.upper().startswith(beg.upper()):
						firstLineTrigger = 1
						##  Resetting current content
						nc = ''
			if isDate(line):
				dateLine = 1
			
			##  Removing lines in sentence
			for beg in sentenceBin:
				if line.upper().startswith(beg.upper()):
					line = beg + ': <heading> '
			
			##  Checking for #endofline
			if ((inactive == 0)):
				for beg in endFileBin:
					if line.upper().startswith(beg.upper()):
						inactive = 1
						
			##  Look for pati[e-ë]nt Datum aanvraag couple, which surrounds a PHI heading
			if (line.upper().startswith("PATIENT") | line.upper().startswith(u"PATIËNT")):
				patMark = 1
				temp = nc
			
			if patMark == 1:
				if (line.upper().startswith("DATUM AANVRAAG")):
					nc = temp
					patMark = 0
			
						
			##  Finally, dependent on our two markers, we decide if we are going to write the line
			if ((inactive == 0) | (dateLine == 1)):
				nc += line + '\n'
				dateLine = 0
				
	##  Reconstructing the content		
	nc = deId(correctChars(nc + '\n' +summary))
	doc = nc
	return convert_surrogates(doc)
	
def processNota(doc, summary):
	## Doing the simple de-id thing
	return convert_surrogates(deId(correctChars(doc + '\n' +str(summary))))

##  Creating a structured ID-banner, so we can perform the reformatting algorithm
def createID(docBin):
	## pid; specialty; type; date (biomina_tmexam); description
	idBin = []
	for doc in docBin:
		row = '[ID='
		row += doc['biomina_extpid'].strip()
		row += ';SPEC=' + doc['biomina_specialty'].strip().upper()
		row += ';TYPE=' + doc['biomina_category'].strip().upper()
		row += ';DATE=' + doc['biomina_tmexam'].strip()
		row += ';DESC=' + deId(doc['biomina_description'].strip() + ']')
		idBin.append(row)
	return idBin


def getDeIDandCat(doc, conclusion, docType):
	if (docType == 'okverslag'):
		text = processOK(doc, conclusion)
		out = 'okverslag'
	elif (docType == 'brief'):
		text = processBrief(doc, conclusion)
		out = 'brief'
	elif (docType == 'protocol'):
		text = processProtocol(doc, conclusion)
		out = 'protocol'
	elif (docType == 'attest'):
		text = processProtocol(doc, conclusion)
		out = 'other'
	elif (docType == 'aanvraag'):
		text = processAanvraag(doc, conclusion)
		out = 'other'
	elif (docType == 'nota'):
		text = processNota(doc, conclusion)	
		out = 'nota'
	else:
		text = processOther(doc, conclusion)
		out = 'other'
	return text, out