'''
Author: Jing Zhou, Dec 11, 2018
Description: This python script get data from local database.
'''

import sqlite3
import numpy as np
import pandas as pd
import tastediveAPI

# get city list from local db
def getCitiesLocal(dbname):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute('select name from Cities')
    return cur.fetchall()

# get artist list from artist_local.db
def getArtistLocal(cityId):

    artistList_cleaned = list()
    
    # put tables into dataframes
    cnx = sqlite3.connect('artist_local.db')
    df_artist = pd.read_sql("SELECT * FROM Artists", cnx)
    df_event = pd.read_sql("SELECT * FROM Events", cnx)

    # get events of the selected city
    df_event_selected = df_event.loc[df_event['city_id']==cityId]
    artistId_selected = df_event_selected['artist_id'].tolist()
    # eliminate the repeated values, get the artist_id
    artistId_selected = list(set(artistId_selected))

    # get the artists
    for artistId in artistId_selected:
        artists = df_artist.loc[df_artist['artist_id']==artistId]
        artistList = artists['name'].tolist()
        for artist in artistList:
            if artist not in artistList_cleaned:
                artistList_cleaned.append(artist)
    return artistList_cleaned

def getSimilarLocal(user_input_artist, cityId):
    
    cnx = sqlite3.connect('artist_local.db')
    df_similar = pd.read_sql("SELECT * FROM Similars", cnx)
    df_similar_selected = df_similar.loc[df_similar['artist_name']==user_input_artist]

    if len(df_similar_selected) != 0:
        similar_selected = df_similar_selected['similar_artist'].tolist()
        return similar_selected  

    else:
        print('Oops, the similar artist of ' + user_input_artist + ' has not been stored in the db yet')
        print('Would you like to get the similar artists remotely?')
        
        while True:

            user_input_remote = input('Yes or No: ', )

            if user_input_remote == 'Yes': 
                similarArtistList_with_event = tastediveAPI.similarArtistLocal(user_input_artist, cityId)
                return similarArtistList_with_event
    
            elif user_input_remote == 'No':
                print('That is all. See you!')   
                break

            else:
                continue