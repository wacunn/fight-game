"""
30 authentic Toronto districts and landmarks for RL evaluation and leaderboard tracking.
Each landmark coordinate has been verified against the walkable 1m collision grid.
"""
import numpy as np

DISTRICTS = [
    ("CN Tower Plaza", -286.5, 159.4),
    ("Ripley Aquatics", -235.0, 195.0),
    ("Rogers Centre North", -460.0, 390.0),
    ("Roundhouse Park", -203.9, 349.5),
    ("Union Station Front St", 265.4, -128.9),
    ("Fairmont Royal York", 178.2, -215.2),
    ("Roy Thomson Hall (King & Simcoe)", -220.0, -260.0),
    ("Pecaut Square Sanctuary", -245.0, -240.0),
    ("Gooderham Flatiron", 749.3, -491.7),
    ("St. Lawrence Market", 956.7, -534.9),
    ("Simcoe Bridge Crossing", -110.0, -20.0),
    ("John Street Overpass", -350.0, 70.0),
    ("Spadina Overpass West", -550.0, 160.0),
    ("Financial District (Bay & King)", 150.0, -260.0),
    ("Harbourfront Centre", 0.0, 380.0),
    ("Lakeshore East Promenade", 450.0, 100.0),
    ("Scotiabank Arena (Maple Leaf Sq)", 230.0, 140.0),
    ("Brookfield Place", 330.0, -220.0),
    ("TD Centre Mies Plaza", 100.0, -180.0),
    ("First Canadian Place", 120.0, -350.0),
    ("Scotia Plaza (King & Yonge)", 350.0, -320.0),
    ("King West Theatre District", -400.0, -260.0),
    ("Bell Lightbox / TIFF", -430.0, -200.0),
    ("Bremner Boulevard Corridor", -50.0, 220.0),
    ("Queen Quay West Marina", -300.0, 430.0),
    ("Rees Street Parkette", -480.0, 450.0),
    ("Spadina & Front Esplanade", -620.0, 220.0),
    ("Berczy Park Dog Fountain", 600.0, -420.0),
    ("Meridian Hall Esplanade", 450.0, -180.0),
    ("St. Lawrence Hall (King East)", 850.0, -450.0),
]

DISTRICT_NAMES = [name for name, _, _ in DISTRICTS]
DISTRICT_COORDS = np.array([[x, z] for _, x, z in DISTRICTS], dtype=np.float32)


def get_nearest_district(x, z):
    """Return the name of the nearest Toronto district for given coordinates."""
    dx = DISTRICT_COORDS[:, 0] - x
    dz = DISTRICT_COORDS[:, 1] - z
    idx = int(np.argmin(dx * dx + dz * dz))
    return DISTRICT_NAMES[idx]


def get_district_stats_template():
    """Generate empty stats dictionary for all 30 districts."""
    return {name: {"episodes": 0, "wins": 0, "ret": 0.0} for name in DISTRICT_NAMES}
