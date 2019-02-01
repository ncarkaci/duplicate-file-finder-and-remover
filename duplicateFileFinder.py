#!/usr/bin/env python
import collections # for sort dictionary
import hashlib     # Default python hash operation library
import os, shutil, sys, time, random, argparse
import logging
import six
import imagehash
from PIL import Image

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


# Define logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_file_paths (directory, extensions=None):
	"""
	Collect all files as an extension from given directory and return their paths list
	:param directory: <string> directory name
	:param extensions: <string> file extension, using for file type filter. Default value is []
	:return: <list> paths of files
	"""

	file_path_list = []
	for root, directories, files in os.walk(directory):
		for filename in files:
			if extensions != "":

				if filename.split(".")[-1] in extensions:
					file_path = os.path.join(root, filename)
					file_path_list.append(file_path)
					logger.debug('File path : ', file_path)

			else:  # Collect all files under directory
					file_path = os.path.join(root, filename)
					file_path_list.append(file_path)

					logger.debug('File path : ', file_path)

	logger.info("Number of file found : "+str(len(file_path_list)))

	return file_path_list


def group_files_as_size(file_names):
	"""
	Get list of files and return a dictionary group as file size.
	:param file_names: <list> list of file path
	:return: <dict> (<key><value>) : key : size, value : filename
	"""

	file_group = {}  # <key><value> --> <size> [list of file names]

	for filename in file_names:
		size = os.path.getsize(filename)

		if size in file_group.keys():
			file_group[size].append(filename)
		else:
			# create list for value of key
			file_group[size] = []
			file_group[size].append(filename)

	logger.debug('File Group : ', file_group)
	logger.info("Number of group : "+str(len(file_group)))

	return file_group


def filter_unique_file_sizes(file_group):
	"""
	Get file group dictionary return non-unique groups in dictionary
	Non-unique group in dictionary means it key has multiple value

	:param file_group: <dict> (<key><value>) file group
	:return: <dict> (<key><value>) : non-unique groups in dictionary
	"""

	uniqueFileSizeDict = {}

	for size in file_group:
		listOfFile = file_group[size]
		if len(listOfFile) > 1:
			uniqueFileSizeDict[size] = listOfFile

	logger.debug('Unique file size dict : ', uniqueFileSizeDict)
	logger.info("Number of group after filtering : "+str(len(uniqueFileSizeDict)))

	return uniqueFileSizeDict


def calculateHashValueForFiles(uniqueFileSizeDict, fastHash=True):
	"""
	Calculate hash values for file in list of files

	:param uniqueFileSizeDict: <dict> (<key><value>) file group
	:param fastHash: <boolean> fast hash is enabled
	:return: <dict> (<key><value>) : key : filename, value : hash value
	"""

	hashMapFileList = {}  # <int><list> --> hash value, filename list

	for size in uniqueFileSizeDict:

		logger.debug('\n File size ', str(size), " Kb")


		listOfFile = uniqueFileSizeDict[size]

		for filename in listOfFile:

			hashValue = hashFile(filename, fastHash)

			if hashValue in hashMapFileList.keys():
				hashMapFileList[hashValue].append(filename)
			else :
				hashMapFileList[hashValue] = []
				hashMapFileList[hashValue].append(filename)

	logger.info("Number of hash values : "+str(len(hashMapFileList)))

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
		else:
			content = file.read()
			hasher.update(content)

	return hasher.hexdigest()


def findDuplicateFiles(hashMapFileList, writeFile=True):

	duplicateFileDict = {}

	for hashValue in hashMapFileList:
		listOfFile = hashMapFileList[hashValue]
		if len(listOfFile) > 1:
			duplicateFileDict[hashValue] = listOfFile

	logger.debug('Duplicate file dict : ', duplicateFileDict)
	logger.info("Number of duplicate hash values : "+str(len(duplicateFileDict)))

	if writeFile:
		with open('duplicateFileList.txt', 'w') as outputFile:
			for hashValue in duplicateFileDict:
				listOfFile = duplicateFileDict[hashValue]
				for filename in listOfFile:
					outputFile.write(hashValue+'\t'+filename+'\n')
				outputFile.write('\n')
	logger.info('Duplicate files written into duplicateFileList.txt file.')

	return duplicateFileDict

def remove_duplicate_files(duplicateFileDict, moveDuplicates=True, removeDuplicates=True, isImageFile=False):
	"""
	Move and remove given file list.
	:param duplicateFileDict: <dict> (<key><value>) : key : hash value, value : duplicate file list
	:param moveDuplicates: Move duplicate files, default True
	:param removeDuplicates: Remove duplicate files, default True
	:param isImageFile: Files are images or not. If files are images, keep and don't remove biggest of the list
	:return: void
	"""

	removedFileNumber = 0
	movedFileNumber   = 0

	for hashValue in duplicateFileDict:
		listOfFile = duplicateFileDict[hashValue]
		for filename in listOfFile[1:]:

			main_file = listOfFile[0]

			if isImageFile:
				for image_file in listOfFile[1:]:
					if os.path.getsize(image_file) > os.path.getsize(main_file):
						main_file = image_file

			listOfFile.remove(main_file)

			if moveDuplicates:
				path, name = os.path.split(filename)
				filenamePrefix 	= str(random.randrange(1, 99999999))

				if isImageFile:
					destinationDir 	= os.getcwd()+os.sep+'duplicate_images'
				else:
					destinationDir = os.getcwd() + os.sep + 'duplicate_files'
				if not os.path.exists(destinationDir):
					os.makedirs(destinationDir)

				destinationFilename = destinationDir+os.sep+filenamePrefix+"_"+name
				sourceFilename      = filename
				shutil.copy(sourceFilename, destinationFilename)
				movedFileNumber = movedFileNumber+1
				logger.debug("Moved file : "+filename+" --> "+destinationFilename)

			if removeDuplicates:
				os.remove(filename)
				removedFileNumber = removedFileNumber+1
				logger.debug("Removed file : "+filename)

	logger.info("Number of removed files : "+str(removedFileNumber))
	logger.info("Number of moved   files : "+str(movedFileNumber))


def find_similar_images(file_list, hash_function=imagehash.average_hash, writeFile=True):
	"""
	Find duplicate images which can be resize or compressed, return list of th duplicate files
	:param file_list: File path list
	:param hash_function: The hash function which used for calculate hash of the files
	:param writeOutputIntoFile: Duplicate file names write into file, default True
	:return: <dict> (<key><value>) : key : hash value, value : duplicate file list
	"""

	# Filter image files
	image_extensions = ['png', 'jpg', 'jpeg', 'bmp', 'gif']
	image_filenames = [filename for filename in file_list if filename.lower().split('.')[-1] in image_extensions]

	images = {}
	for img in sorted(image_filenames):
		try:
			image_hash = hash_function(Image.open(img))
			images[image_hash] = images.get(image_hash, []) + [img]
			logger.debug('Filename :', img, ' image_hash value : ', image_hash)
		except Exception as e:
			logger.error('Problem:', e, 'with', img)
			pass

	duplicate_images = {}
	for image_hash, image_file_list in six.iteritems(images):

		# Filter duplicate images
		if len(image_file_list) > 1:
			duplicate_images[image_hash] = image_file_list

	if writeFile:
		with open('duplicateImageList.txt', 'w') as outputFile:
			for hashValue in duplicate_images:
				file_list = duplicate_images[hashValue]
				for filename in file_list:
					outputFile.write(str(hashValue)+'\t'+filename+'\n')
				outputFile.write('\n')
	logger.info('Duplicate images written into duplicateImageList.txt file.')

	return duplicate_images

def run(directory, extension='', fastHash=False, moveDuplicates=True, removeDuplicates=True, writeOutputIntoFile=True, isImageFile=True ):

	start = time.time()
	logger.info("Start time : "+str(time.ctime(start)))

	file_names			= get_file_paths(directory, extension)
	logger.info('Files collected. The files are grouping as size ... ')

	fileGroupDict		= group_files_as_size(file_names)
	logger.info('Files are grouped as size. Filtering unique file sizes ...')

	uniqueFileSizeDict	= filter_unique_file_sizes(fileGroupDict)
	logger.info('Filtering completed. Calculating hash values ...')

	hashMapFileList		= calculateHashValueForFiles(uniqueFileSizeDict, fastHash)
	logger.info('Hash values calculated. Finding duplicate files ...')

	duplicateFileDict	= findDuplicateFiles(hashMapFileList, writeOutputIntoFile)
	logger.info('Duplicate file found. Removing duplicate files ...')

	remove_duplicate_files(duplicateFileDict, moveDuplicates, removeDuplicates)
	logger.info('All duplicate files removed.')

	file_names = get_file_paths(directory, extension)
	logger.info('Files collected. Duplicate images finding ... ')

	duplicate_images = find_similar_images(file_names)
	logger.info('Duplicate images found. Removing duplicate files ...')

	remove_duplicate_files(duplicate_images, moveDuplicates, removeDuplicates, isImageFile=True)
	logger.info('All duplicate images removed.')

	end = time.time()
	logger.info('End time : '+str(time.ctime(end)))
	logger.info('Running time : '+str(end - start)+' milisecond')

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Finds duplicate files in directory and removes or moves them other directory.")
	parser.add_argument('directory',									help="Search directory name")
	parser.add_argument("-e", "--extensions",	default="",				help="Proceed file extension list")
	parser.add_argument("-f", "--fasthash",   	action='store_true',	help="Fast hash enabling T (True) or F (False)")
	parser.add_argument("-m", "--move",			action='store_true',	help="Moving duplicate file enabling T (True) or F (False)")
	parser.add_argument("-r", "--remove", 		action='store_true',	help="Removing duplicate file enabling T (True) or F (False)")
	parser.add_argument("-o", "--outfile",  	action='store_true',	help="Output file name which include duplicate file names")
	parser.add_argument("-i", "--compressed", 	action='store_true',	help="Check duplication resized and compressed images")

	args = parser.parse_args()

	logger.info('Params : '+str(args))

	if args.extensions != "":
		args.extensions = args.extensions.split(",")

	if args.directory:
		run(args.directory,
			extension=args.extensions,
			fastHash=args.fasthash,
			moveDuplicates=args.move,
			removeDuplicates=args.remove,
			writeOutputIntoFile=args.outfile,
			isImageFile=args.compressed)
	else:
		parser.print_help()
		sys.exit(1)



