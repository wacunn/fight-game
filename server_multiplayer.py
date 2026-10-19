#!/usr/bin/env python3
"""
Fists of Doom: Toronto — High-Performance Multiplayer WebSocket & HTTP Server
Supports simultaneous real-time WebSockets and HTTP static file serving on a single port.
Runs locally or on free cloud hosts (Render.com, Fly.io, Railway, etc.)
"""
import asyncio
import json
import mimetypes
import os
import sys
import time
from pathlib import Path

try:
    import websockets
    from websockets.asyncio.server import serve
    from websockets.datastructures import Headers
    from websockets.http11 import Response
except ImportError:
    print("Error: 'websockets' library is required. Install with: pip install websockets")
    sys.exit(1)

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = Path(__file__).resolve().parent

# Color palette for players
PLAYER_COLORS = [
    0xef4444,  # Red (P1 / Host)
    0x00f0ff,  # Cyan
    0xf59e0b,  # Amber / Gold
    0x10b981,  # Emerald Green
    0xc026d3,  # Purple
    0xf43f5e,  # Rose
    0x38bdf8,  # Sky Blue
    0xffffff   # White
]

class GameServer:
    def __init__(self):
        # rooms: room_name -> { player_id: { 'ws': websocket, 'info': {...} } }
        self.rooms = {}
        self.next_player_num = 1

    def get_static_response(self, path_str):
        clean_path = path_str.split('?')[0].strip('/')
        if not clean_path or clean_path == '':
            clean_path = 'play.html'

        file_path = (BASE_DIR / clean_path).resolve()
        # Security: prevent directory traversal outside BASE_DIR
        if not str(file_path).startswith(str(BASE_DIR)) or not file_path.exists() or not file_path.is_file():
            return Response(404, 'Not Found', Headers([
                ('Content-Type', 'text/plain'),
                ('Access-Control-Allow-Origin', '*')
            ]), b'404 Not Found')

        mime, _ = mimetypes.guess_type(str(file_path))
        if not mime:
            if file_path.suffix == '.js':
                mime = 'application/javascript'
            elif file_path.suffix == '.css':
                mime = 'text/css'
            else:
                mime = 'application/octet-stream'

        try:
            content = file_path.read_bytes()
            headers = Headers([
                ('Content-Type', mime),
                ('Content-Length', str(len(content))),
                ('Access-Control-Allow-Origin', '*'),
                ('Cache-Control', 'no-cache, must-revalidate')
            ])
            return Response(200, 'OK', headers, content)
        except Exception as e:
            return Response(500, 'Server Error', Headers([('Content-Type', 'text/plain')]), str(e).encode('utf-8'))

    async def process_http_request(self, connection, request):
        # If it's a WebSocket upgrade request, return None to continue handshake
        upgrade = request.headers.get("Upgrade", "")
        if upgrade.lower() == "websocket":
            return None

        # Health check endpoint for cloud hosting monitoring
        if request.path in ('/health', '/ping'):
            return Response(200, 'OK', Headers([
                ('Content-Type', 'text/plain'),
                ('Access-Control-Allow-Origin', '*')
            ]), b'pong')

        # Static files
        return self.get_static_response(request.path)

    async def broadcast_to_room(self, room_name, message_str, exclude_ws=None):
        if room_name not in self.rooms:
            return
        dead_ids = []
        for pid, pdata in self.rooms[room_name].items():
            ws = pdata['ws']
            if ws == exclude_ws:
                continue
            try:
                await ws.send(message_str)
            except Exception:
                dead_ids.append(pid)

        for did in dead_ids:
            if did in self.rooms[room_name]:
                del self.rooms[room_name][did]

    async def handle_websocket(self, websocket):
        player_id = f"p_{self.next_player_num}_{int(time.time()*1000)%100000}"
        color_idx = (self.next_player_num - 1) % len(PLAYER_COLORS)
        default_color = PLAYER_COLORS[color_idx]
        self.next_player_num += 1

        current_room = "6ix"
        player_info = {
            "id": player_id,
            "name": f"DEFENDER-{self.next_player_num - 1}",
            "color": default_color,
            "x": 0, "y": 1.7, "z": 0,
            "yaw": 0, "pitch": 0,
            "anim": "idle",
            "isBerserk": False,
            "health": 100,
            "armor": 50,
            "score": 0
        }

        if current_room not in self.rooms:
            self.rooms[current_room] = {}
        self.rooms[current_room][player_id] = { 'ws': websocket, 'info': player_info }

        print(f"🥊 [+] Player connected: {player_id} in room [{current_room}] (Total: {len(self.rooms[current_room])})")

        # 1. Send Welcome message with existing room members
        existing_players = [
            pdata['info'] for pid, pdata in self.rooms[current_room].items()
            if pid != player_id
        ]
        welcome_pkt = json.dumps({
            "type": "welcome",
            "id": player_id,
            "color": default_color,
            "room": current_room,
            "players": existing_players
        })
        await websocket.send(welcome_pkt)

        # 2. Announce join to other players in room
        join_pkt = json.dumps({
            "type": "player_joined",
            "player": player_info
        })
        await self.broadcast_to_room(current_room, join_pkt, exclude_ws=websocket)

        try:
            async for raw_msg in websocket:
                try:
                    data = json.loads(raw_msg)
                except Exception:
                    continue

                m_type = data.get("type")

                if m_type == "state":
                    # Update internal tracking
                    for k in ("x", "y", "z", "yaw", "pitch", "anim", "isBerserk", "health", "armor", "score"):
                        if k in data:
                            player_info[k] = data[k]
                    # Relay to other peers
                    data["id"] = player_id
                    await self.broadcast_to_room(current_room, json.dumps(data), exclude_ws=websocket)

                elif m_type == "join_info":
                    # Player sends custom name and color
                    if "name" in data and data["name"]:
                        player_info["name"] = str(data["name"])[:20]
                    if "color" in data:
                        player_info["color"] = int(data["color"])
                    update_pkt = json.dumps({
                        "type": "player_updated",
                        "player": player_info
                    })
                    await self.broadcast_to_room(current_room, update_pkt)

                elif m_type == "attack":
                    # Relays a swing/kick/slam event so other players see the attack animation & hear sound
                    data["id"] = player_id
                    await self.broadcast_to_room(current_room, json.dumps(data), exclude_ws=websocket)

                elif m_type == "hit":
                    # Player A hit Player B
                    target_id = data.get("targetId")
                    if target_id and current_room in self.rooms and target_id in self.rooms[current_room]:
                        target_ws = self.rooms[current_room][target_id]["ws"]
                        data["attackerId"] = player_id
                        data["attackerName"] = player_info["name"]
                        try:
                            await target_ws.send(json.dumps(data))
                        except Exception:
                            pass

                elif m_type == "ko":
                    # Broadcast kill announcement
                    data["victimId"] = player_id
                    data["victimName"] = player_info["name"]
                    await self.broadcast_to_room(current_room, json.dumps(data))

                elif m_type == "taunt":
                    data["id"] = player_id
                    data["name"] = player_info["name"]
                    await self.broadcast_to_room(current_room, json.dumps(data))

        except Exception as e:
            pass
        finally:
            if current_room in self.rooms and player_id in self.rooms[current_room]:
                del self.rooms[current_room][player_id]
                count = len(self.rooms[current_room])
                if count == 0:
                    del self.rooms[current_room]
                print(f"🚪 [-] Player disconnected: {player_id} (Remaining: {count})")

            leave_pkt = json.dumps({
                "type": "player_left",
                "id": player_id,
                "name": player_info["name"]
            })
            await self.broadcast_to_room(current_room, leave_pkt)

async def main():
    server = GameServer()
    print("=" * 60)
    print("🥊 FISTS OF DOOM: TORONTO — MULTIPLAYER RELAY SERVER")
    print(f"🎮 Listening on: http://0.0.0.0:{PORT} / ws://0.0.0.0:{PORT}/ws")
    print("🚀 Ready for local LAN play & cloud deployment (Render/Fly.io)")
    print("=" * 60)

    async with serve(
        server.handle_websocket,
        "0.0.0.0",
        PORT,
        process_request=server.process_http_request
    ):
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
