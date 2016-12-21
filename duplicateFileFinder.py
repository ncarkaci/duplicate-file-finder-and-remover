#!/usr/bin/env python
#
# Find duplicate file and remove them.
#
# Author: Necmettin Çarkacı
# E-mail: necmettin [ . ] carkaci [ @ ] gmail [ . ] com
#
#Usage : duplicateFileFinder /home/user/binaryDir


'''
	@ url :http://stackoverflow.com/questions/6507272/algorithm-to-find-duplicates
	Algorithm :

	Group files as size
	Eliminate unique file size from group # no need them they are already unique

	Check fast hash for files in group # Hash file little peace

	if hash same :
		check full hash # File full content hash
	else :
		skip
'''

import os, sys, time, random
import collections # for sort dictionary
import hashlib

# Collect all files form given directory and return their paths list
# param directory : <string> directory name
# param extension : <string> file extension, using for file type filter
# return <list> paths of files

def getFilePaths(directory, extension=''):

	file_paths = []

	for root, directories, files in os.walk(directory):
		for filename in files:
			if (extension != '') :
				if (filename.endswith(extension)):			
					filepath = os.path.join(root, filename)
					file_paths.append(filepath) 
					#print (filepath)
			else :				
					filepath = os.path.join(root, filename)
					file_paths.append(filepath) 
					#print (filepath)

	print ("Number of file found : "+ str(len(file_paths)))
	return file_paths



def groupFilesAsSize(listOfFile):
	
	fileGroupDict = {} # <key><value> --> <size> [list of file names]

	for filename in listOfFile:
		size = os.path.getsize(filename)
		
		if size in fileGroupDict.keys(): # or if fileGroupDict.get(size, []):
			fileGroupDict[size].append(filename)
		else :
			fileGroupDict[size] = [] # create list for value of key
			fileGroupDict[size].append(filename)
	
	#print (fileGroupDict)
	print ("Number of group : "+ str(len(fileGroupDict)))	
	return 	fileGroupDict

def filterUniqueFileSizes(fileGroupDict):

	uniqueFileSizeDict = {}

	for size in fileGroupDict:
		listOfFile = fileGroupDict[size]
		if (len(listOfFile) > 1):
			uniqueFileSizeDict[size] = listOfFile

	#print (uniqueFileSizeDict)
	print ("Number of group after filtering : "+ str(len(uniqueFileSizeDict)))
	return uniqueFileSizeDict


def calculateHashValueForFiles(uniqueFileSizeDict, fastHash=True):
	
	hashMapFileList = {} # <int><list> --> hash value, filename list
	
	for size in uniqueFileSizeDict:
		#print ("\n	Size : "+str(size)+" Kb")		
		
		listOfFile = uniqueFileSizeDict[size] 
		
		for filename in listOfFile:

			hashValue = hashFile(filename, fastHash)
						
			if hashValue in hashMapFileList.keys():
				hashMapFileList[hashValue].append(filename)
			else :
				hashMapFileList[hashValue] = []
				hashMapFileList[hashValue].append(filename)
	print ("Number of hash values : "+ str(len(hashMapFileList)))	
	return hashMapFileList


def hashFile(filename, fastHash, buf=(1024*1024)):

	hasher = hashlib.md5()
	with open(filename, 'rb') as file:
		
		if (fastHash) :
		    chunk = file.read(buf)
		    while len(chunk) > 0:
		        hasher.update(chunk)
		        chunk = file.read(buf)
		else :
			content = file.read()
			hasher.update(content)

	#print(hasher.hexdigest())
	
	return hasher.hexdigest()


def findDuplicateFiles(hashMapFileList, writeFile=True):
	
	duplicateFileDict = {}

	for hashValue in hashMapFileList:
		listOfFile = hashMapFileList[hashValue]
		if (len(listOfFile) > 1):
			duplicateFileDict[hashValue] = listOfFile

	#print (duplicateFileDict)
	print ("Number of duplicate hash values : "+ str(len(duplicateFileDict)))	

	if (writeFile):
		with open('duplicateFileList.txt','w') as outputFile:
			for hashValue in duplicateFileDict:
				listOfFile = duplicateFileDict[hashValue]
				for filename in listOfFile:
					outputFile.write(hashValue+'\t'+filename+'\n')
				outputFile.write('\n')
	print ('Duplicate files written into duplicateFileList.txt file.')
	return duplicateFileDict

def removeDuplicateFiles(duplicateFileDict, removable=False):
	
	removedFileNumber = 0

	for hashValue in duplicateFileDict:
		listOfFile = duplicateFileDict[hashValue]
		for filename in listOfFile:
			if listOfFile.index(filename) == 1: # don't remove first file keep them as original file
				print ("Don't remoed : "+filename+" keept as original.")
			else :
				if removable :
					os.remove(filename)
					removedFileNumber = removedFileNumber+1
					print ("Removed file : "+filename)
				else :
					path, name 	= os.path.split(filename)
					filenamePrefix = str(random.randrange(1,99999999))
					destinationFilename = os.getcwd()+os.sep+'duplicated_files'+os.sep+filenamePrefix+"_"
					os.rename(filename,destinationFilename+name)

	print ("Number of removed files : "+ str(removedFileNumber))	
	
def run(directory, extension='', fastHash=False, writeOutputIntoFile=True, removeDuplicates=False):
	
	start = time.time()
	print("Start time : "+str(time.clock()))

	listOfFile			=	getFilePaths(directory, extension)
	print ('Files collected. The files are grouping as size ... ')	

	fileGroupDict		=	groupFilesAsSize(listOfFile)
	print ('Files are grouped as size. Filtering unique file sizes ...')

	uniqueFileSizeDict	=	filterUniqueFileSizes(fileGroupDict)
	print ('Filtering complted. Calculating hash values ... ...')

	hashMapFileList		=	calculateHashValueForFiles(uniqueFileSizeDict, fastHash)
	print ('Hash values calculated. Finding duplicate files ...')	

	duplicateFileDict	=	findDuplicateFiles(hashMapFileList, writeOutputIntoFile)
	print ('Duplicate file found. Removing duplicate files ...')	

	removeDuplicateFiles(duplicateFileDict, removeDuplicates)
	print ('All duplicate files removed.')

	end = time.time()
	print ('End time : '+str(time.clock()))
	print('Running time : '+str(end - start))
		
if __name__ == '__main__':
	
	directory = sys.argv[1]
	run(directory)

