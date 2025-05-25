# File: main.py
############################################

# Imports
import asyncio

import aiohttp
from aiohttp import web
from twitchio.ext import commands
from utils.util import play_sound, send_fake_event
from classes.hue_client import HueClient
from classes.consts import Consts

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

    ############################################
    #                  Triggers                #
    ############################################

    async def trigger_reward(self, reward_name: str):
        if reward_name.lower() == "flashbang":
            await self.flashbang_internal()
        elif reward_name.lower() == "gold":
            await self.gold_internal()
        elif reward_name.lower() == "fbi":
            await self.fbi_internal()

    async def flashbang_internal(self):
        print("[Trigger] Flashbang")
        asyncio.create_task(play_sound("assets/flash.mp3"))
        previous_scene = await self.hue.get_active_scene()
        await self.hue.flashbang(
            light_ids=[self.play_left_id, self.play_right_id],
            on=True
        )
        await self.hue.restore_scene(previous_scene)

    async def gold_internal(self):
        print("[Trigger] Gold")
        asyncio.create_task(play_sound("assets/gold.mp3"))
        previous_scene = await self.hue.get_active_scene()
        await self.hue.gold(
            light_ids=[self.play_left_id, self.play_right_id],
            on=True
        )
        await self.hue.restore_scene(previous_scene)

    async def fbi_internal(self):
        print("[Trigger] FBI")
        asyncio.create_task(play_sound("assets/fbi.mp3"))
        previous_scene = await self.hue.get_active_scene()
        await self.hue.fbi(
            red_scene_id=self.red_scene_id,
            blue_scene_id=self.blue_scene_id
        )
        await self.hue.restore_scene(previous_scene)

    ############################################
    #                   Debug                  #
    ############################################

    @commands.command(name="mocksub")
    async def mocksub(self, ctx):
        await ctx.send("Mocking a subscription event...")

        payload = {
            "subscription": {
                "type": "channel.subscribe"
            },
            "event": {
                "user_name": "FakeUser123"
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:8080/eventsub",
                    json=payload
            ) as resp:
                status = resp.status
                await ctx.send(f"Mock sub sent! Server responded with status {status}")

    @commands.command(name="mockcheer")
    async def mockcheer(self, ctx):
        await ctx.send("Mocking a cheer event...")

        status = await send_fake_event("channel.cheer", {
            "user_name": "CheeryLuna",
            "bits": 100
        })

        await ctx.send(f"Mock cheer sent! Server responded with status {status}")

    @commands.command(name="mockredemption")
    async def mockredemption(self, ctx):
        parts = ctx.message.content.split(" ", 1)
        if len(parts) != 2:
            await ctx.send("Usage: !mockredemption <Reward Name>")
            return

        reward_name = parts[1]
        await ctx.send(f"Mocking redemption: {reward_name}")

        status = await send_fake_event("channel.channel_points_custom_reward_redemption.add", {
            "reward": {
                "title": reward_name
            }
        })

        await ctx.send(f"Mock redemption sent! Server responded with status {status}")


    ############################################
    #                 Functions                #
    ############################################

    async def start_webhook_server(self):
        app = web.Application()

        async def handle_trigger(request):
            data = await request.json()
            reward = data.get("reward")
            print(f"Received internal reward trigger: {reward}")
            await self.trigger_reward(reward)
            return web.Response(text="ok")

        app.router.add_post("/trigger", handle_trigger)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 6969)
        await site.start()
        print("Bot internal API running on http://localhost:6969")

    async def event_ready(self):
        print(f"Logging in as {self.nick}\n-----------------------------")
        await self.start_webhook_server()

    async def event_message(self, message):
        if not message.author:
            return
        print(f'{message.author.name}: {message.content}')
        await self.handle_commands(message)

if __name__ == "__main__":
    twitchbot = Bot()
    twitchbot.run()