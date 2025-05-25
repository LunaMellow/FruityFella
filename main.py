# File: main.py
############################################

# Imports
import asyncio
from twitchio.ext import commands
from utils.Util import play_sound
from classes.HueClient import HueClient
from classes.Consts import Consts

class Bot(commands.Bot):
    def __init__(self):

        ############################################
        #               Credentials                #
        ############################################
        super().__init__(
            token = Consts.TOKEN,
            client_id = Consts.CLIENT_ID,
            prefix = Consts.PREFIX,
            initial_channels = Consts.INITIAL_CHANNELS
        )
        self.hue = HueClient(
            base_url = Consts.BASE_URL,
            hue_app_key = Consts.HUE_APP_KEY
        )

        ############################################
        #               Identifiers                #
        ############################################
        self.group_id = Consts.GROUP_ID
        self.play_left_id = Consts.PLAY_LEFT_ID
        self.play_right_id = Consts.PLAY_RIGHT_ID

        ############################################
        #                  Scenes                  #
        ############################################
        self.red_scene_id = Consts.RED_SCENE_ID
        self.blue_scene_id = Consts.BLUE_SCENE_ID


    ############################################
    #                 Commands                 #
    ############################################

    # FLASHBANG OUT!
    @commands.command(name="flashbang")
    async def flashbang(self, ctx):
        await ctx.send("FLASHBANG OUT!")
        asyncio.create_task(play_sound("assets/flash.mp3"))

        previous_scene = await self.hue.get_active_scene()
        await self.hue.flashbang(
            light_ids=[self.play_left_id, self.play_right_id],
            on=True
        )
        await self.hue.restore_scene(previous_scene)

    # GOLD GOLD GOLD
    @commands.command(name="gold")
    async def gold(self, ctx):
        await ctx.send("GOLD GOLD GOLD")
        asyncio.create_task(play_sound("assets/gold.mp3"))

        previous_scene = await self.hue.get_active_scene()
        await self.hue.gold(
            light_ids=[self.play_left_id, self.play_right_id],
            on=True
        )
        await self.hue.restore_scene(previous_scene)

    # FBI OPEN UP!
    @commands.command(name="fbi")
    async def fbi(self, ctx):
        await ctx.send("FBI OPEN UP!")
        asyncio.create_task(play_sound("assets/fbi.mp3"))

        previous_scene = await self.hue.get_active_scene()
        await self.hue.fbi(
            red_scene_id=self.red_scene_id,
            blue_scene_id=self.blue_scene_id
        )
        await self.hue.restore_scene(previous_scene)

    async def event_ready(self):
        print(f"Logging in as {self.nick}\n"
              f"-----------------------------")

    async def event_message(self, message):
        if not message.author:
            return
        print(f'{message.author.name}: {message.content}')
        await self.handle_commands(message)

if __name__ == "__main__":
    twitchbot = Bot()
    twitchbot.run()