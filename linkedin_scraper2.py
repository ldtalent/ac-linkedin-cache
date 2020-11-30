from selenium import webdriver
from bs4 import BeautifulSoup
import time
import glob
import csv


def scraper(driver, connection_urls):
    # To check if there is csv file and select the mode to write or append csv accordingly
    global cached_cnt
    csv_files = list(glob.glob("*.csv"))
    if ('linkedin_cache.csv' in csv_files):
        mode = 'a'
    else:
        mode = 'w'

    # with open('linkedin_cache.csv', mode , encoding='UTF-16', newline='') as csvfile: # anisha version
    with open('linkedin_cache.csv', mode, newline='') as csvfile: # gobi version
        writer = csv.writer(csvfile)
        if mode == 'w':
            writer.writerow(['name', 'title', 'email', 'profile_link', 'phone', 'location'])

        # Scraping
        for url in connection_urls:
            if url in cached_urls:
                print('Already cached', url)
                continue
            try:
                driver.get(url)
                time.sleep(10)
                print('Getting details for', url)
                content = driver.find_element_by_tag_name('main')
                result = content.get_attribute('innerHTML')
                soup = BeautifulSoup(result, 'html.parser')
                # Initialization
                email = phone = location = 'Not mentioned'

                # To click contact info link and open modal
                driver.find_element_by_css_selector("a[data-control-name='contact_see_more']").click()
                time.sleep(10)
                # Extract all information from contact info modal
                modal = driver.find_element_by_id('artdeco-modal-outlet')
                profile_link = modal.find_element_by_class_name('ci-vanity-url').find_element_by_tag_name('a').text

                try:
                    email = modal.find_element_by_class_name('ci-email').find_element_by_tag_name('a').text
                except Exception as e:
                    pass

                try:
                    phone_nums = modal.find_element_class_name('ci-phone').find_elements_by_tag_name('li')
                    phone = [num.text for num in phone_nums]
                except Exception as e:
                    pass
                # To close contact info modal
                modal.find_element_by_tag_name('button').click()
                time.sleep(10)

                # Extracting user basic information
                name = soup.find("li", class_='inline t-24 t-black t-normal break-words').text.strip()
                title = soup.find("h2", class_='mt1 t-18 t-black t-normal break-words').text.strip()
                loc_obj = soup.find("li", class_='t-16 t-black t-normal inline-block')
                if loc_obj:
                    location = soup.find("li", class_='t-16 t-black t-normal inline-block').text.strip()
                else:
                    print('No location found for', url)

                print('name', name, 'title', title, 'location', location)
                writer.writerow([name, title, email, profile_link, phone, location])
                f1.write(profile_link + '\n')
                cached_cnt = cached_cnt + 1
                print(cached_cnt, 'cached', profile_link)
                '''
                ans = input('Do you want to continue? y/n:')
                if ans.lower() != 'y':
                    exit(0)
                '''
                time.sleep(20)
            except Exception as e:
                print("Unable to get details for", url)


f1 = open('cached.txt')
cached_urls = []
for line in f1:
    cached_urls.append(line[:-1])
f1.close()
f1 = open('cached.txt', 'a')

connection_urls = []
f2 = open('connection_urls.txt')
for line in f2:
    connection_urls.append(line[:-1])
f2.close()
f2 = open('connection_urls.txt', 'a')

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

URL = "https://www.linkedin.com/mynetwork/invite-connect/connections/"
driver = webdriver.Chrome(chrome_options=options) # gobi version
ans = input("Have you logged into linkedin? ")
if ans != 'y':
    exit(0)
driver.get(URL)
time.sleep(10)

f3 = open('connections.txt')
search_url = "https://www.linkedin.com/search/results/people/?facetNetwork=%5B%22F%22%5D&origin=FACETED_SEARCH"
header_line = True

cnt = 0
for line in f3:
    if header_line:
        # Set header_line to False after reading first line
        header_line = False
        continue
    if line.strip() == '':
        continue
    parts = line.split(',')
    nparts = len(parts)
    params = ''
    if nparts > 0:
        fname = parts[0].strip()
        params += "&firstName=" + fname
        if nparts > 1:
            lname = parts[1].strip()
            params += "&lastName=" + lname
        url = search_url + params
        print('cnt =', cnt)
        print('browse to', url)
        time.sleep(10)
        driver.get(url)
        time.sleep(10)
        connections = driver.find_elements_by_class_name('search-result__info')
        linkedin_urls = [url.find_element_by_tag_name('a').get_attribute('href') for url in connections]
        print(linkedin_urls)
        for url in linkedin_urls:
            f2.write(url + '\n')
        cnt = cnt + 1
        connection_urls.extend(linkedin_urls)
        if cnt >= 50:
            break

cached_cnt = 0
scraper(driver, connection_urls)
f3.close()
f2.close()
f1.close()
