# File: hue_client.py
############################################

# Imports
import aiohttp
import asyncio

# Class HueClient
class HueClient:
    def __init__(self, base_url: str, hue_app_key: str):
        self.base_url = base_url
        self.hue_app_key = hue_app_key
        self.headers = {
            'hue-application-key': self.hue_app_key,
            'Content-Type': 'application/json'
        }

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
            await self.trigger_scene(scene_id)

    async def set_all(self, session, light_ids, payload):
        return await asyncio.gather(*[
            session.put(
                f"{self.base_url}/light/{lid}",
                headers=self.headers,
                json=payload,
                ssl=False
            ) for lid in light_ids
        ])

    async def trigger_scene(self, scene_id: str):
        async with aiohttp.ClientSession() as session:
            payload = {
                "recall": {
                    "action": "active"
                }
            }
            async with session.put(
                    f"{self.base_url}/scene/{scene_id}",
                    headers=self.headers,
                    json=payload,
                    ssl=False
            ) as resp:
                if resp.status != 200:
                    print(await resp.text())

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
            await self.set_all(session, light_ids, {
                "on": {"on": True},
                "dimming": {"brightness": 25},
                "color_temperature": {"mirek": 400}
            })

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
            await self.set_all(session, light_ids, {
                "on": {"on": True},
                "dimming": {"brightness": 25},
                "color_temperature": {"mirek": 400}
            })

    async def fbi(self, red_scene_id: str, blue_scene_id: str, loop_count: int = 6):
        await asyncio.sleep(1)
        for _ in range(loop_count):
            await self.trigger_scene(blue_scene_id)
            await asyncio.sleep(0.6)
            await self.trigger_scene(red_scene_id)
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