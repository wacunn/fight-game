"""
Toronto Brawl AI - Fast Vectorized Gymnasium Environment
Simulates the Toronto city map (buildings, traffic, pedestrians, snatchers, goals)
for Recurrent PPO (Actor-Critic with GRU/LSTM) reinforcement learning.
"""

import math
import json
import os
import random
import numpy as np
import gymnasium as gym
from gymnasium import spaces

# Toronto Districts & Key Landmarks for multi-district spawn curriculum
DISTRICT_SPAWNS = [
    {"name": "CN Tower Plaza", "x": -286.5, "z": 159.4, "radius": 40.0},
    {"name": "Ripley's Aquatics", "x": -216.6, "z": 171.4, "radius": 35.0},
    {"name": "Rogers Centre North", "x": -459.9, "z": 246.6, "radius": 45.0},
    {"name": "Roundhouse Park", "x": -203.9, "z": 349.5, "radius": 40.0},
    {"name": "Union Station Front St", "x": 265.4, "z": -128.9, "radius": 45.0},
    {"name": "Royal York Corridor", "x": 178.2, "z": -215.2, "radius": 40.0},
    {"name": "Roy Thomson Hall", "x": -229.0, "z": -292.5, "radius": 35.0},
    {"name": "Pecaut Square Sanctuary", "x": -245.0, "z": -240.0, "radius": 30.0},
    {"name": "Gooderham Flatiron", "x": 749.3, "z": -491.7, "radius": 35.0},
    {"name": "St. Lawrence Market", "x": 956.7, "z": -534.9, "radius": 40.0},
    {"name": "Simcoe Bridge Crossing", "x": -110.0, "z": -20.0, "radius": 25.0},
    {"name": "John Street Overpass", "x": -350.0, "z": 70.0, "radius": 25.0},
    {"name": "Spadina Overpass West", "x": -550.0, "z": 160.0, "radius": 30.0},
    {"name": "Financial District (Bay & King)", "x": 150.0, "z": -260.0, "radius": 50.0},
    {"name": "Harbourfront South", "x": 0.0, "z": 380.0, "radius": 50.0},
    {"name": "Lakeshore East", "x": 450.0, "z": 100.0, "radius": 50.0},
]

# Rail corridor spline
USRC_SPLINE = [
    [-850, 240.0], [-750, 215.0], [-650, 185.0], [-550, 150.0],
    [-450, 115.0], [-350, 78.0],  [-250, 42.0],  [-150, 10.0],
    [-50, -18.0],  [50, -42.0],   [140, -60.0],  [230, -74.0],
    [320, -88.0],  [420, -118.0], [520, -142.0], [620, -162.0],
    [720, -182.0], [850, -210.0]
]
TRENCH_X0, TRENCH_X1 = -900.0, 860.0
TRENCH_HALF_W = 14.0

def get_usrc_z(x):
    if x <= USRC_SPLINE[0][0]:
        return USRC_SPLINE[0][1]
    if x >= USRC_SPLINE[-1][0]:
        return USRC_SPLINE[-1][1]
    for i in range(len(USRC_SPLINE) - 1):
        x0, z0 = USRC_SPLINE[i]
        x1, z1 = USRC_SPLINE[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            t = t * t * (3.0 - 2.0 * t)
            return z0 + t * (z1 - z0)
    return 0.0

def is_inside_trench(x, z):
    if x < TRENCH_X0 or x > TRENCH_X1:
        return False
    return abs(z - get_usrc_z(x)) < TRENCH_HALF_W

def is_point_in_polygon(x, z, poly):
    # Ray casting algorithm
    inside = False
    n = len(poly) // 2
    for i in range(n):
        x1, z1 = poly[i * 2], poly[i * 2 + 1]
        x2, z2 = poly[((i + 1) % n) * 2], poly[((i + 1) % n) * 2 + 1]
        if ((z1 > z) != (z2 > z)) and (x < (x2 - x1) * (z - z1) / (z2 - z1 + 1e-9) + x1):
            inside = not inside
    return inside


class TorontoMapCollision:
    """Fast spatial hashing for 590 Toronto building footprints and bridges."""
    def __init__(self, map_file_path=None):
        if map_file_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            map_file_path = os.path.join(base_dir, "toronto_map.js")

        with open(map_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        idx = content.find("window.TORONTO_MAP = ")
        raw_json = content[idx + len("window.TORONTO_MAP = "):].rstrip(";\n ")
        data = json.loads(raw_json)

        self.bounds = data.get("bounds", [[-820.1, -680.1], [980.4, 520.1]])
        self.min_x, self.min_z = self.bounds[0]
        self.max_x, self.max_z = self.bounds[1]

        # Spatial grid
        self.cell_size = 25.0
        self.grid = {}

        # Parse buildings
        self.buildings = []
        for b in data.get("buildings", []):
            poly = b.get("p", [])
            if len(poly) < 6:
                continue
            xs = poly[0::2]
            zs = poly[1::2]
            min_bx, max_bx = min(xs), max(xs)
            min_bz, max_bz = min(zs), max(zs)
            item = {"poly": poly, "bb": (min_bx, min_bz, max_bx, max_bz)}
            self.buildings.append(item)

            # Insert into spatial grid
            c_x0 = int(math.floor(min_bx / self.cell_size))
            c_x1 = int(math.floor(max_bx / self.cell_size))
            c_z0 = int(math.floor(min_bz / self.cell_size))
            c_z1 = int(math.floor(max_bz / self.cell_size))
            for cx in range(c_x0, c_x1 + 1):
                for cz in range(c_z0, c_z1 + 1):
                    key = (cx, cz)
                    if key not in self.grid:
                        self.grid[key] = []
                    self.grid[key].append(item)

        # Bridges over railway trench (bridges allow safe passage over trench)
        self.bridges = [
            # [minX, minZ, maxX, maxZ]
            [-560.0, 140.0, -540.0, 180.0], # Spadina Overpass
            [-360.0, 50.0, -340.0, 100.0],  # John St Bridge
            [-125.0, -30.0, -95.0, 10.0],   # Simcoe Bridge
            [50.0, -60.0, 80.0, -20.0],     # York St
            [140.0, -85.0, 170.0, -45.0],   # Bay St
            [230.0, -100.0, 260.0, -60.0],  # Yonge St
            [320.0, -115.0, 350.0, -75.0],  # Jarvis
        ]

        # Pre-rasterize a 2.5m occupancy grid for ultra-fast raycasting (2,000+ steps/sec)
        self.occ_res = 2.5
        self.occ_w = int((self.max_x - self.min_x) / self.occ_res) + 1
        self.occ_h = int((self.max_z - self.min_z) / self.occ_res) + 1
        self.occ_grid = np.zeros((self.occ_w, self.occ_h), dtype=bool)

        for b in self.buildings:
            bb = b["bb"]
            gx0 = max(0, int((bb[0] - self.min_x) / self.occ_res))
            gx1 = min(self.occ_w - 1, int((bb[2] - self.min_x) / self.occ_res))
            gz0 = max(0, int((bb[1] - self.min_z) / self.occ_res))
            gz1 = min(self.occ_h - 1, int((bb[3] - self.min_z) / self.occ_res))
            poly = b["poly"]
            for gx in range(gx0, gx1 + 1):
                wx = self.min_x + gx * self.occ_res
                for gz in range(gz0, gz1 + 1):
                    wz = self.min_z + gz * self.occ_res
                    if is_point_in_polygon(wx, wz, poly):
                        self.occ_grid[gx, gz] = True

        # Rasterize trench non-bridge cells
        for gx in range(self.occ_w):
            wx = self.min_x + gx * self.occ_res
            if TRENCH_X0 <= wx <= TRENCH_X1:
                for gz in range(self.occ_h):
                    wz = self.min_z + gz * self.occ_res
                    if is_inside_trench(wx, wz) and not self.is_on_bridge(wx, wz):
                        self.occ_grid[gx, gz] = True

    def is_on_bridge(self, x, z):
        for b in self.bridges:
            if b[0] <= x <= b[2] and b[1] <= z <= b[3]:
                return True
        return False

    def is_blocked(self, x, z):
        gx = int((x - self.min_x) / self.occ_res)
        gz = int((z - self.min_z) / self.occ_res)
        if 0 <= gx < self.occ_w and 0 <= gz < self.occ_h:
            return self.occ_grid[gx, gz]
        return True

    def can_move_to(self, x, z, radius=0.6):
        # Quick bounds & occupancy check
        if self.is_blocked(x, z):
            return False
        if self.is_blocked(x + radius, z) or self.is_blocked(x - radius, z):
            return False
        if self.is_blocked(x, z + radius) or self.is_blocked(x, z - radius):
            return False
        return True

    def raycast(self, ox, oz, angle, max_dist=20.0):
        """Ultra-fast raycast against pre-rasterized 2.5m occupancy grid."""
        dx = math.cos(angle) * 1.5
        dz = math.sin(angle) * 1.5
        cur_x = ox
        cur_z = oz
        cur_dist = 0.0
        while cur_dist < max_dist:
            cur_dist += 1.5
            cur_x += dx
            cur_z += dz
            gx = int((cur_x - self.min_x) / self.occ_res)
            gz = int((cur_z - self.min_z) / self.occ_res)
            if not (0 <= gx < self.occ_w and 0 <= gz < self.occ_h):
                return cur_dist
            if self.occ_grid[gx, gz]:
                return cur_dist
        return max_dist


class TorontoFightGymEnv(gym.Env):
    """
    Gymnasium environment simulating Toronto brawl mechanics for Recurrent PPO.
    Supports Multi-District Spawning & Goal-Conditioned Navigation/Combat.
    """
    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, map_file=None):
        super().__init__()
        self.map_col = TorontoMapCollision(map_file)

        # Observation space: 56 normalized numerical floats
        # [8]  Ego State: pos (2), heading (2), vel (2), health (1), berserk (1)
        # [8]  Active Goal: relative delta (2), distance (1), relative angle (2), goal type one-hot (3)
        # [16] LiDAR distance probes (16 rays around player, 0.0 to 1.0)
        # [12] Top 3 Nearest Threats: relative delta (2), distance (1), health (1) x 3
        # [4]  Nearest Innocent: relative delta (2), distance (1), is_snatched (1)
        # [6]  Nearest Vehicle Hazard: relative delta (2), vel (2), distance (1), TTC norm (1)
        # [2]  Peace Sanctuary Relative Delta: (2)
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(56,), dtype=np.float32
        )

        # Action Space: MultiDiscrete([9, 6])
        # Action[0] = Movement Heading:
        #   0: Idle, 1: N, 2: NE, 3: E, 4: SE, 5: S, 6: SW, 7: W, 8: NW
        # Action[1] = Action Trigger:
        #   0: None, 1: Light Punch, 2: Quick Kick, 3: Meteor Slam, 4: Dodge Roll, 5: Glory Kill
        self.action_space = spaces.MultiDiscrete([9, 6])

        # Direction angle offsets for Action[0] (0 is Idle)
        self.move_dirs = [
            None,
            (0.0, -1.0),                 # 1: North (-Z)
            (0.7071, -0.7071),           # 2: NE
            (1.0, 0.0),                  # 3: East (+X)
            (0.7071, 0.7071),            # 4: SE
            (0.0, 1.0),                  # 5: South (+Z)
            (-0.7071, 0.7071),           # 6: SW
            (-1.0, 0.0),                 # 7: West (-X)
            (-0.7071, -0.7071),          # 8: NW
        ]

        self.max_steps = 600
        self.dt = 1.0 / 15.0 # 15 Hz decision tick

        # Peace Sanctuary locations (Pecaut Square, Roundhouse Park)
        self.sanctuaries = [
            {"x": -245.0, "z": -240.0, "r": 28.0},
            {"x": -203.9, "z": 349.5, "r": 25.0},
        ]

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0

        # Multi-district spawn: Select a landmark district or random street
        if random.random() < 0.75:
            district = random.choice(DISTRICT_SPAWNS)
            cx, cz, cr = district["x"], district["z"], district["radius"]
            self.current_district = district["name"]
        else:
            # Full city exploration
            cx = random.uniform(self.map_col.min_x + 50, self.map_col.max_x - 50)
            cz = random.uniform(self.map_col.min_z + 50, self.map_col.max_z - 50)
            cr = 40.0
            self.current_district = "Downtown Grid Patrol"

        self.episode_reward = 0.0
        self.episode_length = 0

        # Find open walkable spot
        player_x, player_z = cx, cz
        for _ in range(100):
            cand_x = cx + random.uniform(-cr, cr)
            cand_z = cz + random.uniform(-cr, cr)
            if self.map_col.can_move_to(cand_x, cand_z, radius=0.8):
                player_x, player_z = cand_x, cand_z
                break

        self.player = {
            "x": player_x,
            "z": player_z,
            "vx": 0.0,
            "vz": 0.0,
            "heading": random.uniform(-math.pi, math.pi),
            "health": 100.0,
            "berserk": random.uniform(0.0, 40.0),
            "slam_cooldown": 0.0,
            "dodge_cooldown": 0.0,
        }

        # Spawn Active Goal (Distress Beacon, Hostile Nest, Kid Rescue, Sanctuary)
        self.goal_type = random.choice([0, 1, 2]) # 0=Waypoint/Beacon, 1=Hostile Boss, 2=Peace Sanctuary
        if self.goal_type == 2:
            sanc = random.choice(self.sanctuaries)
            self.goal = {"x": sanc["x"], "z": sanc["z"], "radius": sanc["r"], "is_marathon": False}
            self.max_steps = 700
        else:
            # Multi-tier curriculum navigation:
            # 35% Local Block (30m - 90m)
            # 35% Multi-Block Neighborhood (100m - 350m)
            # 30% Full Cross-City Marathon (350m - 1400m, e.g. CN Tower -> St. Lawrence Market!)
            tier = random.random()
            if tier < 0.35:
                min_d, max_d = 30.0, 90.0
                target_landmark = None
            elif tier < 0.70:
                min_d, max_d = 100.0, 350.0
                target_landmark = None
            else:
                min_d, max_d = 350.0, 1400.0
                other_landmarks = [d for d in DISTRICT_SPAWNS if d["name"] != self.current_district]
                target_landmark = random.choice(other_landmarks) if other_landmarks else None

            if target_landmark:
                gx, gz = target_landmark["x"], target_landmark["z"]
                for _ in range(30):
                    cand_gx = gx + random.uniform(-target_landmark["radius"], target_landmark["radius"])
                    cand_gz = gz + random.uniform(-target_landmark["radius"], target_landmark["radius"])
                    if self.map_col.can_move_to(cand_gx, cand_gz, radius=1.0):
                        gx, gz = cand_gx, cand_gz
                        break
            else:
                gx, gz = player_x, player_z
                for _ in range(80):
                    ang = random.uniform(0, math.pi * 2)
                    dist = random.uniform(min_d, max_d)
                    tx = player_x + math.cos(ang) * dist
                    tz = player_z + math.sin(ang) * dist
                    if self.map_col.can_move_to(tx, tz, radius=1.0):
                        gx, gz = tx, tz
                        break

            target_dist = math.hypot(gx - player_x, gz - player_z)
            is_marathon = target_dist >= 350.0
            self.goal = {
                "x": gx,
                "z": gz,
                "radius": 6.0 if is_marathon else 4.5,
                "is_marathon": is_marathon,
                "dest_name": target_landmark["name"] if target_landmark else "Street Waypoint"
            }
            # Dynamically scale max steps so the agent has plenty of time for cross-city travel
            self.max_steps = max(500, min(2500, int(350 + target_dist * 1.6)))

        # Spawn Hostile Enemies (Snatcher robots, surveillance drones)
        self.enemies = []
        num_enemies = random.randint(2, 5)
        for i in range(num_enemies):
            ex, ez = player_x, player_z
            for _ in range(40):
                ang = random.uniform(0, math.pi * 2)
                dist = random.uniform(10.0, 40.0)
                cand_ex = player_x + math.cos(ang) * dist
                cand_ez = player_z + math.sin(ang) * dist
                if self.map_col.can_move_to(cand_ex, cand_ez, radius=0.6):
                    ex, ez = cand_ex, cand_ez
                    break
            self.enemies.append({
                "x": ex,
                "z": ez,
                "vx": 0.0,
                "vz": 0.0,
                "hp": 60.0,
                "max_hp": 60.0,
                "state": "patrol", # patrol, chase, attack, dizzy
                "attack_timer": random.uniform(0.5, 2.0),
                "is_dizzy": False,
            })

        # Spawn Innocent Citizens / Kids
        self.civilians = []
        for _ in range(random.randint(1, 3)):
            civ_x, civ_z = player_x, player_z
            for _ in range(30):
                ang = random.uniform(0, math.pi * 2)
                dist = random.uniform(8.0, 35.0)
                cand_x = player_x + math.cos(ang) * dist
                cand_z = player_z + math.sin(ang) * dist
                if self.map_col.can_move_to(cand_x, cand_z, radius=0.6):
                    civ_x, civ_z = cand_x, cand_z
                    break
            self.civilians.append({
                "x": civ_x,
                "z": civ_z,
                "is_snatched": False,
            })

        # Spawn Traffic (Cars driving on nearby roads)
        self.cars = []
        for _ in range(3):
            # Car traveling along road
            car_x = player_x + random.uniform(-40.0, 40.0)
            car_z = player_z + random.uniform(-40.0, 40.0)
            ang = random.choice([0.0, math.pi * 0.5, math.pi, -math.pi * 0.5])
            speed = random.uniform(9.0, 14.0)
            self.cars.append({
                "x": car_x,
                "z": car_z,
                "vx": math.cos(ang) * speed,
                "vz": math.sin(ang) * speed,
                "heading": ang,
            })

        self.prev_dist_to_goal = math.hypot(self.goal["x"] - player_x, self.goal["z"] - player_z)
        return self._get_obs(), {}

    def _get_obs(self):
        obs = np.zeros(56, dtype=np.float32)
        px, pz = self.player["x"], self.player["z"]
        yaw = self.player["heading"]

        # 1. Ego State (8)
        obs[0] = px / 1000.0
        obs[1] = pz / 1000.0
        obs[2] = math.sin(yaw)
        obs[3] = math.cos(yaw)
        obs[4] = self.player["vx"] / 10.0
        obs[5] = self.player["vz"] / 10.0
        obs[6] = self.player["health"] / 100.0
        obs[7] = self.player["berserk"] / 100.0

        # 2. Active Goal (8)
        gx, gz = self.goal["x"], self.goal["z"]
        dx_g = gx - px
        dz_g = gz - pz
        dist_g = math.hypot(dx_g, dz_g)
        goal_ang = math.atan2(dz_g, dx_g) - yaw
        obs[8] = np.clip(dx_g / 500.0, -1.0, 1.0)
        obs[9] = np.clip(dz_g / 500.0, -1.0, 1.0)
        obs[10] = math.tanh(dist_g / 50.0)
        obs[11] = math.sin(goal_ang)
        obs[12] = math.cos(goal_ang)
        obs[13] = 1.0 if self.goal_type == 0 else 0.0 # Waypoint/Beacon
        obs[14] = 1.0 if self.goal_type == 1 else 0.0 # Combat Target
        obs[15] = 1.0 if self.goal_type == 2 else 0.0 # Peace Sanctuary

        # 3. 16-ray LiDAR distance probes (16)
        for i in range(16):
            ray_ang = yaw + (i / 16.0) * math.pi * 2.0
            d = self.map_col.raycast(px, pz, ray_ang, max_dist=20.0)
            obs[16 + i] = d / 20.0

        # 4. Top 3 Nearest Threats (12 = 3 * 4)
        active_enemies = [e for e in self.enemies if e["hp"] > 0]
        active_enemies.sort(key=lambda e: math.hypot(e["x"] - px, e["z"] - pz))
        for i in range(3):
            base_idx = 32 + i * 4
            if i < len(active_enemies):
                e = active_enemies[i]
                edx = e["x"] - px
                edz = e["z"] - pz
                edist = math.hypot(edx, edz)
                obs[base_idx] = np.clip(edx / 40.0, -1.0, 1.0)
                obs[base_idx + 1] = np.clip(edz / 40.0, -1.0, 1.0)
                obs[base_idx + 2] = np.clip(edist / 40.0, -1.0, 1.0)
                obs[base_idx + 3] = e["hp"] / e["max_hp"]
            else:
                obs[base_idx:base_idx + 4] = 0.0

        # 5. Nearest Innocent / Kid (4)
        if self.civilians:
            c = min(self.civilians, key=lambda civ: math.hypot(civ["x"] - px, civ["z"] - pz))
            cdx = c["x"] - px
            cdz = c["z"] - pz
            cdist = math.hypot(cdx, cdz)
            obs[44] = np.clip(cdx / 40.0, -1.0, 1.0)
            obs[45] = np.clip(cdz / 40.0, -1.0, 1.0)
            obs[46] = np.clip(cdist / 40.0, -1.0, 1.0)
            obs[47] = 1.0 if c["is_snatched"] else 0.0

        # 6. Nearest Traffic Hazard (Car) (6)
        if self.cars:
            car = min(self.cars, key=lambda c: math.hypot(c["x"] - px, c["z"] - pz))
            cardx = car["x"] - px
            cardz = car["z"] - pz
            cardist = math.hypot(cardx, cardz)
            # Time to collision
            rel_vx = car["vx"] - self.player["vx"]
            rel_vz = car["vz"] - self.player["vz"]
            approach_speed = -(cardx * rel_vx + cardz * rel_vz) / (cardist + 1e-5)
            ttc = (cardist / approach_speed) if approach_speed > 0.5 else 999.0
            obs[48] = np.clip(cardx / 40.0, -1.0, 1.0)
            obs[49] = np.clip(cardz / 40.0, -1.0, 1.0)
            obs[50] = np.clip(car["vx"] / 15.0, -1.0, 1.0)
            obs[51] = np.clip(car["vz"] / 15.0, -1.0, 1.0)
            obs[52] = np.clip(cardist / 40.0, -1.0, 1.0)
            obs[53] = 1.0 / (1.0 + max(0.0, ttc))

        # 7. Nearest Peace Sanctuary (2)
        nearest_sanc = min(self.sanctuaries, key=lambda s: math.hypot(s["x"] - px, s["z"] - pz))
        obs[54] = np.clip((nearest_sanc["x"] - px) / 500.0, -1.0, 1.0)
        obs[55] = np.clip((nearest_sanc["z"] - pz) / 500.0, -1.0, 1.0)

        return obs

    def step(self, action):
        self.step_count += 1
        dt = self.dt
        reward = -0.01 # Small step time penalty to incentivize swiftness

        move_act = int(action[0])
        combat_act = int(action[1])

        # 1. Player Movement
        speed = 7.5 if self.player["berserk"] > 50 else 5.5
        if move_act > 0 and self.move_dirs[move_act] is not None:
            mx, mz = self.move_dirs[move_act]
            self.player["vx"] = mx * speed
            self.player["vz"] = mz * speed
            self.player["heading"] = math.atan2(mz, mx)
        else:
            self.player["vx"] *= 0.7
            self.player["vz"] *= 0.7

        nx = self.player["x"] + self.player["vx"] * dt
        nz = self.player["z"] + self.player["vz"] * dt

        # Collision with city obstacles
        if self.map_col.can_move_to(nx, self.player["z"], radius=0.6):
            self.player["x"] = nx
        else:
            reward -= 0.05
            self.player["vx"] = 0.0

        if self.map_col.can_move_to(self.player["x"], nz, radius=0.6):
            self.player["z"] = nz
        else:
            reward -= 0.05
            self.player["vz"] = 0.0

        px, pz = self.player["x"], self.player["z"]

        # Check Peace Sanctuary regeneration
        in_sanctuary = any(math.hypot(s["x"] - px, s["z"] - pz) <= s["r"] for s in self.sanctuaries)
        if in_sanctuary:
            if self.player["health"] < 100.0:
                self.player["health"] = min(100.0, self.player["health"] + 10.0 * dt)
                reward += 0.15 # Reward retreating to heal when damaged

        # 2. Combat Execution
        if combat_act == 1: # Light Punch (reach 2.5m)
            for e in self.enemies:
                if e["hp"] > 0 and math.hypot(e["x"] - px, e["z"] - pz) < 2.5:
                    e["hp"] -= 18.0
                    reward += 1.5
                    self.player["berserk"] = min(100.0, self.player["berserk"] + 12.0)
                    if e["hp"] <= 0:
                        reward += 8.0 # Kill reward
            # Punish hitting civilians
            for c in self.civilians:
                if math.hypot(c["x"] - px, c["z"] - pz) < 2.5:
                    reward -= 5.0

        elif combat_act == 2: # Quick Kick (reach 3.2m, knockback)
            for e in self.enemies:
                if e["hp"] > 0:
                    d = math.hypot(e["x"] - px, e["z"] - pz)
                    if d < 3.2:
                        e["hp"] -= 26.0
                        reward += 2.2
                        # Push enemy back
                        e["x"] += (e["x"] - px) / (d + 1e-4) * 2.0
                        e["z"] += (e["z"] - pz) / (d + 1e-4) * 2.0
                        if e["hp"] <= 0:
                            reward += 8.0

        elif combat_act == 3: # Meteor Slam (AoE 6m)
            if self.player["slam_cooldown"] <= 0:
                self.player["slam_cooldown"] = 3.0
                hit_any = False
                for e in self.enemies:
                    if e["hp"] > 0 and math.hypot(e["x"] - px, e["z"] - pz) < 6.0:
                        e["hp"] -= 45.0
                        reward += 3.5
                        hit_any = True
                        if e["hp"] <= 0:
                            reward += 10.0
                if not hit_any:
                    reward -= 0.2

        elif combat_act == 4: # Dodge Roll
            if self.player["dodge_cooldown"] <= 0:
                self.player["dodge_cooldown"] = 1.2
                self.player["x"] += math.cos(self.player["heading"]) * 4.0
                self.player["z"] += math.sin(self.player["heading"]) * 4.0

        elif combat_act == 5: # Glory Kill on dizzy enemy
            for e in self.enemies:
                if e["hp"] > 0 and e["is_dizzy"] and math.hypot(e["x"] - px, e["z"] - pz) < 3.0:
                    e["hp"] = 0
                    reward += 15.0
                    self.player["health"] = min(100.0, self.player["health"] + 25.0)

        # Update Cooldowns
        self.player["slam_cooldown"] = max(0.0, self.player["slam_cooldown"] - dt)
        self.player["dodge_cooldown"] = max(0.0, self.player["dodge_cooldown"] - dt)
        self.player["berserk"] = max(0.0, self.player["berserk"] - 1.5 * dt)

        # 3. Enemy AI Simulation
        for e in self.enemies:
            if e["hp"] <= 0:
                continue
            if e["hp"] < 20.0:
                e["is_dizzy"] = True
            dist_to_player = math.hypot(px - e["x"], pz - e["z"])
            if dist_to_player < 18.0 and not in_sanctuary:
                # Chase player
                e["x"] += (px - e["x"]) / (dist_to_player + 1e-4) * 3.8 * dt
                e["z"] += (pz - e["z"]) / (dist_to_player + 1e-4) * 3.8 * dt
                # Attack player if in melee
                if dist_to_player < 1.8:
                    e["attack_timer"] -= dt
                    if e["attack_timer"] <= 0:
                        e["attack_timer"] = 1.2
                        self.player["health"] -= 12.0
                        reward -= 1.0

        # 4. Traffic Simulation & Hazards
        for car in self.cars:
            car["x"] += car["vx"] * dt
            car["z"] += car["vz"] * dt
            # Wrap cars around boundaries
            if car["x"] < self.map_col.min_x: car["x"] = self.map_col.max_x
            if car["x"] > self.map_col.max_x: car["x"] = self.map_col.min_x
            if car["z"] < self.map_col.min_z: car["z"] = self.map_col.max_z
            if car["z"] > self.map_col.max_z: car["z"] = self.map_col.min_z

            # Check collision with player
            if math.hypot(car["x"] - px, car["z"] - pz) < 2.5:
                self.player["health"] -= 25.0
                reward -= 12.0 # Big penalty for getting hit by a car!

        # 5. Goal Progress Reward
        cur_dist_to_goal = math.hypot(self.goal["x"] - px, self.goal["z"] - pz)
        dist_improvement = self.prev_dist_to_goal - cur_dist_to_goal
        reward += dist_improvement * 0.4 # Positive reward for moving towards goal
        self.prev_dist_to_goal = cur_dist_to_goal

        # Goal Completion Check
        terminated = False
        if cur_dist_to_goal <= self.goal["radius"]:
            is_m = self.goal.get("is_marathon", False)
            reward += 60.0 if is_m else 30.0 # Huge bonus for completing cross-city marathon!
            terminated = True

        if self.player["health"] <= 0:
            reward -= 20.0 # Death penalty
            terminated = True

        truncated = self.step_count >= self.max_steps

        self.episode_reward += reward
        self.episode_length += 1

        info = {
            "health": self.player["health"],
            "district": self.current_district,
            "goal_reached": cur_dist_to_goal <= self.goal["radius"],
            "is_marathon": self.goal.get("is_marathon", False),
            "dest_name": self.goal.get("dest_name", ""),
        }
        if terminated or truncated:
            info["episode"] = {
                "r": round(float(self.episode_reward), 2),
                "l": int(self.episode_length),
                "district": self.current_district,
                "won": cur_dist_to_goal <= self.goal["radius"],
                "is_marathon": self.goal.get("is_marathon", False),
            }
        return self._get_obs(), reward, terminated, truncated, info
