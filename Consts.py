# File: Consts.py
############################################

# Imports
import os

# Class Consts
class Consts:
    ############################################
    #               Credentials                #
    ############################################
    TOKEN = os.environ['TOKEN']
    CLIENT_ID = os.environ['CLIENT_ID']
    INITIAL_CHANNELS = ['Plumhoe']
    PREFIX = '!'

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
    RED_SCENE_ID = os.environ['HUE_RED_SCENE_ID']
    BLUE_SCENE_ID = os.environ['HUE_BLUE_SCENE_ID']
