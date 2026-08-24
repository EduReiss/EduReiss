#!/usr/bin/env python3
"""
Gera um painel SVG de projetos em destaque a partir de um projects.json,
em duas variantes (clara e escura), sem depender de nenhum serviço externo.

Uso: python3 generate_projects.py projects.json out/
"""

import json
import sys
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

COLS = 2
CARD_W = 430
CARD_H = 150
GAP = 20
PADDING = 10
FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', Helvetica, Arial, sans-serif"

THEMES = {
    "light": {
        "bg": "#ffffff",
        "card_bg": "#f5f5f7",
        "border": "#d1d1d6",
        "title": "#1d1d1f",
        "text": "#48484A",
        "tag_bg": "#e8e8ed",
        "tag_text": "#1d1d1f",
    },
    "dark": {
        "bg": "#00000000",
        "card_bg": "#1c1c1e",
        "border": "#3a3a3c",
        "title": "#ffffff",
        "text": "#A0A0A5",
        "tag_bg": "#2c2c2e",
        "tag_text": "#ffffff",
    },
}


def wrap_text(text, width=52, max_lines=2):
    lines = textwrap.wrap(text, width=width)[:max_lines]
    if len(lines) == max_lines and len(textwrap.wrap(text, width=width)) > max_lines:
        lines[-1] = lines[-1].rstrip(".") + "…"
    return lines


def render_card(x, y, project, theme):
    name = escape(project["name"])
    repo_url = f"https://github.com/{project['repo']}"
    desc_lines = wrap_text(project.get("description", ""))
    tags = project.get("tags", [])

    parts = [
        f'<a href="{escape(repo_url)}" target="_blank">',
        f'<rect x="{x}" y="{y}" width="{CARD_W}" height="{CARD_H}" rx="14" '
        f'fill="{theme["card_bg"]}" stroke="{theme["border"]}" stroke-width="1"/>',
        f'<text x="{x + PADDING + 10}" y="{y + 34}" font-family="{FONT}" '
        f'font-size="17" font-weight="700" fill="{theme["title"]}">{name}</text>',
    ]

    desc_y = y + 58
    for line in desc_lines:
        parts.append(
            f'<text x="{x + PADDING + 10}" y="{desc_y}" font-family="{FONT}" '
            f'font-size="13" fill="{theme["text"]}">{escape(line)}</text>'
        )
        desc_y += 19

    tag_x = x + PADDING + 10
    tag_y = y + CARD_H - 28
    for tag in tags:
        tag_w = 14 + len(tag) * 6.5
        parts.append(
            f'<rect x="{tag_x}" y="{tag_y}" width="{tag_w:.0f}" height="22" rx="11" '
            f'fill="{theme["tag_bg"]}"/>'
        )
        parts.append(
            f'<text x="{tag_x + tag_w / 2:.0f}" y="{tag_y + 15}" font-family="{FONT}" '
            f'font-size="11" fill="{theme["tag_text"]}" text-anchor="middle">{escape(tag)}</text>'
        )
        tag_x += tag_w + 8

    parts.append("</a>")
    return "\n".join(parts)


def render_panel(projects, theme_name):
    theme = THEMES[theme_name]
    rows = (len(projects) + COLS - 1) // COLS
    width = COLS * CARD_W + (COLS - 1) * GAP
    height = rows * CARD_H + (rows - 1) * GAP

    body = []
    for i, project in enumerate(projects):
        col = i % COLS
        row = i // COLS
        x = col * (CARD_W + GAP)
        y = row * (CARD_H + GAP)
        body.append(render_card(x, y, project, theme))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="{width}" height="{height}" fill="{theme["bg"]}"/>
{chr(10).join(body)}
</svg>'''
    return svg


def main():
    if len(sys.argv) < 3:
        print("Uso: generate_projects.py projects.json out_dir/")
        sys.exit(1)

    projects_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    projects = json.loads(projects_path.read_text(encoding="utf-8"))

    for theme_name in THEMES:
        svg = render_panel(projects, theme_name)
        out_path = out_dir / f"projects-{theme_name}.svg"
        out_path.write_text(svg, encoding="utf-8")
        print(f"Gerado: {out_path}")


if __name__ == "__main__":
    main()
