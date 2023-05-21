from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import glob
import csv


def scraper(driver, connection_urls):
    # To check if there is csv file and select the mode to write or append csv accordingly
    global cached_cnt
    csv_files = list(glob.glob("*.csv"))
    if 'linkedin_cache.csv' in csv_files:
        mode = 'a'
    else:
        mode = 'w'

    # with open('linkedin_cache.csv', mode , encoding='UTF-16', newline='') as csvfile: # anisha version
    with open('linkedin_cache.csv', mode, newline='') as csvfile:  # gobi version
        writer = csv.writer(csvfile)
        if mode == 'w':
            writer.writerow(['name', 'title', 'email', 'profile_link', 'phone', 'location'])

        # Scraping
        for url in connection_urls:
            print('\nProcessing for url', url)
            if url in cached_urls:
                print('In scraper: Already cached', url)
                continue
            try:
                driver.get(url)
                time.sleep(10)
                print('Getting details for', url)
                # content = driver.find_element_by_tag_name('main')
                content = driver.find_element(by=By.TAG_NAME, value='main')
                result = content.get_attribute('innerHTML')
                soup = BeautifulSoup(result, 'html.parser')
                # Initialization
                email = phone = location = 'Not mentioned'

                # To click contact info link and open modal
                try:
                    '''
                    pb5 = driver.find_element(by=By.CLASS_NAME, value='pb5')
                    contact_info_link = pb5.find_element(by=By.TAG_NAME, value='a')
                    '''
                    contact_info_link = driver.find_element(By.ID, value="top-card-text-details-contact-info")
                    if contact_info_link.text == 'Contact info':
                        contact_info_link.click()
                        time.sleep(10)
                    else:
                        print("Unable to get contact details for", url)
                        continue
                except Exception:
                    print("Unable to get contact details for", url)
                    continue
                # Extract all information from contact info modal
                # modal = driver.find_element_by_id('artdeco-modal-outlet')
                modal = driver.find_element(By.ID, 'artdeco-modal-outlet')
                # profile_link = modal.find_element_by_class_name('ci-vanity-url').find_element_by_tag_name('a').text
                profile_link = modal.find_element(By.CLASS_NAME, value='ci-vanity-url').\
                    find_element(by=By.TAG_NAME, value='a').text
                if profile_link in cached_urls:
                    print('In scraper: Already cached profile_link', profile_link, 'for url', url)
                    continue
                try:
                    # email = modal.find_element_by_class_name('ci-email').find_element_by_tag_name('a').text
                    email = modal.find_element(By.CLASS_NAME, value='ci-email').\
                        find_element(by=By.TAG_NAME, value='a').text
                except Exception:
                    pass
                try:
                    # phone_nums = modal.find_element_by_class_name('ci-phone').find_elements_by_tag_name('li')
                    phone_nums = modal.find_element(By.CLASS_NAME, value='ci-phone').\
                        find_elements(By.TAG_NAME, value='li')
                    phone = [num.text for num in phone_nums]
                except Exception:
                    pass
                # To close contact info modal
                # modal.find_element_by_tag_name('button').click()
                modal.find_element(by=By.TAG_NAME, value='button').click()
                time.sleep(10)

                # Extracting user basic information
                div1 = soup.find("div", class_='pv-text-details__left-panel')
                name = div1.find("h1", class_='text-heading-xlarge inline t-24 v-align-middle break-words').text.strip()
                # title = soup.find("h2", class_='mt1 t-18 t-black t-normal break-words').text.strip()
                title = div1.find("div", class_='text-body-medium break-words').text.strip()
                try:
                    div2 = soup.find("div", class_="pv-text-details__left-panel mt2")
                    loc_obj = div2.find("span", class_='text-body-small inline t-black--light break-words')
                    if loc_obj:
                        location = loc_obj.text.strip()
                    else:
                        print('No location found for', url)
                except Exception:
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
            except Exception:
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
driver = webdriver.Chrome(options=options)  # gobi version
ans = input("Have you logged into linkedin? y/n:")
if ans != 'y':
    exit(0)
driver.get(URL)
time.sleep(10)

f3 = open('connections.txt')
search_url = "https://www.linkedin.com/search/results/people/?facetNetwork=%5B%22F%22%5D&origin=FACETED_SEARCH"
header_line = True

cnt = 0
linenum = 0
for line in f3:
    linenum += 1
    print('line num in connections.txt', linenum)
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
        # connections = driver.find_elements_by_class_name('entity-result__title-text')
        connections = driver.find_elements(By.CLASS_NAME, value='entity-result__title-text')
        # linkedin_urls = [url.find_element_by_tag_name('a').get_attribute('href') for url in connections]
        linkedin_urls = [url.find_element(by=By.TAG_NAME, value='a').get_attribute('href') for url in connections]
        print(linkedin_urls)
        new_urls = []
        for url in linkedin_urls:
            if url in cached_urls:
                print('In main: Already cached', url)
                continue
            new_urls.append(url)
            f2.write(url + '\n')
        if len(new_urls) == 0:
            continue
        cnt = cnt + 1
        print(cnt, 'new urls found', len(new_urls))
        connection_urls.extend(new_urls)
        if cnt >= 200:
            print('Last processed line number', linenum)
            break


cached_cnt = 0
print('Number of urls to scrape', len(connection_urls))
scraper(driver, connection_urls)
f3.close()
f2.close()
f1.close()
