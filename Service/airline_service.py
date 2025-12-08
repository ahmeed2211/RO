from PyQt5 import Qt
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor
from PyQt5.QtCore import QSize
import requests

def load_svg_icon(url, size=40):
    """
    Load an SVG from a URL and return a QIcon.
    If the download fails, returns an empty icon.
    """
    try:
        data = requests.get(url).content
        svg_renderer = QSvgRenderer(data)
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0,0,0,0))
        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
    except Exception as e:
        print(f"Failed to load SVG: {url} -> {e}")
        return QIcon()
