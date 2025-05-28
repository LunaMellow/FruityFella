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
    #                 Commands                 #
    ############################################

    @commands.command(name="keyboard")
    async def products(self, ctx):
        await ctx.send("Dygma Defy w/Wuque Studio WS Brown's and Keychron PBT Keycaps")

    ############################################
    #                   Debug                  #
    ############################################

    @commands.command(name="mocksub")
    async def mocksub(self, ctx):
        await ctx.send("Mocking a subscription event...")

        payload = \
        {
            "subscription": {
                "type": "channel.subscribe"
            },
            "event": {
                "user_name": "FakeUser123",
                "tier": "1000"
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:8080/eventsub",
                    json=payload
            ) as resp:
                status = resp.status
                await ctx.send(f"Mock sub sent! Server responded with status {status}")

    @commands.command(name="mockprime")
    async def mocksub(self, ctx):
        await ctx.send("Mocking a prime subscription event...")

        payload = \
        {
            "subscription": {
                "type": "channel.subscribe"
            },
            "event": {
                "user_name": "FakeUser123",
                "tier": "1000",
                "is_prime": "true"
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:8080/eventsub",
                    json=payload
            ) as resp:
                status = resp.status
                await ctx.send(f"Mock prime sub sent! Server responded with status {status}")

    @commands.command(name="mockfollow")
    async def mockfollow(self, ctx):
        await ctx.send("Mocking a follow...")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:6969/trigger",
                    json={"reward": "follow"}
            ) as resp:
                await ctx.send(f"Mock follow sent! Status: {resp.status}")

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
                reward = "fbi"
            elif bits >= 25:
                reward = "gold"
            elif bits >= 10:
                reward = "love"

        if reward in ["flashbang", "gold", "fbi", "love", "sub1000", "sub2000", "sub3000", "follow"]:
            await self.push_overlay_event(reward)

        if reward == "flashbang":
            print("[Trigger] Flashbang Triggered")
            await self.flashbang_internal()
        elif reward == "gold":
            print("[Trigger] Gold Triggered")
            await self.gold_internal()
        elif reward == "fbi":
            print("[Trigger] Fbi Triggered")
            await self.fbi_internal()
        elif reward == "love":
            print("[Trigger] Love Triggered")
            await self.love_internal()
        elif reward == "sub1000":
            print("[Trigger] Subscription tier 1 Triggered")
            await self.party_internal()
        elif reward == "sub2000":
            print("[Trigger] Subscription tier 2 Triggered")
            await self.party_internal()
        elif reward == "sub3000":
            print("[Trigger] Subscription tier 3 Triggered")
            await self.party_internal()
        elif reward == "follow":
            print("[Trigger] Follow Triggered")
        else:
            print(f"[Trigger] Unknown reward or cheer amount: {reward_name}, bits={bits}")

    async def flashbang_internal(self):
        asyncio.create_task(play_sound("assets/flash.mp3"))
        previous_scene = await self.hue.get_active_scene()
        await self.hue.flashbang(
            light_ids=[self.play_left_id, self.play_right_id],
            on=True
        )
        await self.hue.restore_scene(previous_scene)

    async def gold_internal(self):
        asyncio.create_task(play_sound("assets/gold.mp3"))
        previous_scene = await self.hue.get_active_scene()
        await self.hue.gold(
            light_ids=[self.play_left_id, self.play_right_id],
            on=True
        )
        await self.hue.restore_scene(previous_scene)

    async def fbi_internal(self):
        asyncio.create_task(play_sound("assets/fbi.mp3"))
        previous_scene = await self.hue.get_active_scene()
        await self.hue.fbi()
        await self.hue.restore_scene(previous_scene)

    async def love_internal(self):
        asyncio.create_task(play_sound("assets/love.mp3"))
        previous_scene = await self.hue.get_active_scene()
        await self.hue.love(
            light_ids=[self.play_left_id, self.play_right_id],
            on=True
        )
        await asyncio.sleep(14)
        await self.hue.restore_scene(previous_scene)

    async def party_internal(self):
        asyncio.create_task(play_sound("assets/pedro.mp3"))
        previous_scene = await self.hue.get_active_scene()

        await self.hue.party_mode()
        await self.hue.restore_scene(previous_scene)

    ############################################
    #                 Functions                #
    ############################################

    async def start_webhook_server(self):
        app = web.Application()

        async def handle_trigger(request):
            data = await request.json()
            reward = data.get("reward")
            bits = data.get("bits")

            print(f"\n[Webhook] Received internal trigger: reward={reward}, bits={bits}")
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
        print("[API] Bot internal API running on http://localhost:6969")

    async def event_ready(self):
        print(f"\n[Twitch] Logging in as {self.nick}"
              f"\n================================================")
        await self.start_webhook_server()

    async def event_message(self, message):
        if not message.author:
            return
        print(f'{message.author.name}: {message.content}')
        await self.handle_commands(message)

if __name__ == "__main__":
    twitchbot = Bot()
    twitchbot.run()