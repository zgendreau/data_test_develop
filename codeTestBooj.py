import urllib
import xml.etree.ElementTree as ElementTree
import time
import datetime
import csv

def main():
	rawData = downloadXML('http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml')
	elements = ['ListingDetails/DateListed', 'ListingDetails/MlsId', 'ListingDetails/MlsName', 'Location/StreetAddress', 'ListingDetails/Price']
	masterList = []
	masterList.append(parseXMLToUnixTime("data.xml", 'ListingDetails/DateListed'))
	masterList.extend(standardParseXML("data.xml", elements))
	joiningElements = ['RichDetails/Appliances,Appliance', 'RichDetails/Rooms,Room']
	masterList.extend(joiningXMLparse("data.xml", joiningElements))
	masterList.append(bathRooms("data.xml"))
	masterList.append(maxLengthXMLParse("data.xml", 'BasicDetails/Description', 200))
	masterList = orderListofLists(masterList)
	filterAndWriteCSV(masterList, "test.csv")
def downloadXML(url):
	dataFile = urllib.URLopener()
	dataFile.retrieve(url, "data.xml")
def standardParseXML(rawData, elements):
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
	tree = ElementTree.parse(rawData)
	root = tree.getroot()
	masterList = []
	for listing in root.findall('Listing'):
		desc = listing.find(element).text[:maxLength]
		masterList.append(desc)
	return masterList
def parseXMLToUnixTime(rawData, element):
	tree = ElementTree.parse(rawData)
	root = tree.getroot()
	masterList = []
	for listing in root.findall('Listing'):
		Listed = listing.find(element).text
		Listed = time.mktime(datetime.datetime.strptime(Listed, "%Y-%m-%d %H:%M:%S").timetuple())
		masterList.append(Listed)
	return masterList

def orderListofLists(masterList):
	outputList = []
	for i in range(0,len(masterList)-1):
		i+=1
		dateListed = masterList[0]
		dataList = masterList[i]
		newList = [j for _,j in sorted(zip(dateListed,dataList))]
		outputList.append(newList)
	return outputList

def filterAndWriteCSV(masterList, outputFile):
	masterList = zip(*masterList)
	with open(outputFile, "w") as file:
		fw = csv.writer(file,delimiter=",")
		for r in masterList:
			if r[0][:4]=="2016":
				fw.writerow(r)



if __name__ == '__main__':
	main()