#!/usr/bin/env python3
"""
Fists of Doom: Toronto — multiplayer relay + static file server (one port).

Model
-----
* Rooms come from the WebSocket URL:  ws://host/ws?room=6ix&name=MAPLE-FIST
* Each room has ONE host (the first player in; the oldest remaining player if the
  host leaves). The host's browser runs the robots / snatchers / civilians and
  streams snapshots ("world"); everyone else renders those and sends their hits
  back to the host ("enemy_hit"). The host tells players when a robot punched
  them ("enemy_dmg") and who earned points ("score_event").
* Co-op vs PvP is a ROOM setting held here, so one kid toggling PvP can't hurt
  someone who thinks they're in co-op. Player-vs-player "hit" packets are only
  relayed while the room is in PvP mode.
* All sends use websockets.broadcast(): fire-and-forget, never awaits a slow
  client, and never iterates a dict that another coroutine can mutate.

Runs locally (python3 server_multiplayer.py) or on Render/Fly/Railway ($PORT).
"""
import asyncio
import json
import mimetypes
import os
import re
import sys
import uuid
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

try:
    from websockets.asyncio.server import broadcast, serve
    from websockets.datastructures import Headers
    from websockets.http11 import Response
except ImportError:
    print("Error: websockets>=13 is required:  pip install -r requirements.txt")
    sys.exit(1)

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_ROOM = "6ix"

PLAYER_COLORS = [
    0xef4444,  # red
    0x00f0ff,  # cyan
    0xf59e0b,  # amber
    0x10b981,  # emerald
    0xc026d3,  # purple
    0xf43f5e,  # rose
    0x38bdf8,  # sky
    0xffffff,  # white
]

STATE_KEYS = ("x", "y", "z", "yaw", "pitch", "anim", "isBerserk", "health", "armor", "score")


def clean_room(raw):
    r = re.sub(r"[^a-z0-9_-]", "", (raw or "").strip().lower())[:24]
    return r or DEFAULT_ROOM


def clean_name(raw, fallback):
    n = re.sub(r"[\x00-\x1f<>]", "", (raw or "").strip())[:20]
    return n or fallback


class Room:
    def __init__(self, name):
        self.name = name
        self.players = {}   # pid -> {"ws": ws, "info": {...}}   (insertion order = join order)
        self.host = None
        self.pvp = False

    def conns(self, exclude=None):
        return [p["ws"] for pid, p in self.players.items() if pid != exclude]

    def free_color(self):
        used = {p["info"]["color"] for p in self.players.values()}
        for c in PLAYER_COLORS:
            if c not in used:
                return c
        return PLAYER_COLORS[len(self.players) % len(PLAYER_COLORS)]


class GameServer:
    def __init__(self):
        self.rooms = {}

    # ------------------------------------------------------------------ HTTP
    def static_response(self, path_str):
        clean = urlsplit(path_str).path.strip("/") or "play.html"
        if any(part.startswith(".") for part in clean.split("/")):
            return self.text(404, "Not Found")
        file_path = (BASE_DIR / clean).resolve()
        if not file_path.is_relative_to(BASE_DIR) or not file_path.is_file():
            return self.text(404, "Not Found")
        mime = mimetypes.guess_type(str(file_path))[0] or {
            ".js": "application/javascript", ".css": "text/css"}.get(file_path.suffix, "application/octet-stream")
        body = file_path.read_bytes()
        return Response(200, "OK", Headers([
            ("Content-Type", mime),
            ("Content-Length", str(len(body))),
            ("Access-Control-Allow-Origin", "*"),
            ("Cache-Control", "no-cache, must-revalidate"),
        ]), body)

    @staticmethod
    def text(code, msg):
        body = msg.encode()
        return Response(code, msg, Headers([
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(body))),
            ("Access-Control-Allow-Origin", "*"),
        ]), body)

    async def process_request(self, connection, request):
        if request.headers.get("Upgrade", "").lower() == "websocket":
            return None  # continue the WebSocket handshake
        if urlsplit(request.path).path in ("/health", "/ping"):
            return self.text(200, "pong")
        return self.static_response(request.path)

    # ------------------------------------------------------------- helpers
    @staticmethod
    def send(ws, obj):
        broadcast([ws], json.dumps(obj))

    def send_room(self, room, obj, exclude=None):
        broadcast(room.conns(exclude), json.dumps(obj))

    # ----------------------------------------------------------- WebSocket
    async def handle(self, ws):
        q = parse_qs(urlsplit(ws.request.path).query)
        room_name = clean_room(q.get("room", [None])[0])
        room = self.rooms.get(room_name)
        if room is None:
            room = self.rooms[room_name] = Room(room_name)

        pid = "p_" + uuid.uuid4().hex[:8]
        info = {
            "id": pid,
            "name": clean_name(q.get("name", [None])[0], f"DEFENDER-{len(room.players) + 1}"),
            "color": room.free_color(),
            "x": 0, "y": 0, "z": 0, "yaw": 0, "pitch": 0,
            "anim": "idle", "isBerserk": False, "health": 100, "armor": 50, "score": 0,
        }
        room.players[pid] = {"ws": ws, "info": info}
        if room.host is None:
            room.host = pid
        print(f"[+] {info['name']} ({pid}) joined [{room_name}] host={room.host} n={len(room.players)}")

        self.send(ws, {
            "type": "welcome", "id": pid, "color": info["color"], "name": info["name"],
            "room": room_name, "hostId": room.host, "pvp": room.pvp,
            "players": [p["info"] for k, p in room.players.items() if k != pid],
        })
        self.send_room(room, {"type": "player_joined", "player": info}, exclude=pid)

        try:
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                    if not isinstance(msg, dict):
                        continue
                    self.dispatch(room, pid, info, msg)
                except Exception as e:  # one bad packet must never kill the connection
                    print(f"  bad packet from {pid}: {e}")
        except Exception:
            pass
        finally:
            room.players.pop(pid, None)
            host_changed = False
            if room.host == pid:
                room.host = next(iter(room.players), None)
                host_changed = True
            print(f"[-] {info['name']} ({pid}) left [{room_name}] n={len(room.players)} host={room.host}")
            if not room.players:
                self.rooms.pop(room_name, None)
            else:
                self.send_room(room, {"type": "player_left", "id": pid, "name": info["name"]})
                if host_changed:
                    self.send_room(room, {"type": "host", "hostId": room.host})

    def dispatch(self, room, pid, info, msg):
        t = msg.get("type")
        is_host = (room.host == pid)

        if t == "state":
            out = {"type": "state", "id": pid}
            for k in STATE_KEYS:
                if k in msg:
                    info[k] = msg[k]
                    out[k] = msg[k]
            self.send_room(room, out, exclude=pid)

        elif t == "join_info":
            info["name"] = clean_name(msg.get("name"), info["name"])
            self.send_room(room, {"type": "player_updated", "player": info}, exclude=pid)

        elif t in ("attack", "taunt"):
            msg["id"] = pid
            msg["name"] = info["name"]
            self.send_room(room, msg, exclude=pid)

        elif t == "set_mode":
            room.pvp = bool(msg.get("pvp"))
            self.send_room(room, {"type": "mode", "pvp": room.pvp, "by": info["name"]})

        elif t == "hit":  # player-vs-player, only in PvP rooms
            target = room.players.get(msg.get("targetId"))
            if room.pvp and target:
                msg.update(attackerId=pid, attackerName=info["name"])
                self.send(target["ws"], msg)

        elif t == "ko":
            msg.update(victimId=pid, victimName=info["name"])
            self.send_room(room, msg)

        # ---- host-authoritative NPC sync ----
        elif t == "world":
            if is_host:
                self.send_room(room, msg, exclude=pid)

        elif t == "enemy_hit":  # guest -> host
            host = room.players.get(room.host)
            if host and not is_host:
                msg["from"] = pid
                self.send(host["ws"], msg)

        elif t in ("enemy_dmg", "score_event"):  # host -> one guest
            target = room.players.get(msg.get("targetId"))
            if is_host and target:
                self.send(target["ws"], msg)


async def main():
    server = GameServer()
    print("=" * 60)
    print("FISTS OF DOOM: TORONTO — multiplayer relay")
    print(f"http://0.0.0.0:{PORT}   ws://0.0.0.0:{PORT}/ws?room=<name>")
    print("=" * 60)
    async with serve(server.handle, "0.0.0.0", PORT, process_request=server.process_request,
                     max_size=2 ** 20, ping_interval=20, ping_timeout=60):
        await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
