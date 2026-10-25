"""Export AlgorithVideo platform icons and SVG wordmarks from the supplied logo.

Requires Pillow, fonttools and brotli. The original PNG is never redrawn or
modified; platform icons are size/format exports of that same artwork.
"""
from base64 import b64encode
from io import BytesIO
from pathlib import Path

from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'resources/algorithvideo-logo-source.png'
NAME = 'AlgorithVideo'


def wordmark():
    font = instantiateVariableFont(TTFont(ROOT / 'src/renderer/assets/fonts/Geist-Variable.woff2'), {'wght': 600})
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    x, paths = 0, []
    for char in NAME:
        name = cmap[ord(char)]
        pen = SVGPathPen(glyphs, ntos=lambda value: f'{value:.2f}'.rstrip('0').rstrip('.'))
        glyphs[name].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        paths.append(pen.getCommands())
        x += font['hmtx'][name][0] - 12
    return ''.join(paths), x + 12, font['OS/2'].sCapHeight


def main():
    raw = SOURCE.read_bytes()
    with Image.open(BytesIO(raw)) as source:
        if source.width != source.height or source.width < 1024:
            raise ValueError('The original logo must be a square PNG of at least 1024px.')
        master = source.convert('RGB')
        icon = master.resize((1024, 1024), Image.Resampling.LANCZOS)
        icon.save(ROOT / 'build/icon.png')
        icon.save(ROOT / 'build/icon.ico', sizes=[(size, size) for size in (16, 24, 32, 48, 64, 128, 256)])
        icon.save(ROOT / 'build/icon.icns', format='ICNS')
        for name, size in [('algorithvideo-icon.svg', 1024), ('algorithvideo-icon-small.svg', 128)]:
            output = BytesIO()
            master.resize((size, size), Image.Resampling.LANCZOS).save(output, format='PNG')
            data = b64encode(output.getvalue()).decode()
            (ROOT / 'resources' / name).write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" role="img" aria-label="{NAME}">\n'
                f'  <title>{NAME}</title><image width="{size}" height="{size}" href="data:image/png;base64,{data}"/>\n</svg>\n', encoding='utf-8', newline='\n')
    data = b64encode(raw).decode()
    image = f'<image width="1254" height="1254" href="data:image/png;base64,{data}"/>'
    # SVG viewport framing leaves the supplied PNG unchanged while making its
    # existing mark readable in the compact sidebar. No new emblem is drawn.
    mark = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="250 250 760 760" role="img" aria-label="{NAME}"><title>{NAME}</title>{image}</svg>\n'
    (ROOT / 'resources/algorithvideo-mark.svg').write_text(mark, encoding='utf-8', newline='\n')
    outline, advance, cap = wordmark()
    scale = 44 / cap
    width = 114 + advance * scale
    for filename, color in [('algorithvideo-logo.svg', '#fafafa'), ('algorithvideo-logo-light.svg', '#0a0a0a')]:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} 100" role="img" aria-label="{NAME}">\n'
        svg += f'  <title>{NAME}</title><svg width="100" height="100" viewBox="250 250 760 760">{image}</svg>\n'
        svg += f'  <path fill="{color}" transform="translate(114 70) scale({scale:.8f})" d="{outline}"/>\n</svg>\n'
        (ROOT / 'resources' / filename).write_text(svg, encoding='utf-8', newline='\n')
    print('Exported AlgorithVideo PNG, multi-size ICO, ICNS, compact mark and outlined wordmarks.')


if __name__ == '__main__':
    main()
