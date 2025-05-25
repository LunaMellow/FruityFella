# File: Util.py
############################################

# Imports
import asyncio
from playsound import playsound

# Play sounds
async def play_sound(filename):
    await asyncio.to_thread(playsound, filename)