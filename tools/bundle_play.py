#!/usr/bin/env python3
"""
Bundle index.html, styles.css, toronto_map.js, city.js, and game.js
into a single standalone play.html file for offline play.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def bundle():
    index_html = (BASE_DIR / 'index.html').read_text(encoding='utf-8')
    styles_css = (BASE_DIR / 'styles.css').read_text(encoding='utf-8')
    toronto_map = (BASE_DIR / 'toronto_map.js').read_text(encoding='utf-8')
    city_js = (BASE_DIR / 'city.js').read_text(encoding='utf-8')
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
    game_tag = '<script src="game.js"></script>'

    out = out.replace(map_tag, f'<script>\n{toronto_map}\n</script>')
    out = out.replace(city_tag, f'<script>\n{city_js}\n</script>')
    out = out.replace(game_tag, f'<script>\n{game_js}\n</script>')

    (BASE_DIR / 'play.html').write_text(out, encoding='utf-8')
    size_kb = len(out.encode('utf-8')) / 1024
    print(f"Successfully generated standalone play.html ({size_kb:.1f} KB)")

if __name__ == '__main__':
    bundle()
