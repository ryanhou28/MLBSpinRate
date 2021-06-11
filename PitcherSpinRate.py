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
        print(href)
        break

driver.close()

url = "https://baseballsavant.mlb.com/savant-player" + href

print("URL: " + url)


req = requests.get(url)
page_soup = soup(req.content, 'html.parser')


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
pitch_table_array = [pitch_table, pitch_table2]

#Grab Spin Rate and Year Data
for table in pitch_table_array:
    for row in table:
        columns = row.findAll('td')
        year = columns[0].text
        pitch_type = columns[1].text
        spin_rate = columns[-4].find('span').text

        if (pitch_type == '4-Seam Fastball'):
            if (spin_rate != ''):
                spin_rate_array.append(spin_rate)
                year_array.append(year.strip())


#Convert from String to Int

for i in range(0, len(spin_rate_array)):
    if (spin_rate_array[i] != ''):
        spin_rate_array[i] = int(spin_rate_array[i])

for i in range(0, len(year_array)):
    if (year_array[i] != ''):
        year_array[i] = int(year_array[i])

#Display Info

print("Year:")
print(year_array)
print("Spin Rate:")
print(spin_rate_array)

fig, ax = plt.subplots()  # Create a figure containing a single axes


#Sort Data
list=zip(*sorted(zip(*(year_array,spin_rate_array))))

#Plot Data
plt.plot(*list)
plt.title(player_name + " 4-Seam Fastball Spin Rate over Time")
plt.xlabel("Year")
plt.ylabel("AVG Spin Rate (RPM)")


for i, v in enumerate(spin_rate_array):
    plt.text(year_array[i] - 0.25, v + 0.5, str(v))

plt.show()
