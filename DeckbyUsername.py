# Imports
import cloudscraper
from bs4 import BeautifulSoup
import random
import time
def findByUsername(username,clan):
    #Lists to append to
    profilelinks = []
    cardslist = []


    # Makes it possible to search for the username
    for letter in username:
        if letter == " ":
            letter = letter.replace(" ","+")

    # Makes the GET request and returns the HTML
    status = 0
    while status != 200:
        scraper = cloudscraper.create_scraper(delay = random.randint(10,100))
        searchresults = scraper.get('https://royaleapi.com/player/search/results?q='+str(username))
        status = searchresults.status_code
    # Parses the HTML to find the usernames
    soup = BeautifulSoup(searchresults.text, "html.parser")
    myheaders = soup.find_all("a", {"class": "header"})
    links = myheaders[2:]
    for link in links:
        profilelinks.append(link.get("href"))

    # Makes the GET request to each profile
    for profile in profilelinks:
        getProfiles = scraper.get("https://royaleapi.com"+str(profile)).text

        # Parses the HTML and checks against the clan
        profilesoup = BeautifulSoup(getProfiles,"html.parser")
        if profilesoup.find(text = clan) != None:
            
            # Finds the deck
            cards = profilesoup.find_all(class_ = "deck_card ui image")
            for card in cards:
                srccards = card["src"]
                splittext = srccards.split('?')
                cardslist.append(splittext[0])
            return cardslist

#Calls the function
print(findByUsername("bob the greater","trade"))
