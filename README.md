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



