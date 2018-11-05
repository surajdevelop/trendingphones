import urllib.request
from bs4 import BeautifulSoup
import gsm_crawler
import crawler_price
import crawler_brand
import crawler_both
import sys
import json


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

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the World of top trending phones. " \
                    " How may i help you?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I didn't get you, what do you want to know? "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying Amazon Alexa Contest Notify Skills Kit. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def getSuggestion(intent, session):
    """ Want to buy a phone on the basis of filters
        """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Sure,You want to filter on the basis of price or brand or both? "

    reprompt_text = "I didn't get you.You want to filter on the basis of price or brand or both? "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getPrice(intent, session):
    session_attributes = {}
    card_title = ""
    speech_output = "Ok, So Whats your budget?"

    reprompt_text = "I didn't get you.Can you repeat your choice? "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getBrand(intent, session):
    session_attributes = {}
    card_title = ""
    speech_output = "Ok, So phones of which brand?"

    reprompt_text = "I didn't get you.Can you repeat your choice? "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def getBothFilter(intent, session):
    session_attributes = {}
    card_title = ""
    speech_output = "Ok, So Whats your budget and brand?"

    reprompt_text = "I didn't get you.Can you repeat your choice? "
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    #gsm-arena filter result
    if intent_name == "TopPhoneNameIntent":
        return gsm_crawler.getNameOnly(intent, session)

    if intent_name == "SpecIntent":
        return gsm_crawler.getSpecs(intent, session)

    # if intent_name == "LinkIntent":
    #     return getLink(intent, session)
    #

    # #flipkart filter result
    if intent_name == "SuggestIntent":
        return getSuggestion(intent, session)

    if intent_name == "PriceIntent":
        return getPrice(intent, session)

    if intent_name == "FinalPriceIntent":
        return crawler_price.getResultPrice(intent, session)
    #
    if intent_name == "BrandIntent":
        return getBrand(intent, session)
    #
    if intent_name == "FinalBrandIntent":
        return crawler_brand.getResultBrand(intent, session)
    #
    if intent_name == "BothFilterIntent":
        return getBothFilter(intent, session)
    #
    if intent_name == "FinalBothFilterIntent":
        return crawler_both.getResultBothFilter(intent, session)


    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")



def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here





# --------------- Main handler ------------------
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.59695ac9-ce4d-4be9-b0df-3b4aa5247a7a"):
        raise ValueError("Invalid Application ID")

    # if event['session']['new']:
    #     on_session_started({'requestId': event['request']['requestId']},
    #                       event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
