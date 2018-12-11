'''
USC - INF 510 Dr. Jeremy Abramson
Author: Jing Zhou, Dec 10, 2018

Command input: 
python ZHOU_JING_hw5.py -source=remote
python ZHOU_JING_hw5.py -source=local

User input:
1. Choose the city
2. Choose the artist

Please see details in ZHOU_JING_hw5.txt
'''

import sqlite3
import argparse
import numpy as np
import pandas as pd

import getLocalData
import tastediveAPI
import bandsintownAPI
import songkickScraper

######## start from here #########

def start():  

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-source', type=str)
    # parser.add_argument('-purpose', type=str)

    args = parser.parse_args()
    source = args.source

    # CMD: python ZHOU_JING_hw5.py -source=remote
    if source == 'remote':

        print('------remote------')

        area_url = "https://www.songkick.com/session/filter_metro_area"
        citylinks = songkickScraper.getCities(area_url)

        # create DB
        bandsintownAPI.createDb('artist_remote.db')

        for key, value in citylinks.items() :
            bandsintownAPI.insertDbCity('artist_remote.db', key)
            print (key)

        while True:
            user_input = input('Choose a city above: ', )
            keylist = list(citylinks.keys())
            if user_input in keylist:
                cityId = getCityID(user_input, 'artist_local.db')
                #cityId = getCityID(user_input, 'artist_remote.db')

                print('please wait...it is looking for all the artists who have the upcoming events in ' + user_input)
                
                citylink =  citylinks[user_input]    
                cityUrl = 'https://www.songkick.com' + citylink
                
                # get the max page
                maxPage = songkickScraper.getMaxPage(cityUrl)

                # get all the artists in the chosen city
                artists = songkickScraper.getArtist(maxPage, cityUrl)
                for i in range(0, len(artists)):
                    print (i, artists[i])
                
                print('These ' + str(i) +' artists above have upcoming events in ' + user_input)
                print('Lets save the data into database')

                # clean up the data 
                newArtists = bandsintownAPI.cleanArtistData(artists)
                
                dbname = 'artist_remote.db'

                # add artist info into DB
                bandsintownAPI.getArtistInfo(dbname, newArtists, cityId)
                print('-----------------------------------------------------------------')

                # let user choose an artist
                for i in range(0, len(artists)):
                    print (i, artists[i])
                print('These ' + str(i) +' artists above have upcoming events in ' + user_input) 
                
                while True:         
                    user_input_artist = input('Please choose one artist above who you are interested in, I will recommend someone you may also like: ', )

                    if user_input_artist in artists:

                        # recommend some similiar artists
                        similarArtistList_with_event = tastediveAPI.similarArtistOne(user_input_artist, cityId)

                        if similarArtistList_with_event is None:
                            continue
                        else:
                            for similarArtist in similarArtistList_with_event:
                                print(similarArtist)
                            print('---------------------------------------------')
                            print('Here are the artist(s) we recommend for you! ')    
                            print('Those who end with star key have the upcoming events.')                  
                            print('P.S. all the data have been saved to database.')
                            break
                    else:
                        print('Oops, please choose the artist again.')
                        continue
                break
            else: 
                print('Oops, please choose the city again.')
                continue

    # CMD: python ZHOU_JING_hw5.py -source=local
    elif source == 'local':

        print('------locally------')

        # print cities 
        cityList = getLocalData.getCitiesLocal('artist_local.db')
        cityListNew = []
        for t in cityList:
            for x in t:
                cityListNew.append(x)
        for city in cityListNew:
            print(city)

        while True:
            
            user_input = input('Choose a city above: ', )

            if user_input in cityListNew:
                
                cityId = getCityID(user_input, 'artist_local.db')                
                
                print('please wait...it is looking for all the artists who have the upcoming events in ' + user_input + ' from database') 

                # get all the artists in the chosen city
                artistList = getLocalData.getArtistLocal(cityId)
                for artist in artistList:
                    print(artist)
                
                print('-----------------------------------------------------------------')
                print('These artists above have upcoming events in ' + user_input)

                # let user choose an artist              
                while True:          
                    user_input_artist = input('Please choose an artist above who you are interested in, I will recommend someone you may also like: ', )
                    print('start')
                    if user_input_artist in artistList:

                        # recommend some similiar artists or music
                        similarArtistList_with_event = getLocalData.getSimilarLocal(user_input_artist, cityId)
                            
                        if similarArtistList_with_event is not None:
                            for similarArtist in similarArtistList_with_event:
                                print(similarArtist)

                            print('---------------------------------------------')
                            print('Here are the artist(s) we recommend for you! ')    
                            print('Those who end with star key have the upcoming events.')                  
                            print('P.S. all the data have been saved to database.')
                            break

                        else: 
                            break

                    else:
                        print('Oops, please choose the artist again.')
                        continue
                break
            else: 
                print('Oops, please choose the city again.')
                continue

    else: 
        print("invalid input!")

def getCityID(user_input, dbname):
    cnx = sqlite3.connect(dbname)
    df_city = pd.read_sql("SELECT * FROM Cities", cnx)
    cityId = df_city[df_city['name']==user_input]['id'].values[0]
    # convert from numpy.int64 to int!
    return int(cityId)

######### entrance ##########

if  __name__ == "__main__":
    start()