#!/usr/bin/env python
# coding: utf-8

# In[199]:


from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import time


# In[200]:


def DownloadNextPage():
    nextUrl = baseUrl % (currentPage * pageSize)
    print('Downloading: ' + nextUrl)
    response = get(nextUrl)
    return BeautifulSoup(response.text, 'html.parser')

def GetGameLinks(html_soup):
    currentPapeGameLinks = []
    gamesLinks = html_soup.select('table#mof_object_list tbody tr td:first-child a')
    lastPage = len(gamesLinks) < pageSize

    for gameLink in gamesLinks:
        currentPapeGameLinks.append(gameLink['href'])
    return currentPapeGameLinks, lastPage

def GetGamesData(gameLinks):
    df = pd.DataFrame()
    for gameLink in gameLinks:
        print('Downloading: ' + gameLink)
        response = get(gameLink)
        html_soup = BeautifulSoup(response.text, 'html.parser')
        tittle = html_soup.find('h1', class_='niceHeaderTitle').a.text
        game = {'GameTittle': tittle}
        #print(tittle)

        gameData = html_soup.select('div#coreGameRelease div')
        for attributeName, attributeValue in zip(*[iter(gameData)]*2):
            #print ('%s: %s' % (attributeName.text, attributeValue.text))
            game[attributeName.text] = attributeValue.text

        gameData = html_soup.select('div#coreGameGenre div div')
        for attributeName, attributeValue in zip(*[iter(gameData)]*2):
            #print ('%s: %s' % (attributeName.text, attributeValue.text))
            game[attributeName.text] = attributeValue.text

        df = df.append(game, ignore_index=True)
        print('Game processed: ' + tittle)
    return df


# In[201]:


pageSize = 25
currentPage = 4565
lastPage = False
baseUrl = 'https://www.mobygames.com/browse/games/offset,%s/so,0a/list-games/'
gameLinks = []

start_time = time.time()

while not lastPage:
    html_soup = DownloadNextPage()
    currentPapeGameLinks,lastPage = GetGameLinks(html_soup)
    print('Add %s links' % (len(currentPapeGameLinks)))   
    gameLinks += currentPapeGameLinks
    currentPage += 1
    
print('Total %s links' % (len(gameLinks)))   

df = GetGamesData(gameLinks)

#df['Platforms'].str.get_dummies(',')
#df[df['Add-on'].notnull()]
#df.isnull().sum()
df.to_csv ('export_dataframe.csv', index = False, header=True)

print("Total time %s seconds" % (time.time() - start_time))

