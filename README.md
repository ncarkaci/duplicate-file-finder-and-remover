# Duplicate file finder and remover

The script search given directory with subdirectory, finds duplicate files and removes or moves them other directory. The script can search duplications for specific file type. It checks simply file type on file extension.

Firstly files are grouped as file sizes. And unique file size group members are not inclueded into comparasion process. This feature provides explicit improvement on runtime.

File comparesion is making according to hash values of the files. The approach is good for lower size files, hovewer; for big file hash calculation can process long time. Overcome to this, big file hash values are calculated with some little piece of the files. This is nahif solution but provide speed. At the sametime, to reduce false positive if we need check second hash value for files.

Algorithm : 

	Group files as size
	Eliminate unique file size from group # no need them they are already unique

	Check fast hash for files in group # Hash file little peace

	if hash same :
		check full hash # File full content hash
	else :
		skip

### Param List
* -e or --extension is File extension list e.i. "png,jpg"
* -f or --fasthash is Fast hash enabling T (True) or F (False), default is False
* -m or --move is Moving duplicate file enabling T (True) or F (False), default is False
* -r or --remove Removing duplicate file enabling T (True) or F (False), default is False
* -o or --output Output file name which include duplicate filenames, default is False
* -i or --compressed Detect compressed and rescale image file duplication


### Usage
```
python duplicateFileFinder.py -h
python duplicateFileFinder.py /home/user/directory
python duplicateFileFinder.py /home/user/directory --move -remome  --compressed -outfile
python duplicateFileFinder.py /home/user/directory --extension 'jpg,png' -fasthash --move -remomve -outfile --compressed
```


