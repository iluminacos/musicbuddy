from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import sys, time
import chromedriver_autoinstaller

timeout = 3.0
max_timeout = 5

#TODO: Hide browser window and add a progress report instead
#Syntax formatting sample - '{:>30}'.format('sample text') /// print("\r"+str(n), end='')

#TODO: Hide unprompted 'usb error' selenium print

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
		
	driver = webdriver.Chrome()
	driver.get('https://images.google.com/')

	#Selenium doesn't use cookies by default, so we have to handle the popup every new session
	driver.find_element(By.XPATH, '//*[@id="L2AGLb"]/div').click()
	
	return driver

#Download image that tries to download further results if the first image takes more than timeout seconds to load
#TODO: Get this working. Current setup cannot fetch big images after checking any result other than the first one
'''
#Makes a query to google images and downloads the first image
def download_image(driver, query, path):
	
	search(driver, query)
	
	n = 1
	last_time = time.time() - timeout
	while 1:
		if n > max_timeout: 
			print("Couldn't load any image for",int(timeout*max_timeout),"seconds, check your connection then try again")
			sys.exit(-1)
		if time.time()-last_time > timeout:
			last_time=time.time()
			n += 1
			#This clicks the nth available image in the results. Every timeout seconds, if the image hasn't loaded, we try the next result
			click_target = 'div.isv-r:nth-child('+str(n)+')'
			driver.find_element(By.CSS_SELECTOR, click_target).click()
		
			#Fetch the big image after clicking the first result
			img = driver.find_element(By.CSS_SELECTOR, 'div a img.n3VNCb')
			
			#Remove image overlay to get a clear screenshot
			element = driver.find_element(By.CSS_SELECTOR, 'a.hm60ue')
			driver.execute_script("""
				var element = arguments[0];
				element.parentNode.removeChild(element);
				""", element)
			element = driver.find_element(By.CSS_SELECTOR, 'div.mWagE')
			driver.execute_script("""
				var element = arguments[0];
				element.parentNode.removeChild(element);
				""", element)
				
			#Set up an event to know when the image is done loaded
			#I don't know much javascript, so changing an attribute of the element seemed an innocuous enough method of passing information back to python
			driver.execute_script("""
				var img = arguments[0];
				img.onload = function() { img.jsname="DONEDONEHASH"; }
				""", img)
		try:
			if img.get_attribute("jsname")=="DONEDONEHASH": break
		except:
			{}
		
	#Finally, save the image. Screenshots are both convenient and provide similar filesizes
	filename = path + query + ".png"
	img.screenshot(filename)
'''

#Makes a query to google images and downloads the first image
def download_image(driver, query, path, extra=''):

	search(driver, query+extra)
	
	#Click the first result
	driver.find_element(By.CSS_SELECTOR, 'div.isv-r:nth-child(2)').click()

	#Fetch the big image that pops up on a sidebar
	img = driver.find_element(By.CSS_SELECTOR, 'div a img.n3VNCb')
	
	#Remove image overlay to get a clear screenshot
	element = driver.find_element(By.CSS_SELECTOR, 'a.hm60ue')
	driver.execute_script("""
		var element = arguments[0];
		element.parentNode.removeChild(element);
		""", element)
	element = driver.find_element(By.CSS_SELECTOR, 'div.mWagE')
	driver.execute_script("""
		var element = arguments[0];
		element.parentNode.removeChild(element);
		""", element)
	
	#Set up an event to know when the image is done loaded
	#We use one of the attributes as an innocuous way of passing information between javascript and python
	driver.execute_script("""
		var img = arguments[0];
		img.onload = function() { img.jsname="DONEDONEHASH"; }
		""", img)
	
	while img.get_attribute("jsname")!="DONEDONEHASH": {}
		
	#Finally, save the image. Screenshots are both convenient and provide consistent filesizes
	filename = path + query + ".png"
	img.screenshot(filename)

def download_batch(artist_list, path, extra):
	driver = init_setup()
	
	for artist in artist_list:
		#At this point, info is formatted like "Artist[ - Album]". Content between brackets is optional
		if len(artist.split(' - '))==1: 
			download_image(driver, artist, path, extra=extra)
		else:
			download_image(driver, artist, path)