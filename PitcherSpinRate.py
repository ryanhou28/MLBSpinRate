#imports
import matplotlib
import os
from urllib.request import urlopen, urlretrieve, Request, URLopener
from bs4 import BeautifulSoup as soup
import requests
from selenium import webdriver, common
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import lxml

import matplotlib.pyplot as plt
import numpy as np
import chromedriver_binary

#Setup

search_player = input("Enter Name of Player: ")

#Demo URL
#url = "https://baseballsavant.mlb.com/savant-player/trevor-bauer-545333?stats=statcast-r-pitching-mlb"

#Find Player URL Based on MlB Website
mlb_url = "https://www.mlb.com/players"

driver = webdriver.Chrome()
driver.set_page_load_timeout(10)
try:
    driver.get(mlb_url)
except TimeoutException:
    driver.execute_script("window.stop();")


html = driver.page_source
mlb_soup = soup(html, 'html.parser')

players = mlb_soup.findAll('a', {'class':'p-related-links__link'})

for player in players:
    if (player.text == search_player):
        href = player['href']
        href = href[7:]
        #print(href)
        break

#Begin Scraping from Baseball Savant
url = "https://baseballsavant.mlb.com/savant-player" + href

print("URL: " + url)

try:
    driver.get(url)
except TimeoutException:
    driver.execute_script("window.stop();")
#req = requests.get(url)
#page_soup = soup(req.content, 'html.parser')

html = driver.page_source
page_soup = soup(html, 'html.parser')

#Player Bio

player_name_container = page_soup.find('div', class_='bio-player-name')

name_div = player_name_container.find('div', {"style":"display: inline-block"})

player_name = name_div.text

print("Player Name: " + player_name)

#Find Spin Rate

pitch_table = page_soup.findAll('tr', {"style":"background-color: #f5f5f5;;"})

pitch_table2 = page_soup.findAll('tr', {"style":"background-color: #ffffff;"})

spin_rate_array = []
year_array = []
velo_array = []
era_array = []
pitch_table_array = [pitch_table, pitch_table2]

#Grab Spin Rate and Year Data
for table in pitch_table_array:
    for row in table:
        columns = row.findAll('td')
        year = columns[0].text
        pitch_type = columns[1].text
        spin_rate = columns[-4].find('span').text
        velo = columns[6].text

        if (pitch_type == '4-Seam Fastball'):
            if (spin_rate != ''):
                spin_rate_array.append(spin_rate)
                year_array.append(year.strip())
                velo_array.append(velo.strip())


#Gather ERA Data
try:
    driver.get('https://www.mlb.com/player/' + href)
except TimeoutException:
    driver.execute_script("window.stop();")

era_html = driver.page_source
era_soup = soup(era_html, 'html.parser')

stat_table = era_soup.find('div', {"class":'career-table'}).find('tbody')
rows = stat_table.findAll('tr')


for row in rows:
    columns = row.findAll('td')

    try:
        era_year = columns[0].find('span').text
        era = columns[5].find('span').text

        for year in year_array:
            if (year == era_year):
                era_array.append(era)
    except:
        continue

#Convert from String to Int/Float

for i in range(0, len(spin_rate_array)):
    if (spin_rate_array[i] != ''):
        spin_rate_array[i] = int(spin_rate_array[i])

for i in range(0, len(year_array)):
    if (year_array[i] != ''):
        year_array[i] = int(year_array[i])

for i in range(0, len(velo_array)):
    if (velo_array[i] != ''):
        velo_array[i] = float(velo_array[i])

for i in range(0, len(era_array)):
    if (era_array[i] != ''):
        era_array[i] = float(era_array[i])

#Close Webpage
driver.close()

#Display Data

print("Year (Unsorted):")
print(year_array)
print("Spin Rate (Unsorted):")
print(spin_rate_array)
print("Velo (Unsorted):")
print(velo_array)
print("ERA (Sorted):")
print(era_array)

fig, axs = plt.subplots(3, figsize=(12, 10))  # Create figures and axes


#Sort Unsorted Data
list_spin=zip(*sorted(zip(*(year_array,spin_rate_array))))
list_velo=zip(*sorted(zip(*(year_array,velo_array))))

#Plot Data

#   Spin Rate
axs[0].plot(*list_spin)
axs[0].set_title(player_name + " 4-Seam Fastball Spin Rate over Time")
axs[0].set(xlabel='Year', ylabel='AVG Spin Rate (RPM)')


for i, v in enumerate(spin_rate_array):
    axs[0].text(year_array[i] - 0.25, v + 0.5, str(v))

#   Velo

axs[1].plot(*list_velo)
axs[1].set_title(player_name + " 4-Seam Fastball Velocity over Time")
axs[1].set(xlabel='Year', ylabel='AVG Velo (MPH)')


for i, v in enumerate(velo_array):
    axs[1].text(year_array[i] - 0.25, v + 0.01, str(v))

#  ERA

sorted_year_array = year_array
sorted_year_array.sort()

print("Year (Sorted):")
print(sorted_year_array)

axs[2].plot(sorted_year_array, era_array)
axs[2].set_title(player_name + " ERA over Time")
axs[2].set(xlabel='Year', ylabel='ERA')

for i, v in enumerate(era_array):
    axs[2].text(sorted_year_array[i] - 0.25, v + 0.01, str(v))

plt.tight_layout()

plt.show()
