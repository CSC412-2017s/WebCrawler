#!/usr/bin/python
import argparse, os, time
import urlparse, random
import csv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from bs4 import BeautifulSoup

def getPeopleLinks(page):
    links = []
    for link in page.find_all('a'):
        url = link.get('href')
        if url:
            if 'profile/view?id' in url:
                links.append(url)
    return links


def getJobLinks(page):
    links = []
    for link in page.find_all('a'):
        url = link.get('href')
        if url:
            if '/jobs' in url:
                links.append(url)
    return links


def getID(url):
    pUrl = urlparse.urlparse(url)
    return urlparse.parse_qs(pUrl.query)['id'][0]


def Search(browser):
    visited = {}
    pList = []
    count = 0
    page = BeautifulSoup(browser.page_source)
    people = getPeopleLinks(page)

    with open('names.csv', 'w+') as csvfile:
        fieldnames = ['name', 'experience', 'skills', 'links']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, dialect=csv.Dialect.lineterminator)
        writer.writeheader()
        for i in range(len(people)):
            #time.sleep(random.uniform(3.5, 6.9))

            if people:
                for person in people:
                    ID = getID(person)
                    if ID not in visited:
                        pList.append(person)
                        visited[ID] = 1
                if pList:
                    person = pList.pop()
                    browser.get('https://www.linkedin.com' + person)
                    count += 1
                    time.sleep(5)
                    current = browser.current_url

                    person_page = BeautifulSoup(browser.page_source)

                    name = person_page.find_all('h1')
                    name = name[0].text

                    jobs = person_page.find_all('span', class_='pv-position-entity__secondary-title pv-entity__secondary-title Sans-15px-black-55%')

                    jobs_text = ''

                    for job in jobs:
                        jobs_text += job.text + ','

                    skills = person_page.find_all('span', class_='pv-skill-entity__skill-name truncate Sans-15px-black-85%-semibold inline-block ')
                    skills_text = ''

                    for skill in skills:
                        skills_text += skill.text + ','

                    writer.writerow({
                        'name': name.encode('utf-8'),
                        'experience': jobs_text.encode('utf-8'),
                        'skills': skills_text.encode('utf-8'),
                        'links': current.encode('utf-8'),
                    })
                else:
                    print "Error Cant be founded"
                    break
            print "+" + browser.title + " visited! \n(" \
                  + str(count) + "/" + str(len(pList)) + ") Visited/Queue"


def Main():
    email = ""
    password = ""

    with open('info.txt', 'r') as f:
        email = f.readline().rstrip('\n')
        password = f.readline().rstrip('\n')

    browser = webdriver.Chrome(executable_path=os.path.abspath('C:\\Users\\anton\\Downloads\\chromedriver_win32\\chromedriver.exe'))
    browser.get(url="https://linkedin.com/uas/login")

    emailElement = browser.find_element_by_id("session_key-login")
    emailElement.send_keys(email)

    passElement = browser.find_element_by_id("session_password-login")
    passElement.send_keys(password)
    passElement.submit()

    print "Success! Logged in Bot Starting!"

    time.sleep(10)

    browser.get("https://www.linkedin.com/edu/alumni?id=18770&facets=FS.100189&keyword=&dateType=attended&startYear=&endYear=&incNoDates=true&start=0&count=100&filters=off&hideSchoolAsEmployer=&name=Elizabeth%20City%20State%20University&trk=edu-as-com-CN-4")
    Search(browser)
    browser.close()


Main()