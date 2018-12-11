'''
Author: Jing Zhou, Dec 10, 2018
Description: This python script gets the details for events(including artists, venues and tickets) via Bandsintown API
API link: http://www.artists.bandsintown.com/bandsintown-api
'''

import sqlite3
import requests
import time
import json
import numpy as np

def cleanArtistData(artists):
    
    newArtists = list()

    for artist in artists:
        # if there are several artists
        if artist.find(',') != -1 :
            multiartists = artist.split(',')
            # loop during these artists
            for multiartist in multiartists:
                # try to del the damn 'and'
                if multiartist.find('and') != -1:
                    newArtist = multiartist.replace('and', '').strip()
                # or just del the blank
                else:
                    newArtist = multiartist.strip()
                # append
                newArtist = newArtist.replace(' ', '')
                if newArtist not in newArtists:
                    newArtists.append(newArtist)
        else:
            newArtist = artist.replace(' ', '')
            if newArtist not in newArtists:
                newArtists.append(newArtist)
    print('artists data cleaned')
    return newArtists

def getArtistInfo(dbname, newArtists, cityId):
    
    app_id = '7b3647c2df2f2942b789250b2b6df7b6' 
    
    for newArtist in newArtists:

        ArtistUrl = 'https://rest.bandsintown.com/artists/' + newArtist + '?app_id=' + app_id
        r = requests.get(ArtistUrl) 
        jsonArtist = r.content

        time.sleep(0.4)

        # table1: artist
        if (len(jsonArtist))>23:

            try:
                artistInfo = json.loads(jsonArtist)

                artistId = artistInfo['id']
                artistName = artistInfo['name']
                artistMainPage = artistInfo['url']
                artistImg = artistInfo['thumb_url']
                artistTrackerCount = artistInfo['tracker_count']
                artistEventCount = artistInfo['upcoming_event_count'] 

                # insert into DB table Artists
                insertDbArtist(dbname, artistId, artistName, artistMainPage, artistImg, artistTrackerCount, artistEventCount)     
                # print('all the new artists are inserted')

                getEventInfo(dbname, newArtist, cityId)
            
            except:
                continue

def getEventInfo(dbname, newArtist, cityId):

    app_id = '7b3647c2df2f2942b789250b2b6df7b6' 

    # newArtists = cleanArtistData(artists)

    # for newArtist in newArtists:
    EventUrl = 'https://rest.bandsintown.com/artists/' + newArtist + '/events?app_id=' + app_id

    r = requests.get(EventUrl) 
    jsonEvent = r.content

    time.sleep(0.4)

    if (len(jsonEvent))>5: 
        EventInfo = json.loads(jsonEvent)

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

                insertDbEvent(dbname, eventId, artistId, eventUrl, onSaleDate, eventDate, cityId)

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
                    insertDbVenue(dbname, eventId, venueName, venueCountry, venueCity, venueRegion, venueLat, venueLon)

                # table4: ticket
                tktUrl = eachEventInfo['offers'][0]['url']
                tktType =  eachEventInfo['offers'][0]['type']
                status =  eachEventInfo['offers'][0]['status']
                print(tktType,status)
                # insert into DB table Tickets
                insertDbTkt(dbname, tktUrl, tktType, status, eventId)

                print('events, tickets and venues for ' + eventId + ' are inserted')

            except:
                continue

#create tables
def createDb(dbname):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()

    cur.execute('DROP TABLE IF EXISTS Cities ')
    cur.execute('CREATE TABLE Cities \
        (name TEXT, \
        id INTEGER PRIMARY KEY \
        )' 
    ) 

    cur.execute('DROP TABLE IF EXISTS Artists ')
    cur.execute('CREATE TABLE Artists \
        (name TEXT, \
        mainpage TEXT, \
        img_url TEXT, \
        tracker_count INTEGER, \
        event_count INTEGER, \
        artist_id INTEGER, \
        id INTEGER PRIMARY KEY \
        )' 
    ) 

    cur.execute('DROP TABLE IF EXISTS Events ')
    cur.execute('CREATE TABLE Events \
        (event_id INTEGER, \
        artist_id INTEGER, \
        event_url TEXT, \
        event_date DATE, \
        on_sale_date DATE, \
        venue_id INTEGER, \
        ticket_id INTEGER, \
        city_id INTEGER, \
        id INTEGER PRIMARY KEY \
        )' 
    ) 

    cur.execute('DROP TABLE IF EXISTS Venues ')
    cur.execute('CREATE TABLE Venues \
        (name TEXT, \
        country TEXT, \
        city TEXT, \
        region TEXT, \
        latitude INTEGER, \
        longitude INTEGER, \
        event_id INTEGER, \
        id INTEGER PRIMARY KEY \
        )' 
    ) 

    cur.execute('DROP TABLE IF EXISTS Tickets ')
    cur.execute('CREATE TABLE Tickets \
        (event_id INTEGER, \
        tktType TEXT, \
        tktUrl TEXT, \
        status TEXT, \
        id INTEGER PRIMARY KEY \
        )' 
    )                

    # join event, ticket and venue through event_id
    cur = conn.execute('select * from Events e join Tickets t on e.event_id = t.event_id')
    cur = conn.execute('select * from Events e join Venues v on e.event_id = v.event_id') 
    cur = conn.execute('select * from Events e join Tickets t on e.ticket_id = t.id')
    cur = conn.execute('select * from Events e join Venues v on e.venue_id = v.id') 
    cur = conn.execute('select * from Cities c join Events e on c.id = e.city_id')

    print('artist_remote.db created')

    conn.close()

#table: Cities
def insertDbCity(dbname, cityName):

    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()  

    cursor.execute('SELECT * FROM Cities WHERE (name=?)', (cityName,))
    entry = cursor.fetchone()  

    if entry is None:
        cursor.execute('INSERT INTO Cities (name) VALUES (?)', (cityName,))
        cursor.execute('SELECT * FROM Cities WHERE (name=?)', (cityName,))
        entry = cursor.fetchone()

    conn.commit()
    conn.close()

#table: Artists
def insertDbArtist(dbname, artistId, artistName, artistMainPage, artistImg, artistTrackerCount, artistEventCount):

    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Artists WHERE (artist_id=?)', (artistId,))
    entry = cursor.fetchone()  
    
    if entry is None:
        cursor.execute('INSERT INTO Artists (artist_id, name, mainpage, img_url, tracker_count, event_count)\
                        VALUES (?,?,?,?,?,?)',
                       (artistId, artistName, artistMainPage, artistImg, artistTrackerCount, artistEventCount))
        
        print('artist ' + artistName + ' added to table Artists')
        cursor.execute('SELECT * FROM Artists WHERE (artist_id=?)', (artistId,))
        entry = cursor.fetchone()

    else:
        print('Artist ' + artistName + ' already existed')

    conn.commit()
    conn.close()

#table: Events
def insertDbEvent(dbname, eventId, artistId, eventUrl, onSaleDate, eventDate, cityId):

    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    # Events
    cursor.execute('SELECT * FROM Events WHERE (event_id=?)', (eventId,))
    entry = cursor.fetchone()

    if entry is None:
        cursor.execute('INSERT INTO Events (event_id, artist_id, event_url, event_date, on_sale_date, city_id)\
                        VALUES (?, ?, ?, ?, ?, ?)',
                       (eventId, artistId, eventUrl, eventDate, onSaleDate, cityId))
        
        print('New event ' + eventId + ' added to table Events')
        cursor.execute('SELECT * FROM Events WHERE (event_id=?)', (eventId,))
        entry = cursor.fetchone()
    
    else:
        print('Events ' + eventId + ' already existed')
        
    conn.commit()
    conn.close()

#table: Venues
def insertDbVenue(dbname, eventId, venueName, venueCountry, venueCity, venueRegion, venueLat, venueLon):

    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    
    # Events
    cursor.execute('SELECT * FROM Venues WHERE (Name=?)', (venueName,))
    entry = cursor.fetchone()

    if entry is None:
        cursor.execute('INSERT INTO Venues (name, country, city, region, latitude, longitude, event_id)\
                        VALUES (?, ?, ?, ?, ?, ?, ?)', 
                       (venueName, venueCountry, venueCity, venueRegion, venueLat, venueLon, eventId,))
        
        print('New venue ' + venueName + ' added to table Venues')
        cursor.execute('SELECT * FROM Venues WHERE (name=?)', (venueName,))
        entry = cursor.fetchone()
    
    else:
        print('Venue ' + venueName + ' already existed')
        
    conn.commit()
    conn.close()

#table: Tickets
def insertDbTkt(dbname, tktUrl, tktType, status, eventId):

    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM Tickets WHERE (tktUrl=?)', (tktUrl,))
    entry = cursor.fetchone()

    if entry is None:
        cursor.execute('INSERT INTO Tickets (\
                        tktUrl, tktType, status, event_id)\
                        VALUES (?, ?, ?, ?)', 
                       (tktUrl, tktType, status, eventId,))
        
        print('New Ticket for ' + eventId + ' added to table Ticket')
        cursor.execute('SELECT * FROM Tickets WHERE (tktUrl=?)', (tktUrl,))
        entry = cursor.fetchone()
    
    else:
        print('Ticket for ' + eventId + ' already existed')
        
    conn.commit()
    conn.close()