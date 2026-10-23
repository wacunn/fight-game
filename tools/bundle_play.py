#!/usr/bin/env python3
"""
Bundle index.html, styles.css, toronto_map.js, city.js, traffic.js, multiplayer.js, ai_grid.js,
ai_copilot.js (+ ai_model.json) and game.js
into a single standalone play.html file for offline play.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def bundle():
    index_html = (BASE_DIR / 'index.html').read_text(encoding='utf-8')
    styles_css = (BASE_DIR / 'styles.css').read_text(encoding='utf-8')
    toronto_map = (BASE_DIR / 'toronto_map.js').read_text(encoding='utf-8')
    city_js = (BASE_DIR / 'city.js').read_text(encoding='utf-8')
    traffic_js = (BASE_DIR / 'traffic.js').read_text(encoding='utf-8')
    multiplayer_js = (BASE_DIR / 'multiplayer.js').read_text(encoding='utf-8')
    ai_copilot_js = (BASE_DIR / 'ai_copilot.js').read_text(encoding='utf-8')
    game_js = (BASE_DIR / 'game.js').read_text(encoding='utf-8')

    # Replace CSS link
    css_tag = '<link rel="stylesheet" href="styles.css">'
    inline_css = f'<style>\n{styles_css}\n</style>'
    if css_tag in index_html:
        out = index_html.replace(css_tag, inline_css)
    else:
        raise RuntimeError(f"Could not find {css_tag} in index.html")

    # Replace JS script tags
    map_tag = '<script src="toronto_map.js"></script>'
    city_tag = '<script src="city.js"></script>'
    traffic_tag = '<script src="traffic.js"></script>'
    multiplayer_tag = '<script src="multiplayer.js"></script>'
    ai_tag = '<script src="ai_copilot.js"></script>'
    game_tag = '<script src="game.js"></script>'

    grid_file = BASE_DIR / 'ai_grid.js'
    grid_js = grid_file.read_text(encoding='utf-8') if grid_file.exists() else ''
    out = out.replace('<script src="ai_grid.js"></script>', f'<script>\n{grid_js}\n</script>' if grid_js else '')

    ai_runner_file = BASE_DIR / 'ai_model_runner.json'
    if not ai_runner_file.exists():
        ai_runner_file = BASE_DIR / 'ai_model.json'
    ai_fighter_file = BASE_DIR / 'ai_model_fighter.json'

    scripts = []
    if ai_runner_file.exists():
        scripts.append(f'window.AI_MODEL_WEIGHTS_RUNNER = {ai_runner_file.read_text(encoding="utf-8")};')
        scripts.append('window.AI_MODEL_WEIGHTS = window.AI_MODEL_WEIGHTS_RUNNER;')
    if ai_fighter_file.exists():
        scripts.append(f'window.AI_MODEL_WEIGHTS_FIGHTER = {ai_fighter_file.read_text(encoding="utf-8")};')

    inlined_weights = "\n".join(scripts)
    ai_inline = f'<script>\n{inlined_weights}\n</script>\n<script>\n{ai_copilot_js}\n</script>'

    out = out.replace(map_tag, f'<script>\n{toronto_map}\n</script>')
    out = out.replace(city_tag, f'<script>\n{city_js}\n</script>')
    out = out.replace(traffic_tag, f'<script>\n{traffic_js}\n</script>')
    out = out.replace(multiplayer_tag, f'<script>\n{multiplayer_js}\n</script>')
    out = out.replace(ai_tag, ai_inline)
    out = out.replace(game_tag, f'<script>\n{game_js}\n</script>')

    (BASE_DIR / 'play.html').write_text(out, encoding='utf-8')
    size_kb = len(out.encode('utf-8')) / 1024
    print(f"Successfully generated standalone play.html ({size_kb:.1f} KB)")

if __name__ == '__main__':
    bundle()
