from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import sys, time
import chromedriver_autoinstaller

timeout = 3.0
#Image results begin at the 2nd div, check google images html
first_result = 2
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

#Makes a query to google images and downloads the first image
def download_image(driver, query, path, extra=''):

	search(driver, query+extra)
		
	last_n = 0
	n = first_result
	last_time = time.time()

	while 1:
		#If an image takes too long to load, try to load another one
		if time.time()-last_time >= timeout:
			last_time=time.time()
			n += 1
		#Abort execution if it takes too long to get a viable image
		if n >= first_result + max_timeout: 
			print("Couldn't load any image for",int(timeout*max_timeout),"seconds, check your connection then try again")
			driver.close()
			sys.exit(-1)
		#Try to load a new image after the query, then every time a timeout occurs
		if n > last_n:
			last_n = n
			#This clicks the nth available image in the results. Every timeout seconds, if the image hasn't loaded, we try the next result
			click_target = 'div.isv-r:nth-child('+str(n)+')'

			driver.find_element(By.CSS_SELECTOR, click_target).click()
			#Fetch the big image after clicking the first result
			xpath = '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[3]/div/a/img'
			img = driver.find_element(By.XPATH, xpath)
			
			#Remove image overlay to get a clear screenshot
			xpath = '//*[@id="Sva75c"]/div/div/div[2]/a'
			element = driver.find_element(By.XPATH, xpath)
			driver.execute_script("""
				var element = arguments[0];
				element.parentNode.removeChild(element);
				""", element)
			xpath = '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[1]'
			element = driver.find_element(By.XPATH, xpath)
			driver.execute_script("""
				var element = arguments[0];
				element.parentNode.removeChild(element);
				""", element)
				
			#Set up an event to know when the image is done loaded
			#I don't know much javascript, so changing an attribute of the element seemed an innocuous enough method of passing information back to python
			driver.execute_script("""
				var img = arguments[0];
				if (img.complete && img.naturalHeight !== 0) {
					img.alt="KEYWORDKEYWORDKEYWORD";
				}
				else {
					img.onload = function() { img.alt="KEYWORDKEYWORDKEYWORD"; }
				}
				""", img)
		
		#We know the image is loaded if the attribute changes
		if img.get_attribute("alt") == 'KEYWORDKEYWORDKEYWORD': break
				
	filename = filename = path + query + ".png"
	img.screenshot(filename)

def download_batch(artist_list, path, extra):
	driver = init_setup()
	
	for artist in artist_list:
		#At this point, info is formatted like "Artist[ - Album]". Content between brackets is optional
		if len(artist.split(' - '))==1: 
			download_image(driver, artist, path, extra=extra)
		else:
			download_image(driver, artist, path)