import os, sys
import eyed3

#Extracts informations from filename. Filename format should be "[Artist - ]Song Title[#Album]". Content between brackets is optional
def split_filename(filename):
	
	artist = None
	album = None

	#Special character to split regular filename and the album name
	parse = filename[0:-4].split('#')
	if len(parse)>1:
		#Join album and artist name and process it as a singular artist
		#Names are processed separately when handling metadata tags
		album = parse[1]
	
	names = parse[0].split(' - ')
	if len(names)>1: 
		title = names[1]
		artist = names[0]
	else:
		title = names[0]
	
	return title, artist, album

#Add a collection of images as metadata tags to mp3 files, according to their filename
def handle_images(path_mp3, path_image, default_artist, remove):
	try:
		list = os.listdir(path_mp3)
	except:
		print("Invalid path for mp3 folder")
		sys.exit(-1)
		
	used_images = []
	
	for item in list:
		if item[-4:] != ".mp3": continue
		_, artist, album = split_filename(item)
		file = eyed3.load(path_mp3+'\\'+item)
		
		#Adjust info obtained from filename to fecth correct file
		if artist == None:
			artist = default_artist
		else:
			try: artist = artist + ' - ' + album
			except: {}
		
		#The "rb" option stands for "read, binary"
		filename = os.path.abspath(path_image)+'\\'+artist+'.png'
		try:
			image = open(filename, "rb").read()
		except:
			print("Skipped ",item,", couldn't find image file: ",filename,sep='')
			continue
		'''
		Haven't checked for compatibility with other image file formats
		The '3' option describes the kind of image metadata we're inserting. 3 is the most generic one
		Consult the eyed3 manual for more info
		'''
		if filename[-4:] == '.png':
			file.tag.images.set(3, image, 'image/png')
		elif filename[-4:] == '.jpg':
			file.tag.images.set(3, image, 'image/jpg')
		else:
			print("File format for ",filename," is not compatible. Please use either PNG or JPG",sep='')
		file.tag.save()
		
		#If the remove option is selected, all images used for metadata tags will be removed at the end of execution
		if not filename in used_images:
			used_images.append(filename)
	
	if remove:
		for file in used_images:
			os.remove(file)
		try: 
			os.rmdir(path_image)
		except:
			{}
		
#Change the metadata and filename of all given mp3 files in a directory, according to their filename 
#If you're confused about the control flags, consult the print_help function in musicbuddy.py
def handle_tags(path, default_artist, artist_flag, album_flag, rename_flag=1):
	try:
		list = os.listdir(path)
		last_dir = os.getcwd()
		os.chdir(path)
	except:
		print("Invalid path for mp3 folder")
		sys.exit(-1)
	
	for item in list:
		if item[-4:] != ".mp3": continue
		file = eyed3.load(item)
		
		title, artist, album = split_filename(item)
		
		file.tag.title = title
		
		if artist != None:
			file.tag.artist = artist
		elif artist_flag:
			file.tag.artist = default_artist
			
		if album != None:
			file.tag.album = album
		elif album_flag:
			if artist != None:
				file.tag.album = artist
			elif artist_flag:
				file.tag.album = default_artist
		
		file.tag.save()
		if rename_flag: os.rename(item, title+'.mp3')
	
	os.chdir(last_dir)

#TODO: Add an option to have certain keywords (Like 'OST') be considered albums
#Return a list of all found artist names in given path and the number of files with said name
def list(path, default_name):
	try:
		list = os.listdir(path)
	except:
		print("Invalid path for mp3 folder")
		sys.exit(-1)

	#Artist names
	artist_list = []
	#Number of songs from that artist
	artist_value = []

	for item in list:
		if item[-4:] != ".mp3": continue
		title, artist, album = split_filename(item)
		
		#Songs without an artist
		if artist == None:
			artist = default_name
		#For named artists, add the name of the album, if any
		else: 
			try: artist = artist + ' - ' + album
			except: {}
			
		#Update artists already in the list
		try:
			i = artist_list.index(artist)
			artist_value[i] += 1
		#Add new artists
		except:
			artist_list.append(artist)
			artist_value.append(1)
	
	if len(artist_list) == 0:
		print("No mp3 files found in target folder",path)
		sys.exit(0)
		
	'''
	Values returned are used explicitely to download images, so listing the directory multiple times
	is necessary to perform all five actions. This shouldn't have much of an impact on performance,
	but could be optimised at the cost of some readibility.
	'''
	return artist_list, artist_value