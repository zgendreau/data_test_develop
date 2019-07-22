import urllib
import xml.etree.ElementTree as ElementTree
import time
import datetime
import csv

def main():
	rawData = downloadXML('http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml', "data.xml")
	elements = ['ListingDetails/DateListed', 'ListingDetails/MlsId', 'ListingDetails/MlsName', 'Location/StreetAddress', 'ListingDetails/Price']
	masterList = []
	masterList.append(parseXMLToUnixTime("data.xml", 'ListingDetails/DateListed'))
	masterList.extend(standardParseXML("data.xml", elements))
	joiningElements = ['RichDetails/Appliances,Appliance', 'RichDetails/Rooms,Room']
	masterList.extend(joiningXMLparse("data.xml", joiningElements))
	masterList.append(bathRooms("data.xml"))
	masterList.append(maxLengthXMLParse("data.xml", 'BasicDetails/Description', 200))
	masterList = orderListofLists(masterList)
	filterAndWriteCSV(masterList, "test.csv", "2016")
def downloadXML(url, file):
	'''
	input
	url the file to be downloaded
	file name of the file to be saved
	downloads file and saves it
	'''
	dataFile = urllib.URLopener()
	dataFile.retrieve(url, file)
def standardParseXML(rawData, elements):
	'''
	input 
	rawData XML file to be parsed
	elements - list of XML elements to be parse and stores the values in a list of lists
	returns a list of lists
	'''
	tree = ElementTree.parse(rawData)
	root = tree.getroot()
	masterList = []
	for element in elements:
		innerList = []
		for listing in root.findall('Listing'):
			innerList.append(listing.find(element).text)
		masterList.append(innerList)
	return masterList
def joiningXMLparse(rawData, elements):
	'''
	input
	rawData XML file to be parsed
	elements - list of XML elements to be parse and the sub element
	parses and joins the sub elements with a comma
	returns a list of lists
	'''
	tree = ElementTree.parse(rawData)
	root = tree.getroot()
	masterList = []
	for value in elements:
		element = value.split(',')[0]
		subElement = value.split(',')[1]
		innerList = []
		for listing in root.findall('Listing'):
			alist = listing.find(element)
			string = ""
			if alist == None:
				innerList.append("")
			else:
				first = True
				for a in alist.findall(subElement):
					if first:
						string = a.text
						first = False
					else:
						string = string + "," + a.text
				innerList.append(string)
		masterList.append(innerList)
	return masterList
def bathRooms(rawData):
	'''
	input rawData XML file to be parsed
	calculates the number of bathrooms in the house
	returns list of the number of bathrooms
	'''
	tree = ElementTree.parse(rawData)
	root = tree.getroot()
	masterList = []
	for listing in root.findall('Listing'):
		full = listing.find('BasicDetails/FullBathrooms').text
		if full == None:
			full = 0
		else:
			full = int(full)
		half = listing.find('BasicDetails/HalfBathrooms').text
		if half == None:
			half = 0
		else:
			half = int(half)
		threeQ = listing.find('BasicDetails/ThreeQuarterBathrooms').text
		if threeQ == None:
			threeQ = 0
		else:
			threeQ = int(threeQ)
		
		masterList.append(int(full)+int(half)*.5+int(threeQ)*.75)
	return masterList

def maxLengthXMLParse(rawData, element, maxLength):
	'''
	input
	rawData XML file to be parsed
	element the element to be parsed
	maxLength the max number of characters in the string in each element of the list
	returns a list 
	'''
	tree = ElementTree.parse(rawData)
	root = tree.getroot()
	masterList = []
	for listing in root.findall('Listing'):
		desc = listing.find(element).text[:maxLength]
		masterList.append(desc)
	return masterList
def parseXMLToUnixTime(rawData, element):
	'''
	input
	rawData XML file to be parsed
	element the element to be parsed
	value must be in y-m-d H:M:S
	returns a list of floats
	'''
	tree = ElementTree.parse(rawData)
	root = tree.getroot()
	masterList = []
	for listing in root.findall('Listing'):
		Listed = listing.find(element).text
		Listed = time.mktime(datetime.datetime.strptime(Listed, "%Y-%m-%d %H:%M:%S").timetuple())
		masterList.append(Listed)
	return masterList

def orderListofLists(masterList):
	'''
	input
	masterList list of lists
	orders all lists based on the list list in the list
	returns list of lists without the first list 
	'''
	outputList = []
	for i in range(0,len(masterList)-1):
		i+=1
		dateListed = masterList[0]
		dataList = masterList[i]
		newList = [j for _,j in sorted(zip(dateListed,dataList))]
		outputList.append(newList)
	return outputList

def filterAndWriteCSV(masterList, outputFile, year):
	'''
	input
	masterList list of lists
	outputFile csv file the lists will be writen to
	year the year of the value in the first list of lists to filter on
	Takes the inverse of the masterList an filters the year in the first value 
	Writes csv file
	'''
	masterList = zip(*masterList)
	with open(outputFile, "w") as file:
		fw = csv.writer(file,delimiter=",")
		for r in masterList:
			if r[0][:4]==year:
				fw.writerow(r)



if __name__ == '__main__':
	main()