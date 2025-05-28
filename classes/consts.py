# File: consts.py
############################################

# Imports
import os


# Class Consts
class Consts:
    ############################################
    #               Credentials                #
    ############################################
    # Use get() method with defaults for missing environment variables
    TOKEN = os.environ.get('TWITCH_TOKEN', '')
    SECRET = os.environ.get('TWITCH_SECRET', '')
    CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID', '')
    INITIAL_CHANNELS = ['Plumhoe']
    PREFIX = '!'

    # Secrets
    ACCESS_TOKEN = os.environ.get('TWITCH_ACCESS_TOKEN', '')
    BROADCASTER_ID = os.environ.get('TWITCH_BROADCASTER_ID', '')
    CALLBACK_URL = os.environ.get('TWITCH_CALLBACK_URL', '')

    # HUE API Login
    BASE_URL = os.environ.get('HUE_BASE_URL', '')
    HUE_APP_KEY = os.environ.get('HUE_APP_KEY', '')

    ############################################
    #               Identifiers                #
    ############################################
    GROUP_ID = os.environ.get('HUE_GROUP_ID', '')
    PLAY_LEFT_ID = os.environ.get('HUE_PLAY_LEFT_ID', '')
    PLAY_RIGHT_ID = os.environ.get('HUE_PLAY_RIGHT_ID', '')

    ############################################
    #                  Scenes                  #
    ############################################

    # Collected RED
    RED_SCENE_ID = os.environ.get('HUE_RED_SCENE_ID', '')

    # Collected GREEN
    GREEN_SCENE_ID = os.environ.get('HUE_GREEN_SCENE_ID', '')

    # Collected BLUE
    BLUE_SCENE_ID = os.environ.get('HUE_BLUE_SCENE_ID', '')

    # Individual RED
    RED_RIGHT_SCENE_ID = os.environ.get('HUE_RED_RIGHT_SCENE_ID', '')
    RED_LEFT_SCENE_ID = os.environ.get('HUE_RED_LEFT_SCENE_ID', '')

    # Individual GREEN
    GREEN_RIGHT_SCENE_ID = os.environ.get('HUE_GREEN_RIGHT_SCENE_ID', '')
    GREEN_LEFT_SCENE_ID = os.environ.get('HUE_GREEN_LEFT_SCENE_ID', '')

    # Individual BLUE
    BLUE_RIGHT_SCENE_ID = os.environ.get('HUE_BLUE_RIGHT_SCENE_ID', '')
    BLUE_LEFT_SCENE_ID = os.environ.get('HUE_BLUE_LEFT_SCENE_ID', '')

    ############################################
    #                   Paths                  #
    ############################################
    OVERLAY_PATH = "browsersource/overlay.html"

    @classmethod
    def validate_environment(cls):
        """Check if required environment variables are set"""
        required_vars = [
            'TWITCH_TOKEN', 'TWITCH_SECRET', 'TWITCH_CLIENT_ID',
            'TWITCH_ACCESS_TOKEN', 'TWITCH_BROADCASTER_ID', 'TWITCH_CALLBACK_URL'
        ]

        missing_vars = [var for var in required_vars if not os.environ.get(var)]

        if missing_vars:
            print("WARNING: The following required environment variables are missing:")
            for var in missing_vars:
                print(f"  - {var}")
            print("Some functionality may not work correctly.")
