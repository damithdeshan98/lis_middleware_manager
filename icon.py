import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon, QPainter, QPainterPath, QPixmap


def create_app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(_render(size))
    return icon


def _gear_path(cx: float, cy: float, outer_r: float, inner_r: float, teeth: int) -> QPainterPath:
    path = QPainterPath()
    step = 2 * math.pi / teeth
    half = step * 0.18
    first = True
    for i in range(teeth):
        a = i * step - math.pi / 2
        for r, da in [
            (inner_r, -step * 0.38),
            (outer_r, -half),
            (outer_r,  half),
            (inner_r,  step * 0.38),
        ]:
            x = cx + r * math.cos(a + da)
            y = cy + r * math.sin(a + da)
            if first:
                path.moveTo(x, y)
                first = False
            else:
                path.lineTo(x, y)
    path.closeSubpath()
    return path


def _render(size: int) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    cx = cy = size / 2.0
    pad = max(1.0, size * 0.04)

    # Rounded-rect background
    bg = QPainterPath()
    radius = size * 0.22
    bg.addRoundedRect(pad, pad, size - 2 * pad, size - 2 * pad, radius, radius)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor("#1e1e2e")))
    p.drawPath(bg)

    # Gear shape
    teeth   = 6 if size <= 24 else 8
    outer_r = size * 0.375
    inner_r = size * 0.268
    hole_r  = size * 0.098

    gear = _gear_path(cx, cy, outer_r, inner_r, teeth)
    hole = QPainterPath()
    hole.addEllipse(QPointF(cx, cy), hole_r, hole_r)
    final_gear = gear.subtracted(hole)

    p.setBrush(QBrush(QColor("#89b4fa")))
    p.drawPath(final_gear)

    p.end()
    return pix
