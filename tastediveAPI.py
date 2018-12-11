'''
Author: Jing Zhou, Dec 10, 2018
Description: This python script gets the recommendations for artists via tastedive API
API link: https://tastedive.com/read/api
Limit: 300 requests per hour
'''

import time
import json
import sqlite3
import requests
import bandsintownAPI

# get the similar artists of what user input
def similarArtistOne(user_input_artist, cityId):

    similarArtistList_with_event = list()

    access_key = '324611-Jane-TH6MQQ3R' 

    diveUrl = 'https://tastedive.com/api/similar?q=' + user_input_artist + '&type=music&verbose=1&k=' + access_key
    re = requests.get(diveUrl) 
    jsonSimilar = re.content

    time.sleep(0.4)

    if (len(jsonSimilar))>50:

        try:

            # create table Similars
            createTable()

            similarInfo = json.loads(jsonSimilar)
            # the artist name 
            artistName = similarInfo['Similar']['Info'][0]['Name']

            # the similar artists
            similarResults = similarInfo['Similar']['Results']
            
            if len(similarResults) != 0:
                # may have multiple similar artists
                for i, element in enumerate(similarResults):
                    similarArtist = similarResults[i]['Name']
                    wikiUrl = similarResults[i]['wUrl']
                    wikiTeaser = similarResults[i]['wTeaser']
                    yUrl = similarResults[i]['yUrl']  

                    # insert into DB table Similars
                    # dbname = 'artist_local.db'
                    dbname = 'artist_remote.db'
                    insertDbSimilar(dbname, artistName, similarArtist, wikiUrl, wikiTeaser, yUrl)
                    
                    # check if the similar artists have any upcoming events
                    similarArtist_new = getSimilarEvent(similarArtist, cityId)
                    
                    if similarArtist_new not in similarArtistList_with_event:
                        similarArtistList_with_event.append(similarArtist_new)
                
                print('-----------------------------------------------')
                
                return similarArtistList_with_event

            else:
                print('Oops, you have a minority taste! We do not have any recommendations for ' + user_input_artist + ' right now.')

        except:
            None
    else:
        print('Oops, you have a minority taste! We do not have any recommendations right now.')

# get all the recommendations for all the artists in the list
def similarArtist(newArtists, cityId):
    
    # create table Similars
    # createTable()

    similarArtistList = list()

    access_key = '324611-Jane-TH6MQQ3R' 

    for newArtist in newArtists:
    
        diveUrl = 'https://tastedive.com/api/similar?q=' + newArtist + '&type=music&verbose=1&k=' + access_key
        r = requests.get(diveUrl) 
        jsonSimilar = r.content

        time.sleep(0.4)

        if (len(jsonSimilar))>50:

            try:
                similarInfo = json.loads(jsonSimilar)
                # the artist name 
                artistName = similarInfo['Similar']['Info'][0]['Name']
                
                # the similar artists
                similarResults = similarInfo['Similar']['Results']
                if len(similarResults) != 0:

                    for i, element in enumerate(similarResults):
                        similarArtist = similarResults[i]['Name']
                        wikiUrl = similarResults[i]['wUrl']
                        wikiTeaser = similarResults[i]['wTeaser']
                        yUrl = similarResults[i]['yUrl']  

                        # save it into list
                        if similarArtist not in similarArtistList:
                            similarArtistList.append(similarArtist)

                        # insert into DB table Similars
                        dbname = 'artist_remote.db'
                        insertDbSimilar(dbname, artistName, similarArtist, wikiUrl, wikiTeaser, yUrl)

                        # check if the similar artists have any upcoming events
                        getSimilarEvent(similarArtist, cityId)

            except:
                continue
        
        time.sleep(10)
    
    return similarArtistList

# get the similar artists of what user input
def similarArtistLocal(user_input_artist, cityId):

    similarArtistList_with_event = list()

    access_key = '324611-Jane-TH6MQQ3R' 

    diveUrl = 'https://tastedive.com/api/similar?q=' + user_input_artist + '&type=music&verbose=1&k=' + access_key
    
    re = requests.get(diveUrl) 
    jsonSimilar = re.content

    time.sleep(0.4)

    if (len(jsonSimilar))>50:

        try:

            similarInfo = json.loads(jsonSimilar)
            # the artist name 
            artistName = similarInfo['Similar']['Info'][0]['Name']

            # the similar artists
            similarResults = similarInfo['Similar']['Results']

            if len(similarResults) != 0:
                # may have multiple similar artists

                for i, element in enumerate(similarResults):
                    similarArtist = similarResults[i]['Name']
                    wikiUrl = similarResults[i]['wUrl']
                    wikiTeaser = similarResults[i]['wTeaser']
                    yUrl = similarResults[i]['yUrl']  

                    # insert into DB table Similars
                    dbname = 'artist_local.db'
                    insertDbSimilar(dbname, artistName, similarArtist, wikiUrl, wikiTeaser, yUrl)
                 
                    # check if the similar artists have any upcoming events
                    similarArtist_new = getSimilarEvent(similarArtist, cityId)

                    if similarArtist_new not in similarArtistList_with_event:
                        similarArtistList_with_event.append(similarArtist_new)

                print('-----------------------------------------------')
                
                return similarArtistList_with_event

            else:
                print('Oops, you have a minority taste! We do not have any recommendations for ' + user_input_artist + ' right now even remotely.')

        except:
            pass
    else:
        print('Oops, you have a minority taste! We do not have any recommendations right now even remotely.')

#create table
def createTable():
    conn = sqlite3.connect('artist_remote.db')
    cur = conn.cursor()

    # cur.execute('DROP TABLE IF EXISTS Similars ')
    cur.execute('CREATE TABLE Similars \
        (artist_name TEXT, \
        similar_artist TEXT, \
        w_url TEXT, \
        w_Teaser TEXT, \
        y_url TEXT, \
        id INTEGER PRIMARY KEY \
        )' 
    )      
    # join       
    cur = conn.execute('select * from Similars s join Artists a on s.artist_name = a.name')

    print('table Similars created')

    conn.close()

#table: Similar
def insertDbSimilar(dbname, artistName, similarArtist, wikiUrl, wikiTeaser, yUrl):

    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Similars WHERE (similar_artist=?)', (similarArtist,))
    entry = cursor.fetchone()  
    
    if entry is None:
        cursor.execute('INSERT INTO Similars (artist_name, similar_artist, w_url, w_Teaser, y_url)\
                        VALUES (?,?,?,?,?)',
                       (artistName, similarArtist, wikiUrl, wikiTeaser, yUrl))
        
        print('Similar artist ' + similarArtist + ' added to table Similars')
        cursor.execute('SELECT * FROM Similars WHERE (similar_artist=?)', (similarArtist,))
        entry = cursor.fetchone()

    else:
        print('Similar artist ' + similarArtist + '  already added to table Similars')

    conn.commit()
    conn.close()

# check if this similar artist has upcoming events
def getSimilarEvent(similarArtist, cityId):

    dbname = 'artist_local.db'

    app_id = '7b3647c2df2f2942b789250b2b6df7b6' 

    EventUrl = 'https://rest.bandsintown.com/artists/' + similarArtist + '/events?app_id=' + app_id

    r = requests.get(EventUrl) 
    jsonEvent = r.content

    time.sleep(0.4)

    if (len(jsonEvent))>5: 

        EventInfo = json.loads(jsonEvent)
        
        print('-----------------------------------------------------------------')
        print('The similar artist ' + similarArtist + ' also has the upcoming events!!')
        print('-----------------------------------------------------------------')

        similarArtist_new = str(similarArtist + ' *')
        
        # loop in mutiple events
        for eachEventInfo in EventInfo:   
            try:
                # table2: event
                eventId = eachEventInfo['id']
                artistId = eachEventInfo['artist_id']
                eventUrl = eachEventInfo['url']
                onSaleDate = eachEventInfo['on_sale_datetime']
                eventDate = eachEventInfo['datetime']

                # insert into DB table Events
                bandsintownAPI.insertDbEvent(dbname, eventId, artistId, eventUrl, onSaleDate, eventDate, cityId)

                # table3: venue
                venueNames = list()
                venueName = eachEventInfo['venue']['name']
                # filter the repeated ones
                if venueName not in venueNames:
                    venueNames.append(venueName)
                    venueCountry = eachEventInfo['venue']['country']
                    venueCity = eachEventInfo['venue']['city']
                    venueRegion = eachEventInfo['venue']['region']
                    venueLat = eachEventInfo['venue']['latitude']
                    venueLon = eachEventInfo['venue']['longitude']

                    # insert into DB table Venues
                    bandsintownAPI.insertDbVenue(dbname, eventId, venueName, venueCountry, venueCity, venueRegion, venueLat, venueLon)

                # table4: ticket
                tktUrl = eachEventInfo['offers'][0]['url']
                tktType =  eachEventInfo['offers'][0]['type']
                status =  eachEventInfo['offers'][0]['status']

                # insert into DB table Tickets
                bandsintownAPI.insertDbTkt(dbname, tktUrl, tktType, status, eventId)

            except:
                continue
            
    else:
        print('The similar artist ' + similarArtist + ' do not have upcoming events!')
        similarArtist_new = str(similarArtist)

    return similarArtist_new
    