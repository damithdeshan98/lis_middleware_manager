from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon, QPainter, QPainterPath, QPixmap


def create_app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(_render(size))
    return icon


def _render(size: int) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    pad  = max(1.0, size * 0.05)
    inn  = size - 2 * pad          # inner content dimension

    # ── Rounded-rect background ──────────────────────────────────── #
    bg = QPainterPath()
    bg.addRoundedRect(pad, pad, inn, inn, size * 0.22, size * 0.22)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor("#1e1e2e")))
    p.drawPath(bg)

    # ── Helpers ──────────────────────────────────────────────────── #
    def r(x, y, w, h) -> QRectF:
        return QRectF(pad + x * inn, pad + y * inn, w * inn, h * inn)

    cr = max(inn * 0.028, 1.0)      # shared corner radius for all parts

    p.setBrush(QBrush(QColor("#89b4fa")))
    p.setPen(Qt.PenStyle.NoPen)

    # ── Microscope parts (normalised coords 0-1 within inner area) ── #

    # Base — wide rounded bar at the bottom
    p.drawRoundedRect(r(0.07, 0.86, 0.86, 0.11), cr, cr)

    # Column — vertical body on the right
    p.drawRoundedRect(r(0.59, 0.22, 0.15, 0.66), cr, cr)

    # Arm — horizontal bridge at the top of the column
    p.drawRoundedRect(r(0.26, 0.22, 0.48, 0.12), cr, cr)

    # Eyepiece tube — short vertical tube above the arm (right side)
    p.drawRoundedRect(r(0.61, 0.05, 0.12, 0.19), cr, cr)

    # Eyepiece cap — wider ring at the very top
    p.drawRoundedRect(r(0.57, 0.04, 0.20, 0.07), cr, cr)

    # Objective tube — long vertical tube hanging from the left of the arm
    p.drawRoundedRect(r(0.32, 0.34, 0.11, 0.43), cr, cr)

    # Stage — horizontal platform through the objective tube
    p.drawRoundedRect(r(0.11, 0.49, 0.50, 0.09), cr, cr)

    # Objective lens — wider body at the bottom of the objective tube
    p.drawRoundedRect(r(0.23, 0.75, 0.29, 0.09), cr, cr)

    # Stage aperture — small dark circle (light hole through the stage)
    p.setBrush(QBrush(QColor("#1e1e2e")))
    p.drawEllipse(r(0.33, 0.50, 0.09, 0.07))

    p.end()
    return pix
