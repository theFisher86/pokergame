import io
import pygame
import cairosvg


def svg_to_surface(svg: str, size: tuple[int, int]) -> pygame.Surface:
    """Render an SVG string to a pygame surface at the given size."""
    png_bytes = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=size[0], output_height=size[1])
    return pygame.image.load(io.BytesIO(png_bytes)).convert_alpha()

FELT_SVG = """
<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64'>
  <rect width='64' height='64' fill='#157015'/>
  <circle cx='10' cy='10' r='2' fill='#1b7a1b'/>
  <circle cx='30' cy='5' r='2' fill='#1b7a1b'/>
  <circle cx='50' cy='20' r='2' fill='#1b7a1b'/>
  <circle cx='20' cy='40' r='2' fill='#1b7a1b'/>
  <circle cx='45' cy='50' r='2' fill='#1b7a1b'/>
</svg>
"""

CARD_BACK_SVG = """
<svg xmlns='http://www.w3.org/2000/svg' width='80' height='120'>
  <rect width='80' height='120' rx='8' ry='8' fill='#b00' stroke='#fff' stroke-width='4'/>
  <rect x='10' y='10' width='60' height='100' fill='none' stroke='#fff' stroke-width='2'/>
</svg>
"""
