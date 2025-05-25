# File: main.py
############################################

# Imports
import os
import json
import asyncio
from typing import Any, Coroutine

import aiohttp
from aiohttp import web
from twitchio.ext import commands
from utils.util import play_sound, send_fake_event
from classes.hue_client import HueClient
from classes.consts import Consts

class Bot(commands.Bot):

    clients = []

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

    # Sax mode activated
    @commands.command(name="love")
    async def love(self, ctx):
        await ctx.send("Sax mode activated 💘")
        await self.love_internal()

    ############################################
    #                  Triggers                #
    ############################################

    async def push_overlay_event(self, reward: str):
        data = f"data: {json.dumps({'reward': reward})}\n\n"
        for client in list(self.clients):
            try:
                await client.write(data.encode("utf-8"))
            except Exception:
                self.clients.remove(client)

    async def trigger_reward(self, reward_name: str | None = None, bits: int | None = None):
        reward = None

        if reward_name:
            reward = reward_name.lower().strip()

        elif bits is not None:
            if bits >= 100:
                reward = "flashbang"
            elif bits >= 50:
                reward = "love"
            elif bits >= 25:
                reward = "gold"
            elif bits >= 10:
                reward = "fbi"

        if reward in ["flashbang", "gold", "fbi", "love"]:
            await self.push_overlay_event(reward)

        if reward == "flashbang":
            await self.flashbang_internal()
        elif reward == "gold":
            await self.gold_internal()
        elif reward == "fbi":
            await self.fbi_internal()
        elif reward == "love":
            await self.love_internal()
        else:
            print(f"[Trigger] Unknown reward or cheer amount: {reward_name}, bits={bits}")

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

    async def love_internal(self):
        print("[Trigger] Love")
        asyncio.create_task(play_sound("assets/love.mp3"))
        previous_scene = await self.hue.get_active_scene()
        await self.hue.love(
            light_ids=[self.play_left_id, self.play_right_id],
            on=True
        )
        await asyncio.sleep(14)
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
        bits = 10
        await ctx.send(f"Mocking a cheer of {bits} bits...")

        status = await send_fake_event("channel.cheer", {
            "user_name": "CheeryLuna",
            "bits": bits
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
            bits = data.get("bits")

            print(f"Received internal trigger: reward={reward}, bits={bits}")
            await self.trigger_reward(reward_name=reward, bits=bits)
            return web.Response(text="ok")

        async def handle_overlay(request):
            return web.FileResponse(Consts.OVERLAY_PATH)

        async def overlay_events(request):
            response = web.StreamResponse(
                status=200,
                reason='OK',
                headers={
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                }
            )
            await response.prepare(request)
            self.clients.append(response)

            try:
                while True:
                    await asyncio.sleep(10)
            except asyncio.CancelledError:
                self.clients.remove(response)

        # ✅ Register routes first — before starting the server
        app.router.add_post("/trigger", handle_trigger)
        app.router.add_get("/overlay", handle_overlay)
        app.router.add_get("/overlay-events", overlay_events)

        # ✅ Start server after all routes are registered
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 6969)
        await site.start()
        print("Bot internal API running on http://localhost:6969")

    async def event_ready(self):
        print(f"Logging in as {self.nick}"
              f"\n-----------------------------")
        await self.start_webhook_server()

    async def event_message(self, message):
        if not message.author:
            return
        print(f'{message.author.name}: {message.content}')
        await self.handle_commands(message)

if __name__ == "__main__":
    twitchbot = Bot()
    twitchbot.run()