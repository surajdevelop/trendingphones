import urllib.request
from bs4 import BeautifulSoup
import json
import sys


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Methods to run price crawler ----------------------

def getResultBothFilter(intent, session):
    card_title = "Trending Phones names"
    session_attributes = {}
    should_end_session = False
    prices = ['2000', '4000', '7000', '10000', '13000', '16000', '20000', '25000', '30000', '50000', 'Max']
    price = intent['slots']['phone']['number']['value']
    if price not in prices:
        sys.exit("Price not found in price filter")
    brand_filter = '&p%5B%5D=facets.brand%255B%255D%3D' + intent['slots']['brand']['value']

    flipkart_mobile_url = 'https://www.flipkart.com/mobiles/pr?sid=tyy%2C4io&marketplace=FLIPKART&p%5B%5D=facets.price_range.from%3DMin&p%5B%5D=facets.price_range.to%3D'
    soup = get_soup(flipkart_mobile_url + price + brand_filter)


    top3Phones = getTop3Phones(soup)

    top3names = []

    phone_attributes = []

    for p in top3Phones:
        p_obj = {}
        p_obj['phone_name'] = p
        top3names.append(p_obj['phone_name'])
        phone_attributes.append(p_obj)

    top3Details = getTop3Details(soup, phone_attributes)
    speech_output = "Top results are,  " \
                    + top3names[0] + " With Rating of " + top3Details[0]['rating'] \
                    + " by " + top3Details[0]['num_ratings'] + " Users " \
                                                               ",Its price is " + top3Details[0]['price'] \
                    + " Want to buy it, or want to know its specifications? You can have the link" \
                      " Another one is  " \
                    + top3names[1] + "With Rating of" + top3Details[1]['rating'] \
                    + " by " + top3Details[1]['num_ratings'] + "Users " \
                                                               ",Its price is" + top3Details[1]['price']
    reprompt_text = "I didn't get it, Can you repeat whats your budget and brand?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



def getTop3Phones(soup):
	top3Phones = []
	divs = soup.find('div', attrs={'class': '_1HmYoV _35HD7C col-10-12'})
	for div in divs:
		div = div.find('div', attrs={'class': '_3wU53n'})
		if (div is not None):
			top3Phones.append(div.text)
	return top3Phones[:3]


def getTop3Details(soup, phone_attributes):
    divs = soup.find('div', attrs={'class': '_1HmYoV _35HD7C col-10-12'})
    for idx, div in enumerate(divs):
        if (div is not None):
            rating = div.find('div', attrs={'class': 'hGSR34 _2beYZw'})
            if rating is not None and idx < 4:
                rating_split = rating.text.split(" ")
                phone_attributes[idx - 1]['rating'] = rating_split[0]

            num_ratings_reviews = div.find('span', attrs={'class': '_38sUEc'})
            if num_ratings_reviews is not None and idx < 4:
                num_ratings_reviews_split = num_ratings_reviews.text.split("&")
                num_rating_split = num_ratings_reviews_split[0].split("R")
                num_review_split = num_ratings_reviews_split[1].split("R")
                phone_attributes[idx - 1]['num_ratings'] = num_rating_split[0]
                phone_attributes[idx - 1]['num_reviews'] = num_review_split[0]

            price = div.find('div', attrs={'class': '_1vC4OE _2rQ-NK'})
            if price is not None and idx < 4:
                price_split = price.text
                price_split = price_split[1:len(price_split)]
                phone_attributes[idx - 1]['price'] = price_split

            for ultag in div.find_all('ul', attrs={'class': 'vFw0gD'}):
                tags = ultag.find_all('li')
                if idx < 4:
                    phone_attributes[idx - 1]['specs'] = ""
                    for tag in tags:
                        phone_attributes[idx - 1]['specs'] += tag.text

            link = div.find('a', attrs={'class': '_31qSD5'})
            if link is not None and idx < 4:
                phone_attributes[idx - 1]['link'] = 'https://www.flipkart.com' + link['href']

    return phone_attributes

def getPhoneFromDiv(div):
	return(div.find('div', attrs={'class': 'hGSR34 _2beYZw'}).text)

def get_soup(link):
	page = urllib.request.urlopen(link)
	soup = BeautifulSoup(page, 'html.parser')
	return soup

def get_selfie_camera_res(soup):
	selfie = soup.find('td', attrs={'data-spec': 'cam2modules'}).text
	# For future reference, data structure:
	# [20 MP, f/2.2, 1/2.8", 1.0um]
	return selfie.split(', ')[0]

def get_internal_storage(soup):
	internal_storage = soup.find('td', attrs={'data-spec': 'internalmemory'}).text
	return internal_storage.split(', ')[0]

def get_rear_camera_res(features):
	return features.find('span', attrs={'data-spec': 'camerapixels-hl'})

def get_ram_size(features):
	return features.find('span', attrs={'data-spec': 'ramsize-hl'})

def get_display_size(features):
	return features.find('span', attrs={'data-spec': 'displaysize-hl'})

def get_battery_size(features):
	return features.find('span', attrs={'data-spec': 'batsize-hl'})
