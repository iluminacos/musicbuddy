import os, sys
import parsefiles
import autoimgloader

#Default values for operations
default_artist = "Misc. Artist"
path_mp3 = os.getcwd()
path_image = os.getcwd()
extra = ''

#Various logics flags
actions = [0,0,0,0]
print_flag = 0
default_artist_flag = 1
default_album_flag = 1
remove = 1
rename = 1
overwrite = 0
keyword = []

def print_help():
		print("Unless actions are specified, the script will perform all actions in sequence in the current directory.")
		print("Help:")
		print("-h, --help\t\tShow this message, then cease execution")
		print("Actions:")
		print("-l, --list\t\tList found artists and albums")
		print("-d, --download\t\tDownload images based on found artist and album names")
		print("-a, --art\t\tFix the Album Art tag")
		print("-m, --meta\t\tFix the Song Title, Artist, Album Name tags, and filename")
		print("Directories:")
		print("-i [directory]\t\tWhere to look for mp3 files")
		print("-t [directory]\t\tWhere the images will be downloaded")
		print("Options:")
		print("--overwrite\t\tDownload images for all artists without checking if there's already viable ones")
		print("--no-artist\t\tDon't give default artist names to songs without artists")
		print("--default [name]\tChange the default artist name for songs without an artist. By default, it's \"Misc. Artist\"")
		print("--no-album\t\tThe album name field will remain empty instead of being filled with the artist name by default")
		print("--extra [name]\t\tAdd text to queries with no album name to get more suitable results, e.g. \"latest album\"")
		print("-r, --no-remove\t\tDon't delete downloaded images after using them")
		print("--no-rename\t\tDon't rename files after changing their metadata")
		print("--keyword [name]\tParse filename for special phrases to add to album name, e.g. \"OST\", \"Live concert\"")
		print("\t\t\tCan be used multiple times to look for different key phrases")
		sys.exit(0)

if __name__ == '__main__':

	#Handle arguments
	n=0
	while n<len(sys.argv)-1:
		n = n+1
		arg = sys.argv[n]
		if arg=='-h' or arg=='--help': print_help()
		elif arg=='-l' or arg=='--list':
			actions[0] = 1
			print_flag = 1
		elif arg=='-d' or arg=='--download':
			actions[0] = 1
			actions[1] = 1
		elif arg=='-a' or arg=='--art':
			actions[2] = 1
		elif arg=='-m' or arg=='--meta':
			actions[3] = 1
		elif arg=='-r' or arg=='--no-remove':
			remove = 0
		elif arg=='-i':
			n=n+1
			try:
				path_mp3 = sys.argv[n]
			except:
				print("Directory not specified for -i")
		elif arg=='-t':
			n=n+1
			try:
				path_image = sys.argv[n]
			except:
				print("Directory not specified for -t")
		elif arg=='--no-artist':
			default_artist_flag = 0
		elif arg=='--overwrite':
			overwrite = 1
		elif arg=='--default':
			n=n+1
			try:
				default_artist = sys.argv[n]
			except:
				print("Name not specified for --default")
		elif arg=='--keyword':
			n=n+1
			try:
				keyword.append(sys.argv[n])
			except:
				print("Name not specified for --keyword")
		elif arg=='--no-album':
			default_album_flag = 0
		elif arg=='--extra':
			n=n+1
			try:
				#The extra whitespace is necessary to separate the regular query from the additional text
				extra = ' ' + sys.argv[n]
			except:
				print("Name not specified for --extra")
		elif arg=='--no-rename':
			rename = 0
		else:
			print("Unrecognised option:",arg)
	
	#If no specific action is chosen, all are done in sequence
	if sum(actions) == 0: 
		actions = [1,1,1,1]
		print_flag = 1
	
	#Get and list valid mp3 files
	if actions[0]:
		artist_list, artist_value = parsefiles.list(path_mp3, default_artist, key_phrase=keyword)
		if print_flag:
			for n in range(0,len(artist_list)):
				print(str(artist_list[n]) + ': ' + str(artist_value[n]))
			
	#Download images 
	if actions[1]:
		#Set up folder to download images
		if not os.path.exists(path_image):
			os.makedirs(path_image)
		#Don't download new images if there's already valid ones
		if not overwrite:
			for image in os.listdir(path_image):
				try: artist_list.remove(image[:-4])
				except: {}
		#Mixing / and \ works, at least in python windows
		if path_image[-1]!='\\': path_image += '\\'
		if len(artist_list) > 0: autoimgloader.download_batch(artist_list, path_image, extra)
		
	#Apply downloaded images as album art tags
	if actions[2]:
		parsefiles.handle_images(path_mp3, path_image, default_artist, remove, key_phrase=keyword)
		
	#Fix metadata and filename
	if actions[3]:
		parsefiles.handle_tags(path_mp3, default_artist, default_artist_flag, default_album_flag, rename_flag=rename, key_phrase=keyword)
		