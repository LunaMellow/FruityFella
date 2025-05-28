# File: hue_client.py
############################################

# Imports
import aiohttp
import asyncio
import random
from classes.consts import Consts
from datetime import datetime

# Class HueClient
class HueClient:
    def __init__(self, base_url: str, hue_app_key: str):
        self.base_url = base_url
        self.hue_app_key = hue_app_key

        # Collected scenes
        self.red_scene_id = Consts.RED_SCENE_ID
        self.green_scene_id = Consts.GREEN_SCENE_ID
        self.blue_scene_id = Consts.BLUE_SCENE_ID

        self.collected_scenes = [
            {"id": self.red_scene_id, "name": "Red"},
            {"id": self.green_scene_id, "name": "Green"},
            {"id": self.blue_scene_id, "name": "Blue"}
        ]

        # Individual scenes (if needed in future)
        self.red_scene_left_id = Consts.RED_LEFT_SCENE_ID
        self.red_scene_right_id = Consts.RED_RIGHT_SCENE_ID
        self.green_scene_left_id = Consts.GREEN_LEFT_SCENE_ID
        self.green_scene_right_id = Consts.GREEN_RIGHT_SCENE_ID
        self.blue_scene_left_id = Consts.BLUE_LEFT_SCENE_ID
        self.blue_scene_right_id = Consts.BLUE_RIGHT_SCENE_ID

        self.headers = {
            'hue-application-key': self.hue_app_key,
            'Content-Type': 'application/json'
        }

        self.DEFAULT_RESTORE_STATE = {
            "on": {"on": True},
            "dimming": {"brightness": 25},
            "color_temperature": {"mirek": 400}
        }

    async def _trigger_scene(self, scene_id: str, session: aiohttp.ClientSession | None = None):
        payload = {"recall": {"action": "active"}}
        if session:
            response = await session.put(
                f"{self.base_url}/scene/{scene_id}",
                headers=self.headers,
                json=payload,
                ssl=False
            )
            if response.status != 200:
                print(await response.text())
        else:
            async with aiohttp.ClientSession() as local_session:
                response = await local_session.put(
                    f"{self.base_url}/scene/{scene_id}",
                    headers=self.headers,
                    json=payload,
                    ssl=False
                )
                if response.status != 200:
                    print(await response.text())

    async def get_active_scene(self) -> str | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/scene", headers=self.headers, ssl=False) as resp:
                data = await resp.json()
                for scene in data.get("data", []):
                    if scene.get("status", {}).get("active") not in ["inactive", None]:
                        return scene.get("id")
        return None

    async def restore_scene(self, scene_id: str | None):
        if scene_id:
            async with aiohttp.ClientSession() as session:
                await self._trigger_scene(scene_id, session)

    async def set_all(self, session: aiohttp.ClientSession, light_ids: list[str], payload: dict) -> list:
        return await asyncio.gather(*[
            session.put(
                f"{self.base_url}/light/{lid}",
                headers=self.headers,
                json=payload,
                ssl=False
            ) for lid in light_ids
        ])

    async def flashbang(self, light_ids: list[str], on: bool, loop_count: int = 1):
        async with aiohttp.ClientSession() as session:
            bright = {
                "on": {"on": on},
                "dimming": {"brightness": 100},
                "color_temperature": {"mirek": 153}
            }
            for _ in range(loop_count):
                await self.set_all(session, light_ids, bright)
                await asyncio.sleep(4)
            await self.set_all(session, light_ids, self.DEFAULT_RESTORE_STATE)

    async def gold(self, light_ids: list[str], on: bool, loop_count: int = 13):
        async with aiohttp.ClientSession() as session:
            bright = {
                "on": {"on": on},
                "dimming": {"brightness": 100},
                "color_temperature": {"mirek": 500}
            }
            dim = {
                "on": {"on": on},
                "dimming": {"brightness": 0},
                "color_temperature": {"mirek": 500}
            }
            for _ in range(loop_count):
                await self.set_all(session, light_ids, bright)
                await asyncio.sleep(0.25)
                await self.set_all(session, light_ids, dim)
                await asyncio.sleep(0.25)
            await self.set_all(session, light_ids, self.DEFAULT_RESTORE_STATE)

    async def fbi(self, loop_count: int = 6):
        await asyncio.sleep(1)
        async with aiohttp.ClientSession() as session:
            for _ in range(loop_count):
                await self._trigger_scene(self.blue_scene_id, session)
                await asyncio.sleep(0.6)
                await self._trigger_scene(self.red_scene_id, session)
                await asyncio.sleep(0.6)

    async def love(self, light_ids: list[str], on: bool = True):
        async with aiohttp.ClientSession() as session:
            payload = {
                "on": {"on": on},
                "dimming": {"brightness": 100},
                "color": {
                    "xy": {
                        "x": 0.5,
                        "y": 0.3
                    }
                }
            }
            await self.set_all(session, light_ids, payload)

    async def party_mode(self, loop_count: int = 24):
        last_scene_id = None
        async with aiohttp.ClientSession() as session:
            for _ in range(loop_count):
                start = datetime.now()

                for _ in range(10):
                    scene = random.choice(self.collected_scenes)
                    if scene["id"] != last_scene_id:
                        break

                last_scene_id = scene["id"]

                # print(f"[{now}] [Party Mode] Scene: {scene['name']}")

                await self._trigger_scene(scene["id"], session)

                elapsed = (datetime.now() - start).total_seconds()
                delay = max(0, 0.5 - elapsed)
                await asyncio.sleep(delay)