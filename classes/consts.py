# File: consts.py
############################################

# Imports
import os

# Class Consts
class Consts:
    ############################################
    #               Credentials                #
    ############################################
    TOKEN = os.environ['TWITCH_TOKEN']
    SECRET = os.environ['TWITCH_SECRET']
    CLIENT_ID = os.environ['TWITCH_CLIENT_ID']
    INITIAL_CHANNELS = ['Plumhoe']
    PREFIX = '!'

    # Secrets
    ACCESS_TOKEN = os.environ['TWITCH_ACCESS_TOKEN']
    BROADCASTER_ID = os.environ['TWITCH_BROADCASTER_ID']
    CALLBACK_URL = os.environ['TWITCH_CALLBACK_URL']

    # HUE API Login
    BASE_URL = os.environ['HUE_BASE_URL']
    HUE_APP_KEY = os.environ['HUE_APP_KEY']

    ############################################
    #               Identifiers                #
    ############################################
    GROUP_ID = os.environ['HUE_GROUP_ID']
    PLAY_LEFT_ID = os.environ['HUE_PLAY_LEFT_ID']
    PLAY_RIGHT_ID = os.environ['HUE_PLAY_RIGHT_ID']

    ############################################
    #                  Scenes                  #
    ############################################

    # Collected RED
    RED_SCENE_ID = os.environ['HUE_RED_SCENE_ID']

    # Collected GREEN
    GREEN_SCENE_ID = os.environ['HUE_GREEN_SCENE_ID']

    # Collected BLUE
    BLUE_SCENE_ID = os.environ['HUE_BLUE_SCENE_ID']

    # Individual RED
    RED_RIGHT_SCENE_ID = os.environ['HUE_RED_RIGHT_SCENE_ID']
    RED_LEFT_SCENE_ID = os.environ['HUE_RED_LEFT_SCENE_ID']

    # Individual GREEN
    GREEN_RIGHT_SCENE_ID = os.environ['HUE_GREEN_RIGHT_SCENE_ID']
    GREEN_LEFT_SCENE_ID = os.environ['HUE_GREEN_LEFT_SCENE_ID']

    # Individual BLUE
    BLUE_RIGHT_SCENE_ID = os.environ['HUE_BLUE_RIGHT_SCENE_ID']
    BLUE_LEFT_SCENE_ID = os.environ['HUE_BLUE_LEFT_SCENE_ID']

    ############################################
    #                   Paths                  #
    ############################################
    OVERLAY_PATH = "browsersource/overlay.html"