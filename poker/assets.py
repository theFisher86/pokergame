import io
import importlib
import importlib.util
import pygame
import skia


# pygame-svg is optional; fall back to skia if it's unavailable.
_pygame_svg = importlib.util.find_spec("pygame_svg")


def svg_to_surface(svg: str, size: tuple[int, int]) -> pygame.Surface:
    """Render an SVG string to a pygame surface at the given size."""
    width, height = size
    if _pygame_svg is not None:  # pragma: no cover - depends on optional package
        pygame_svg = importlib.import_module("pygame_svg")
        return pygame_svg.svg_to_surface(svg, width=width, height=height)

    stream = skia.MemoryStream(bytes(svg, "utf-8"))
    dom = skia.SVGDOM.MakeFromStream(stream)
    surface = skia.Surface(width, height)
    canvas = surface.getCanvas()
    canvas.clear(skia.ColorTRANSPARENT)
    dom.setContainerSize(skia.Size(width, height))
    dom.render(canvas)
    image = surface.makeImageSnapshot()
    return pygame.image.load(io.BytesIO(image.encodeToData().bytes())).convert_alpha()

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
