import logging
#import requests
#import six
#import random

#from ask_sdk_core.skill_builder import SkillBuilder
#from ask_sdk_core.handler_input import HandlerInput
#from ask_sdk_core.dispatch_components import (
#    AbstractRequestHandler, AbstractExceptionHandler,
#    AbstractResponseInterceptor, AbstractRequestInterceptor)
#from ask_sdk_core.utils import is_intent_name, is_request_type
#
##from typing import Union, Dict, Any, List
#from ask_sdk_model.dialog import (
#    ElicitSlotDirective, DelegateDirective)
#from ask_sdk_model import (
#    Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot)
#from ask_sdk_model.slu.entityresolution import StatusCode
#
#logger = logging.getLogger(__name__)
#logger.setLevel(logging.INFO)

import trails

##############################
# Builders
##############################


def build_PlainSpeech(body):
    speech = {}
    speech['type'] = 'PlainText'
    speech['text'] = body
    return speech


def build_response(message, session_attributes={}):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response


def build_SimpleCard(title, body):
    card = {}
    card['type'] = 'Simple'
    card['title'] = title
    card['content'] = body
    return card


##############################
# Responses
##############################


def conversation(title, body, session_attributes):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = False
    return build_response(speechlet, session_attributes=session_attributes)


def statement(title, body):
    speechlet = {}
    speechlet['outputSpeech'] = build_PlainSpeech(body)
    speechlet['card'] = build_SimpleCard(title, body)
    speechlet['shouldEndSession'] = True
    return build_response(speechlet)


def continue_dialog():
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return build_response(message)


##############################
# Custom Intents
##############################


def sing_intent(event, context):
    song = "Daisy, Daisy. Give me your answer, do. I'm half crazy all for the love of you"
    return statement("daisy_bell_intent", song)


def counter_intent(event, context):
    session_attributes = event['session']['attributes']

    if "counter" in session_attributes:
        session_attributes['counter'] += 1

    else:
        session_attributes['counter'] = 1

    return conversation("counter_intent", session_attributes['counter'],
                        session_attributes)


def trip_intent(event, context):
    dialog_state = event['request']['dialogState']

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog()

    elif dialog_state == "COMPLETED":
        return statement("trip_intent", "Have a good trip")

    else:
        return statement("trip_intent", "No dialog")


##############################
# Required Intents
##############################


def cancel_intent():
    return statement("CancelIntent", "You want to cancel")	#don't use CancelIntent as title it causes code reference error during certification 

def help_intent():
    return statement("CancelIntent", "You want help")		#same here don't use CancelIntent

def stop_intent():
    return statement("StopIntent", "You want to stop")		#here also don't use StopIntent


##############################
# On Launch
##############################

def on_launch(event, context):
    t = trails.Trails()
    return statement("Trail Status", t.summary())

##############################
# Routing
##############################


def intent_router(event, context):
    intent = event['request']['intent']['name']

    # Custom Intents

    if intent == "OpenIntent":
        t = trails.Trails()
        return statement("Open Trails", t.summary("open"))

    if intent == "ClosedIntent":
        t = trails.Trails()
        return statement("Open Trails", t.summary("closed"))
    
    # Required Intents

    if intent == "AMAZON.CancelIntent":
        return cancel_intent()

    if intent == "AMAZON.HelpIntent":
        return help_intent()

    if intent == "AMAZON.StopIntent":
        return stop_intent()


##############################
# Program Entry
##############################


def lambda_handler(event, context):
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event, context)

    elif event['request']['type'] == "IntentRequest":
        return intent_router(event, context)
