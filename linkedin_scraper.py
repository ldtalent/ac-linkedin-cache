from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import glob
import csv

from education import get_education
from experience import single_role, multi_role
from auto_scroll import auto_scroll

def initial_setup():
  # PATH = "./chromedriver" 
  options = webdriver.ChromeOptions()
  options.add_argument("--start-maximized")

  URL = "https://www.linkedin.com/mynetwork/invite-connect/connections/"
  # driver = webdriver.Chrome(PATH, chrome_options=options) # anisha version
  driver = webdriver.Chrome(chrome_options=options) # gobi version
  driver.get(URL)
  time.sleep(80) # 80

  auto_scroll(driver)

  # To get profile url of all the connections  
  connections = driver.find_elements_by_class_name('mn-connection-card')
  connection_urls = [ url.find_element_by_tag_name('a').get_attribute('href') for url in connections ]

  scraper(driver, connection_urls)

def scraper(driver, connection_urls):
  # To check if there is csv file and select the mode to write or append csv accordingly
  csv_files = list(glob.glob("*.csv"))
  if ('linkedin_cache.csv' in csv_files):
    mode = 'a'
  else:
    mode = 'w'

  # with open('linkedin_cache.csv', mode , encoding='UTF-16', newline='') as csvfile: # anisha version
  with open('linkedin_cache.csv', mode, newline='') as csvfile: # gobi version
    writer = csv.writer(csvfile)
    if mode == 'w':
      writer.writerow(['name', 'title', 'email', 'profile_link', 'website', 'phone', 'address', 'birthday', 'about', 'location', 'experiences', 'education'])

    # To count number of contacts to scrape on a single run
    count = 0

    # Scraping
    for url in connection_urls:
      driver.get(url)
      time.sleep(5)
      content = driver.find_element_by_tag_name('main')
      result = content.get_attribute('innerHTML')
      soup = BeautifulSoup(result, 'html.parser')

      # Initialization
      email = website = phone = address = birthday = about = 'Not mentioned'
      experiences = []
      education = []

      # To click contact info link and open modal
      driver.find_element_by_css_selector("a[data-control-name='contact_see_more']").click()
      time.sleep(5)

      # Extract all information from contact info modal
      modal = driver.find_element_by_id('artdeco-modal-outlet')
      profile_link = modal.find_element_by_class_name('ci-vanity-url').find_element_by_tag_name('a').text
      
      try:
        email = modal.find_element_by_class_name('ci-email').find_element_by_tag_name('a').text
      except:
        pass

      try:
        websites = modal.find_element_by_class_name('ci-websites').find_elements_by_tag_name('a')
        website = [ site.text for site in websites ]
      except:
        pass
      
      try:
        phone_nums = modal.find_element_class_name('ci-phone').find_elements_by_tag_name('li')
        phone = [ num.text for num in phone_nums ]
      except:
        pass

      try:
        address = modal.find_element_by_class_name('ci-address').find_element_by_tag_name('a')
      except:
        pass

      try:
        birthday = modal.find_element_by_class_name('ci-birthday').find_element_by_class_name('pv-contact-info__ci-container').text
      except:
        pass  
      
      # To close contact info modal
      modal.find_element_by_tag_name('button').click()
      
      time.sleep(5)

      # Extracting user basic information
      name     = soup.find("li", class_ = 'inline t-24 t-black t-normal break-words').text.strip()
      title    = soup.find("h2", class_ = 'mt1 t-18 t-black t-normal break-words').text.strip()
      location = soup.find("li", class_ = 't-16 t-black t-normal inline-block').text.strip()

      # To click the see more link in about section
      try:
        driver.find_element_by_class_name('lt-line-clamp__more').click()
        time.sleep(2)
        about = driver.find_element_by_class_name('lt-line-clamp__raw-line').text.strip()
      except:
        try:
          about = soup.find("span", class_ = 'lt-line-clamp__line lt-line-clamp__line--last').text.strip()  
        except:
          pass
      
      # To click all the show more records button in the page
      try:
        see_more_list = driver.find_elements_by_class_name('pv-profile-section__see-more-inline')
        for more in see_more_list:
          more.click()
      except:
        pass

      time.sleep(3)

      # Extracting experiences 
      experience_section = driver.find_element_by_class_name('experience-section')
      experience_section = BeautifulSoup(experience_section.get_attribute('innerHTML'), 'html.parser')
      experience_list    = experience_section.find_all("li", class_ = 'pv-entity__position-group-pager pv-profile-section__list-item ember-view')
      for experience in experience_list:
        try:
          data = single_role(experience)
        except:
          data = multi_role(experience)
        experiences.append(data)
      experiences = '\n\n'.join(experiences)

      # Extracting education
      education_section = driver.find_element_by_class_name('education-section')
      education_section = BeautifulSoup(education_section.get_attribute('innerHTML'), 'html.parser')
      education_list    = education_section.find_all("li", class_ = 'pv-profile-section__list-item pv-education-entity pv-profile-section__card-item ember-view')
      for item in education_list:
        data = get_education(item)
        education.append(data)
      education = '\n\n'.join(education)
      
      # To check duplicate entry and skip the contact if duplicate else save it to csv
      if (mode == 'w'):
        writer.writerow([name, title, email, profile_link, website, phone, address, birthday, about, location, experiences, education])
        print('New contact entry: ', name)
        count += 1
      else:
        # df = pd.read_csv('linkedin_cache.csv', encoding = 'UTF-16') # anisha version
        df = pd.read_csv('linkedin_cache.csv') # gobi version
        if ( ((df['name'] == name) & (df['profile_link'] == profile_link)).any() ):
          print('Skipped duplicate contact: ', name)
        else:
          writer.writerow([name, title, email, profile_link, website, phone, address, birthday, about, location, experiences, education])
          print('New contact entry: ', name)
          count += 1

      # To scrape only 30 contacts on a single run
      if count >= 3: #30
        break
      
if __name__ == "__main__":
    initial_setup()
