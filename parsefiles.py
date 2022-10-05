import os, sys
import eyed3

#Extracts informations from filename. Filename format should be "[Artist - ]Song Title[#Album]". Content between brackets is optional
def split_filename(filename, keywords):
	
	artist = None
	album = None
	add_key = []
	
	#Check for special keywords to then be added to the album name
	for key in keywords:
		filename = filename.split(key)
		if len(filename)>1:
			add_key.append(key)
			filename = ''.join(filename)
		else:
			#Split returns a one item list, we want to fetch the string within
			filename = filename[0]
	
	add_key = ' '.join(add_key)
	
	#Special character to split regular filename and the album name
	#The [0:-4] is to ignore ".mp3" . Would need an adjustment if support for other file formats is added
	parse = filename[0:-4].split('#')
	if len(parse)>1:
		album = parse[1].strip() + ' ' + add_key
	#If there's no album BUT there are keywords, keywords are used as the entire album name
	elif add_key != '': album = add_key
	
	#Special character to split artist and song name
	names = parse[0].split(' - ')
	if len(names)>1: 
		title = names[1]
		artist = names[0]
	else:
		title = names[0]
	
	#Remove front and back whitespaces
	if title!=None: title = title.strip()
	if artist!=None: artist = artist.strip()
	if album!=None: album = album.strip()
	
	return title, artist, album
		
#Define the specific combination of artist, album name, and keywords to look up images
def gen_artist(artist, album, default_artist):
	
	#Songs without an artist. A name is necessary to fetch images
	if artist == None:
		artist = default_artist
	#For named artists, add the name of the album, if any
	else: 
		try: artist = artist + ' - ' + album
		except: {}
		
	return artist

#Add a collection of images as metadata tags to mp3 files, according to their filename
def handle_images(path_mp3, path_image, default_artist, remove, key_phrase = None):
	try:
		list = os.listdir(path_mp3)
	except:
		print("Invalid path for mp3 folder")
		sys.exit(-1)
		
	used_images = []
	
	for item in list:
		if item[-4:] != ".mp3": continue
		_, artist, album = split_filename(item, key_phrase)
		file = eyed3.load(path_mp3+'\\'+item)
		
		#Adjust info obtained from filename to fecth correct file
		artist = gen_artist(artist, album, default_artist)
		
		#The "rb" option stands for "read, binary"
		#eyed3 should be compatible with other image formats 
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
def handle_tags(path, default_artist, artist_flag, album_flag, rename_flag=1, key_phrase=None):
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
		
		title, artist, album = split_filename(item, key_phrase)
		
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

#Return a list of all found artist names in given path and the number of files with said name
def list(path, default_artist, key_phrase=None):
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
		title, artist, album = split_filename(item, key_phrase)
		
		#Adjust info obtained from filename to look up relevant information
		artist = gen_artist(artist, album, default_artist)
						
		#Selenium behaves oddly when trying to save files with the same name but different capitalisation
		#Since capitalisation shouldn't affect search quality, we make all searches lowercase to avoid unnecessary searches
		artist = artist.lower()
			
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
