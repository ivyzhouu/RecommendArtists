'''
Author: Jing Zhou, Dec 10, 2018
Description: This python script scrapes data directly from Songkick website.
link: https://www.songkick.com/session/filter_metro_area
'''

import requests
from bs4 import BeautifulSoup

# check if the url can be opened or read 
def checkUrl(url):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        return soup

    except ValueError:
        print("Cannot open or read the Songkick URL!")

# get the list of 30 cities
def getCities(area_url):
    citylinks = dict()
    soup = checkUrl(area_url)
    # <ol>: US, UK, EU
    for ols in soup.findAll('ol'):
        # <li>: 10 cities
        for liTag in ols: 
            if liTag.find('a') != -1 and liTag.find('a') != None:
                citywithCountry = liTag.find('a').text
                city = citywithCountry.split(',')[0]
                link = liTag.find('a').attrs['href']
                citylinks[city]=link
    return citylinks

# get the max page of event page
def getMaxPage(cityUrl):
    soup = checkUrl(cityUrl)
    maxPage = soup.find('div',{'class':"pagination"}).findAll('a')[-2].text
    return maxPage

# get the list of artists
def getArtist(maxPage, cityUrl):
    # for test, only pick 2 pages 
    maxPage = 2
    artists = list() 
    for currentPage in range(1, int(maxPage)):
        cityWithPageUrl = cityUrl + '?page=' + str(currentPage)
        soup = checkUrl(cityWithPageUrl)
        allArtists = soup.findAll('p', {'class': 'artists summary'})
        for artist in allArtists:
            artistName = artist.find('strong').text
            if artistName not in artists:
                artists.append(artistName)
    return artists
