import requests
from PIL import Image




def returnCard(link):
    cardByteForm = requests.get(link, stream=True).raw
    img = Image.open(cardByteForm)
    return img


def create_image(cardList):
    #cardList is a list of links to the images
    for x in range(len(cardList)):
        newCard = returnCard(cardList[x])
        cardList[x] = newCard
    totalWidth = 0
    for card in cardList:
        totalWidth += card.width
    dst = Image.new('RGB', (totalWidth, cardList[0].height))
    index = 0
    for x in range(0,totalWidth, int(totalWidth / len(cardList))):
        dst.paste(cardList[index], (x, 0))
        index += 1
    dst.show()

