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
    import re
    inline_css = f'<style>\n{styles_css}\n</style>'
    out = re.sub(r'<link rel="stylesheet" href="styles\.css[^"]*">', lambda m: inline_css, index_html)

    # Replace JS script tags
    grid_file = BASE_DIR / 'ai_grid.js'
    grid_js = grid_file.read_text(encoding='utf-8') if grid_file.exists() else ''
    def sub_literal(pat, repl, s):
        return re.sub(pat, lambda m: repl, s)

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

    out = sub_literal(r'<script src="ai_grid\.js[^"]*"></script>', f'<script>\n{grid_js}\n</script>' if grid_js else '', out)
    out = sub_literal(r'<script src="toronto_map\.js[^"]*"></script>', f'<script>\n{toronto_map}\n</script>', out)
    out = sub_literal(r'<script src="city\.js[^"]*"></script>', f'<script>\n{city_js}\n</script>', out)
    out = sub_literal(r'<script src="traffic\.js[^"]*"></script>', f'<script>\n{traffic_js}\n</script>', out)
    out = sub_literal(r'<script src="multiplayer\.js[^"]*"></script>', f'<script>\n{multiplayer_js}\n</script>', out)
    out = sub_literal(r'<script src="ai_copilot\.js[^"]*"></script>', ai_inline, out)
    out = sub_literal(r'<script src="game\.js[^"]*"></script>', f'<script>\n{game_js}\n</script>', out)

    (BASE_DIR / 'play.html').write_text(out, encoding='utf-8')
    size_kb = len(out.encode('utf-8')) / 1024
    print(f"Successfully generated standalone play.html ({size_kb:.1f} KB)")

if __name__ == '__main__':
    bundle()
