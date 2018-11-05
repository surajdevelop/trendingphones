import urllib.request
from bs4 import BeautifulSoup
import sys
import json

top5Links = []
top5Phones = []
gsm_home_page = 'https://www.gsmarena.com/'


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
        'response': speechlet_response,
        'sessionAttributes': session_attributes
    }


# --------------- Methods to run gsm-arena crawler ----------------------

def getNameOnly(intent, session):
    """ Get Names of top 5 trending phones according to user reviews and votes.
       """
    card_title = "Trending Phones names"
    session_attributes = {}
    should_end_session = False
    soup = get_soup(gsm_home_page)

    top5Links, top5Phones = getTop5Phones(soup)
    speech_output = "Top of Chart is, " + top5Phones[0] + \
                    ". On number two, its " + top5Phones[1] + \
                    ". Number three is " + top5Phones[2] + \
                    ". Number four is " + top5Phones[3] + \
                    ", and on number five, its" + top5Phones[4]

    reprompt_text = "How may I help you?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_soup(link):
    page = urllib.request.urlopen(link)
    soup = BeautifulSoup(page, 'html.parser')
    return soup


def getTop5Phones(soup):
    tt = soup.find('table', attrs={'class': 'module-fit blue'})
    rows = tt.findChildren(['th', 'tr'])

    for row in rows:
        try:
            row_text = row.a.text
            row_link = row.a['href']
        except:
            continue
        if not row_link in top5Links:
            top5Links.append(row_link)
            top5Phones.append(row_text)

    x = top5Links[:5]
    y = top5Phones[:5]
    return (x, y)


def getSpecs(intent, session):
    """ Get details of a particular phone.
           """
    card_title = "Specification of a phone"
    session_attributes = {}
    should_end_session = False
    name = intent['slots']['phone']['value']
    soup = get_soup(gsm_home_page)
    top5Links, top5Phones = getTop5Phones(soup)
    for i in range(len(top5Phones)):
        top5Phones[i] = top5Phones[i].lower()

    if name in top5Phones:
        x = top5Phones.index(name)
        link = top5Links[x]
        phone_page = gsm_home_page + link
        psoup = get_soup(phone_page)
        features = psoup.find('ul', attrs={'class': 'specs-spotlight-features'})
        display_size = get_display_size(features).text
        rear_res = get_rear_camera_res(psoup).text
        selfie_res = get_selfie_camera_res(psoup)
        ram_size = get_ram_size(psoup).text
        internal_storage = get_internal_storage(psoup)
        battery_size = get_battery_size(psoup).text
        speech_output = printAttributes(top5Phones[x], display_size, rear_res, selfie_res, ram_size, internal_storage,
                                        battery_size, phone_page)
    else:
        speech_output = "Sorry, but this phone is not in top five trending smartphones"

    reprompt_text = "Can you repeat the name?"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


#####----------- To send Link to user----------#####
# def getLink(intent, session)
#     """ Get link of a particular phone.
#                """
#     card_title = "Link of a phone"
#     session_attributes = {}
#     should_end_session = True
#     name = intent['slots']['phone']['value']
#     if name in top5Phones:
#         x= top5Phones.index(name)
#         link=top5Links[x]
#         phone_page = gsm_home_page + link
#     else:
#         phone_page='That phone is not in top five'
#     return phone_page


def printAttributes(phone_name, display_size, rear_res, selfie_res, ram_size, internal_storage, battery_size, link):
    output = "The phone is " + phone_name + \
             "Its display size is " + display_size + "inches" + \
             "rear camera resolution is " + rear_res + \
             "front camera resolution is " + selfie_res + \
             "ram size is " + ram_size + "GB" + \
             "internal storage is " + internal_storage + \
             "battery is " + battery_size + "mAh"
    # print(link)
    return output


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