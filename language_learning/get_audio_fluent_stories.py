# get audio on https://www.fluentwithstories.com/

import requests
from bs4 import BeautifulSoup
import re

url = input("URL of page where mp3 audio is to be found.\n> ")
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

# "normal" links to audio; this retrieves nothing on the
# Fluent With Stories site ... but might be useful for other sites.
links = soup.find_all('a', href=re.compile(r'\d+\s*.mp3$'))
for link in links:
    print(link)

for div_tag in soup.find_all('div'):
    text = div_tag.text.strip()
    if text.startswith("http") and text.endswith(".mp3"):
        print(text)
