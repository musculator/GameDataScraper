from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import time
import os


#Global variables
outdir = './partialdata'
baseUrl = 'https://www.mobygames.com/browse/games/offset,%s/so,0a/list-games/'
pageSize = 25
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}


#Function that downloads a url
def DownloadWebPage(url):       
    print('Downloading: ' + url)
    time.sleep(1)
    response = get(url, headers=headers)
    return BeautifulSoup(response.text, 'html.parser')

#Function that downloads the specified page number
def DownloadNextPage(currentPage):       
    nextUrl = baseUrl % (currentPage * pageSize)
    return DownloadWebPage(nextUrl)

#Function that gets all the game links from an html
def GetGameLinks(html_soup):
    currentPapeGameLinks = []
    gamesLinks = html_soup.select('table#mof_object_list tbody tr td:first-child a')
    lastPage = len(gamesLinks) < pageSize

    for gameLink in gamesLinks:
        currentPapeGameLinks.append(gameLink['href'])
    return currentPapeGameLinks, lastPage

#Function that gets the data of the games from a list of pages
def GetGamesData(gameLinks):
    df = pd.DataFrame()
    for gameLink in gameLinks:    
        html_soup = DownloadWebPage(gameLink)
        try:
            tittle = html_soup.find('h1', class_='niceHeaderTitle').a.text
            game = {'GameTittle': tittle}

            gameData = html_soup.select('div#coreGameRelease div')
            for attributeName, attributeValue in zip(*[iter(gameData)]*2):
                game[attributeName.text] = attributeValue.text

            gameData = html_soup.select('div#coreGameGenre div div')
            for attributeName, attributeValue in zip(*[iter(gameData)]*2):
                game[attributeName.text] = attributeValue.text
            df = df.append(game, ignore_index=True)
        except:
            game = {'GameTittle': ''}
            df = df.append(game, ignore_index=True)
        print('Game processed: ' + tittle)
    return df

#Function that unifies all temporary files in a single csv
def JoinFiles():
    df = pd.DataFrame()
    files = os.listdir(outdir)
    for file in files:
        dftmp = pd.read_csv(os.path.join(outdir,file))
        df = df.append(dftmp, ignore_index=True)
    df.to_csv ('export_dataframe.csv', index = False, header=True)   
    
#Main function that downloads the game data from the mobygames page, 
#indicating the initial page, and the number of pages it will store in each temporary file
def GameScrapping(maxPagesInFile = 50, currentPage = 0):    
    pagesInFile = 0
    gameLinks = []
    lastPage = False
    
    start_time = time.time()
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    while not lastPage:        
        html_soup = DownloadNextPage(currentPage)
        currentPapeGameLinks,lastPage = GetGameLinks(html_soup)
        print('Add %s links' % (len(currentPapeGameLinks)))   
        gameLinks += currentPapeGameLinks
        pagesInFile += 1
        if pagesInFile == maxPagesInFile:
            print('Total %s links' % (len(gameLinks)))   
            df = GetGamesData(gameLinks)
            df.to_csv ('%s\export_dataframe_%s.csv' % (outdir,currentPage), index = False, header=True)        
            pagesInFile = 0
            gameLinks = []
            lastPage=True
        currentPage += 1

    print('Total %s links' % (len(gameLinks)))   
    if len(gameLinks) > 0:
        df = GetGamesData(gameLinks)    
        df.to_csv ('%s\export_dataframe_%s.csv' % (outdir,currentPage), index = False, header=True)   

    JoinFiles()

    print("Total time %s seconds" % (time.time() - start_time))


#Download all games starting from page 0 and saving 50 pages in each file
GameScrapping(maxPagesInFile = 1, currentPage = 0)