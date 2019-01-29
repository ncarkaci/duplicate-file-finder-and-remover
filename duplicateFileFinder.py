#!/usr/bin/env python
import collections # for sort dictionary
import hashlib     # Default python hash operation library
import os, shutil, sys, time, random, argparse

'''
Find duplicate file and remove them.

Author: Necmettin Çarkacı
E-mail: necmettin [ . ] carkaci [ @ ] gmail [ . ] com

Usage : python duplicateFileFinder.py -h
Usage : python duplicateFileFinder.py /home/user/binaryDir
Usage : python duplicateFileFinder.py /home/user/binaryDir -e '.ext' -f True -m True -r False -o True


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


def getFilePaths(directory, extension=''):
	"""
	Collect all files from given directory and return their paths list
	You filter file list as file extension
	:param directory: <string> directory name
	:param extension: <string> file extension, using for file type filter. Default value is []
	:return: <list> paths of files
	"""

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
	"""
	Get list of files and return a dictionary group as file size.
	:param listOfFile: <list> list of file path
	:return: <dict> (<key><value>) : key : size, value : filename
	"""
	
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
	"""
	Get file group dictionary return non-unique groups in dictionary
	Non-unique group in dictionary means it key has multiple value

	:param fileGroupDict: <dict> (<key><value>) file group
	:return: <dict> (<key><value>) : non-unique groups in dictionary
	"""

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
	"""
	Calculate md5 hash value for given file and return the value
	if fast hash enabled, it calculate fast hashing.
	Fast hashing meaning it get specific part of the file header and calculate hash for this part.
	Fast hashing part size can give as parameter and it should enabled for big file hashing process.
	:param filename: <string> file path. Default value is False
	:param fastHash: <boolean> Specific part of the file header hashing.
	:param buf: <integer> Fast hashing size. Default value is 1024*1024 = 1 megabyte
	:return: <string> hash value of file
	"""

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

def removeDuplicateFiles(duplicateFileDict, move=True, removable=True):
	
	removedFileNumber = 0

	for hashValue in duplicateFileDict:
		listOfFile = duplicateFileDict[hashValue]
		for filename in listOfFile:
			if listOfFile.index(filename) == 1: # don't remove first file keep them as original file
				# print ("Don't removed : "+filename+" keept as original.")
				pass
			else :
				if move :
					path, name 	= os.path.split(filename)
					filenamePrefix 	= str(random.randrange(1,99999999))
					destinationDir 	= os.getcwd()+os.sep+'duplicated_files'

					if not os.path.exists(destinationDir):
						os.makedirs(destinationDir)

					destinationFilename = destinationDir+os.sep+filenamePrefix+"_"+name
					sourceFilename      = filename
					shutil.copy(sourceFilename,destinationFilename)
					removedFileNumber = removedFileNumber+1
					print ("Moved file : "+filename+" --> "+destinationFilename)

				if removable :
					os.remove(filename)
					removedFileNumber = removedFileNumber+1
					print ("Removed file : "+filename)


	print ("Number of removed or moved files : "+ str(removedFileNumber))	
	
def run(directory, extension='', fastHash=False, moveDuplicates=True, removeDuplicates=True, writeOutputIntoFile=True ):
	
	start = time.time()
	print("Start time : "+str(time.ctime(start)))

	listOfFile			=	getFilePaths(directory, extension)
	print ('Files collected. The files are grouping as size ... ')	

	fileGroupDict		=	groupFilesAsSize(listOfFile)
	print ('Files are grouped as size. Filtering unique file sizes ...')

	uniqueFileSizeDict	=	filterUniqueFileSizes(fileGroupDict)
	print ('Filtering completed. Calculating hash values ... ...')

	hashMapFileList		=	calculateHashValueForFiles(uniqueFileSizeDict, fastHash)
	print ('Hash values calculated. Finding duplicate files ...')	

	duplicateFileDict	=	findDuplicateFiles(hashMapFileList, writeOutputIntoFile)
	print ('Duplicate file found. Removing duplicate files ...')	

	removeDuplicateFiles(duplicateFileDict, moveDuplicates, removeDuplicates)
	print ('All duplicate files removed.')

	end = time.time()
	print ('End time : '+str(time.ctime(end)))
	print('Running time : '+str(end - start)+' milisecond')
		
if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description="Finds duplicate files in directory and removes or moves them other directory.")
	parser.add_argument('directory',							help="Search directory name")
	parser.add_argument("-e", "--extension", default = '',		help="File extension")
	parser.add_argument("-f", "--fasthash",  default = False,	help="Fast hash enabling T (True) or F (False)")
	parser.add_argument("-m", "--move",		 default = True,	help="Moving duplicate file enabling T (True) or F (False)")
	parser.add_argument("-r", "--remove", 	 default = True,	help="Removing duplicate file enabling T (True) or F (False)")
	parser.add_argument("-o", "--output",	 default = True,	help="Output file name which include duplicate filenames")

	args = parser.parse_args()

	if args.directory :
		run(args.directory, extension=args.extension, fastHash=args.fasthash, 
			moveDuplicates=args.move, removeDuplicates=args.remove, writeOutputIntoFile=args.output )
	else :
		parser.print_help()
		sys.exit(1)



