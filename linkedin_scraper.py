from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
import glob
import csv

def initial_setup():
  PATH = "./chromedriver" 
  options = webdriver.ChromeOptions()
  options.add_argument("--start-maximized")

  URL = "https://www.linkedin.com/mynetwork/invite-connect/connections/"
  driver = webdriver.Chrome(PATH, chrome_options=options) # anisha version
  # driver = webdriver.Chrome(chrome_options=options) # gobi version
  driver.get(URL)
  time.sleep(50)
  connections = driver.find_elements_by_class_name('mn-connection-card')
  connection_urls = [ url.find_element_by_tag_name('a').get_attribute('href') for url in connections ]

  scraper(driver, connection_urls)

def get_detail(value):
  interval = value.find("h4", class_ = 'pv-entity__date-range t-14 t-black--light t-normal').find_all("span")[1].text
  duration = value.find("h4", class_ = 't-14 t-black--light t-normal').find_all("span")[1].text
  try:
    desc = value.find("p", class_ = 'pv-entity__description t-14 t-black t-normal inline-show-more-text inline-show-more-text--is-collapsed ember-view')
    for tag in desc.select('span'):
      tag.extract()
    desc = '\n' + ' \u2022 ' + desc.text.replace('\n', '').strip()
  except:
    desc = ''
  try:
    location = ' \u2022 ' + value.find("h4", class_ = 'pv-entity__location t-14 t-black--light t-normal block').find_all("span")[1].text
  except:
    location = ''
  data = interval + ' (' + duration + ')' + location + desc
  return data

def single_role(experience):
  title = experience.find("h3", class_ = 't-16 t-black t-bold').text
  company = experience.find("p", class_ = 'pv-entity__secondary-title t-14 t-black t-normal').text.strip()
  detail = get_detail(experience)
  data = company + ' ---> ' + '\n' + '- ' + title + ' \u2022 ' + detail
  return data

def multi_role(experience):
  all_roles = []
  company = experience.find("h3", class_ = 't-16 t-black t-bold').find_all("span")[1].text
  multi_roles = experience.find_all("li", class_ = 'pv-entity__position-group-role-item')
  for role in multi_roles:
    role_title = role.find("h3", class_ = 't-14 t-black t-bold').find_all("span")[1].text 
    detail = get_detail(role)
    role = '- ' + role_title + ' \u2022 ' + detail
    all_roles.append(role)
  all_roles = '\n\n'.join(all_roles)
  data = company + ' ---> ' + '\n' + all_roles
  return data

def get_education(item):
  institute = item.find("h3", class_ = 'pv-entity__school-name t-16 t-black t-bold').text
  degree_date = item.find("p", class_ = 'pv-entity__dates t-14 t-black--light t-normal').find_all("span")[1].text.strip()

  try:
    degree = ' \u2022 ' + item.find("p", class_ = 'pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal').find_all("span")[1].text
  except:
    degree = ''

  try:
    field = ', ' + item.find("p", class_ = 'pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal').find_all("span")[1].text
  except:
    field = ''

  try:
    desc = item.find("p", class_ = 'pv-entity__description t-14 t-normal mt4')
    for tag in desc.select('span'):
      tag.extract()
    desc = '\n' + ' \u2022 ' + desc.text.replace('\n', '').strip()
  except:
    desc = ''

  try:
    extra = ' \u2022 ' + item.find("p", class_ = 'pv-entity__secondary-title t-14 t-black--light t-normal').text
  except:
    extra = ''

  data = institute + degree + field + ' \u2022 ' + degree_date + extra + desc
  return data

def scraper(driver, connection_urls):

  # To check if there is csv file and select the mode to write or append csv accordingly
  csv_files = list(glob.glob("*.csv"))
  if ('linkedin_cache.csv' in csv_files):
    mode = 'a'
  else:
    mode = 'w'

  with open('linkedin_cache.csv', mode , encoding='UTF-16', newline='') as csvfile: # anisha version
  # with open('linkedin_cache.csv', mode, newline='') as csvfile: # gobi version
    writer = csv.writer(csvfile)
    if mode == 'w':
      writer.writerow(['name', 'title', 'email', 'profile_link', 'website', 'phone', 'address', 'birthday', 'about', 'location', 'experiences', 'education'])

    for url in connection_urls:
      driver.get(url)
      time.sleep(5)
      content = driver.find_element_by_tag_name('main')
      result = content.get_attribute('innerHTML')
      soup = BeautifulSoup(result, 'html.parser')

      # Initialization
      website = phone = address = birthday = about = 'Not mentioned'
      experiences = []
      education = []

      # To click contact info link and open modal
      driver.find_element_by_css_selector("a[data-control-name='contact_see_more']").click()
      time.sleep(5)

      # Extract all information from contact info modal
      modal         = driver.find_element_by_id('artdeco-modal-outlet')
      email         = modal.find_element_by_class_name('ci-email').find_element_by_tag_name('a').text
      profile_link  = modal.find_element_by_class_name('ci-vanity-url').find_element_by_tag_name('a').text
      
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
      name = soup.find("li", class_ = 'inline t-24 t-black t-normal break-words').text.strip()
      title = soup.find("h2", class_ = 'mt1 t-18 t-black t-normal break-words').text.strip()
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

      time.sleep(2)

      # Extracting experiences 
      experience_section = driver.find_element_by_class_name('experience-section')
      experience_section = BeautifulSoup(experience_section.get_attribute('innerHTML'), 'html.parser')
      experience_list = experience_section.find_all("li", class_ = 'pv-entity__position-group-pager pv-profile-section__list-item ember-view')
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
      education_list = education_section.find_all("li", class_ = 'pv-profile-section__list-item pv-education-entity pv-profile-section__card-item ember-view')
      for item in education_list:
        data = get_education(item)
        education.append(data)
      education = '\n\n'.join(education)
      
      # To check duplicate and skip the contact if duplicate
      if (mode == 'w'):
        writer.writerow([name, title, email, profile_link, website, phone, address, birthday, about, location, experiences, education])
        print('New contact entry: ', name)
      else:
        df = pd.read_csv('linkedin_cache.csv', encoding = 'UTF-16')
        if ( ((df['name'] == name) & (df['email'] == email)).any() ):
          print('Skipped duplicate contact: ', name)
        else:
          writer.writerow([name, title, email, profile_link, website, phone, address, birthday, about, location, experiences, education])
          print('New contact entry: ', name)

if __name__ == "__main__":
    initial_setup()