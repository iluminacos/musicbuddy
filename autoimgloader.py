from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import sys, urllib
import chromedriver_autoinstaller

#TODO: Test google images API vs selenium scrape

max_attempts = 5

#When in google images, makes a new image query
def search(driver, query):
	#Click search bar
	box = driver.find_element(By.NAME, 'q')
	#Delete all text currently in search bar
	box.send_keys(Keys.CONTROL, 'a')
	box.send_keys(Keys.BACKSPACE)
	#Type and search
	box.send_keys(query)
	box.send_keys(Keys.ENTER)

#Begins selenium browser session. 
def init_setup():
	#Not much experience with selenium, this seems necessary
	chromedriver_autoinstaller.install()
		
	options = webdriver.chrome.options.Options()
	#This hides the browser
	options.headless = True
	#This hides selenium's console output, except for fatal errors
	options.add_argument("--log-level=3")
	driver = webdriver.Chrome(options=options)
	driver.get('https://images.google.com/')

	#Selenium doesn't use cookies by default, so we have to handle the popup every new session
	driver.find_element(By.XPATH, '//*[@id="L2AGLb"]/div').click()
	
	return driver

#Makes a query to google images and downloads the first image
def download_image(driver, query, path, extra=''):

	search(driver, query+extra)
	
	#Results begin at the second div
	n=2
	while n<2+max_attempts:
		#This clicks the nth available image in the results. Every timeout seconds, if the image hasn't loaded, we try the next result
		click_target = 'div.isv-r:nth-child('+str(n)+')'

		driver.find_element(By.CSS_SELECTOR, click_target).click()
		#Fetch the big image after clicking the first result
		xpath = '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[3]/div/a/img'
		img = driver.find_element(By.XPATH, xpath)
		
		src = img.get_attribute('src')

		#Loaded images should have a proper url, all preloaded image sources begin with "data:image/"
		while src[0:11] == 'data:image/':
			src = img.get_attribute('src')
		
		#To handle protocol errors
		try:
			#Download the image
			filename = filename = path + query + ".png"
			urllib.request.urlretrieve(src, filename)
			return 0;
		except: n+=1
	print('Skipping','"'+query+extra+'": Couldn\'t download any image in',n,'attempts')
		
def download_batch(artist_list, path, extra):
	driver = init_setup()
	
	#Data for the print
	length = len(artist_list)
	n = 0
	last_len = 0
	filler = 0
	
	for artist in artist_list:
	
		#Status update message
		n+=1
		message = "Image "+str(n)+'/'+str(length)+' - '+artist
		filler = max(last_len - len(message), 0)
		print(message, ' '*filler, end='\r', sep='', flush=True)
		last_len = len(message)
	
		#At this point, info is formatted like "Artist[ - Album]". Content between brackets is optional
		if len(artist.split(' - '))==1: 
			download_image(driver, artist, path, extra=extra)
		else:
			download_image(driver, artist, path)