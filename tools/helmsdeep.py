"""Helm's Deep on a night of rain.

The Hornburg stands on its rock spur at the northern side of the gorge: the
curtain wall, the hall with its timber roof, and the great tower. From its foot
the Deeping Wall runs across the mouth of the gorge to the southern cliff, torches
burning along the parapet and the Deeping-stream running out through the culvert.
Behind, the dark horns of the Thrihyrne; to the south a far flash of lightning
lights the underside of the storm; in front, the wet floor of the Deeping-coomb.
"""
import math
import sys
from scene_kit import Scene, W, H, f

C = dict(
    bg="#13161a",
    sky=[(0, "#07090c"), (.5, "#121820"), (1, "#202833")],
    flash="#b9c8da", flash_core="#e6eef7",
    cloud="#151a21", cloud_mid="#1d242d", cloud_lit="#56657a",
    peak="#1f262f", peak_lit="#3b4757", snow="#8d9aab",
    cliff="#161b21", cliff_face="#1c2229", cliff_lit="#33404e",
    stone="#2a3037", stone_dark="#20252b", stone_lit="#4b5560",
    wood="#3a2c1f", wood_dark="#271d14",
    fire="#f4b65a", fire_core="#fff0c4", glow="#d7b45e", window="#e8b763",
    coomb="#171c20", coomb_far="#1c2227", water="#3d4a57",
    rain="#a9b6c6",
)

WALL_L, WALL_R = 652, 1022     # the Deeping Wall runs between these x
WALL_TOP_L, WALL_TOP_R = 203, 209
WALL_H = 36


def hexrgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    A, B = hexrgb(a), hexrgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(A, B))


def poly(pts, close=True):
    return "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + ("Z" if close else "")


def jag(sc, pts, n=3, amt=.12):
    """Roughen a polyline by midpoint displacement so rock edges look broken."""
    out = list(pts)
    for _ in range(n):
        nxt = [out[0]]
        for (ax, ay), (bx, by) in zip(out, out[1:]):
            d = math.hypot(bx - ax, by - ay)
            nxt.append(((ax + bx) / 2 + sc.r(-1, 1) * d * amt * .4, (ay + by) / 2 + sc.r(-1, 1) * d * amt))
            nxt.append((bx, by))
        out = nxt
    return out


def wall_top(x):
    return WALL_TOP_L + (WALL_TOP_R - WALL_TOP_L) * (x - WALL_L) / (WALL_R - WALL_L)


def torch(sc, x, y, s=1.0):
    """A torch on a short pole: a warm halo, the flame, and a hot core."""
    sc.add(f'<circle cx="{f(x)}" cy="{f(y - 7 * s)}" r="{f(22 * s)}" fill="url(#halo)"/>'
           f'<rect x="{f(x - .7 * s)}" y="{f(y - 6 * s)}" width="{f(1.4 * s)}" height="{f(7 * s)}" fill="{C["wood_dark"]}"/>'
           f'<path d="M{f(x - 2.2 * s)},{f(y - 6 * s)} Q{f(x - 2 * s)},{f(y - 10 * s)} {f(x + .6 * s)},{f(y - 13.5 * s)} Q{f(x + .4 * s)},{f(y - 10 * s)} {f(x + 2.2 * s)},{f(y - 6 * s)}Z" fill="{C["fire"]}"/>'
           f'<ellipse cx="{f(x)}" cy="{f(y - 7.5 * s)}" rx="{f(.9 * s)}" ry="{f(1.6 * s)}" fill="{C["fire_core"]}"/>')


def crenels(x0, y0, x1, y1, merlon, gap, h):
    """Battlements along a sloping top edge from (x0,y0) to (x1,y1): returns path data for the merlons."""
    d = ""
    x = x0
    while x < x1 - 1:
        xe = min(x + merlon, x1)
        ya = y0 + (y1 - y0) * (x - x0) / ((x1 - x0) or 1)
        yb = y0 + (y1 - y0) * (xe - x0) / ((x1 - x0) or 1)
        d += f"M{f(x)},{f(ya)} L{f(x)},{f(ya - h)} L{f(xe)},{f(yb - h)} L{f(xe)},{f(yb)}Z "
        x += merlon + gap
    return d


def cliff_faces(sc, edge, x0, x1, face, lit_col, lx):
    """Long vertical facets hanging from a cliff's crest, like the jointed rock of the White Mountains."""
    x = x0
    g = []
    while x < x1:
        w = sc.r(8, 22)
        yt = Scene.y_at(edge, x + w * .5) + sc.r(2, 8)
        ln = sc.r(40, 140)
        lit = max(0.0, 1 - abs(x - lx) / 420)
        col = mix(face, lit_col, lit * .7) if sc.r(0, 1) < .6 else mix(face, "#000000", .25)
        g.append(f'<path d="{poly([(x, yt), (x + w, yt + sc.r(-3, 3)), (x + w * sc.r(.6, 1), yt + ln), (x + w * .3, yt + ln * sc.r(.7, 1.1))])}" fill="{col}" opacity="{f(sc.r(.5, .9))}"/>')
        x += w + sc.r(4, 26)
    sc.add("".join(g))


def build(seed=21):
    sc = Scene(seed)
    sc.defs.append(f'<radialGradient id="halo"><stop offset="0" stop-color="{C["glow"]}" stop-opacity=".55"/>'
                   f'<stop offset=".35" stop-color="{C["glow"]}" stop-opacity=".18"/><stop offset="1" stop-color="{C["glow"]}" stop-opacity="0"/></radialGradient>')
    # rain: three tiled sheets at different weights, slanting with the wind
    for rid, size, n, op, sw, ln, ang in [("r1", 97, 18, .16, .7, (10, 22), 14), ("r2", 151, 16, .22, .9, (16, 34), 15), ("r3", 223, 10, .3, 1.1, (26, 52), 16)]:
        lines = ""
        for _ in range(n):
            x, y, l = sc.r(0, size), sc.r(0, size), sc.r(*ln)
            lines += f"M{f(x)},{f(y)}v{f(l)}"
            if y + l > size:  # wrap so the tile is seamless
                lines += f"M{f(x)},{f(y - size)}v{f(l)}"
        sc.defs.append(f'<pattern id="{rid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse" patternTransform="rotate({ang})">'
                       f'<path d="{lines}" stroke="{C["rain"]}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round"/></pattern>')

    # ---------- sky and storm ----------
    sc.sky(sc.lin("sky", C["sky"]))
    lx, ly = 1250, 70   # the lightning, far off to the south, behind the cloud
    sc.defs.append(f'<radialGradient id="litbody" gradientUnits="userSpaceOnUse" cx="{lx}" cy="{ly}" r="600">'
                   f'<stop offset="0" stop-color="{C["cloud_lit"]}"/><stop offset=".35" stop-color="#262e39"/>'
                   f'<stop offset="1" stop-color="{C["cloud"]}"/></radialGradient>')
    # the glow of the flash behind the cloud, and a gap of paler sky low behind the peaks
    sc.add(f'<rect y="60" width="{W}" height="180" fill="{sc.lin("low", [(0, "#2b3542", 0), (.7, "#2b3542", .6), (1, "#2b3542", .2)])}"/>')
    sc.add(f'<ellipse cx="{lx}" cy="{ly + 10}" rx="460" ry="200" fill="{sc.rad("flash", [(0, C["flash"], .6), (.3, C["flash"], .22), (1, C["flash"], 0)])}"/>')

    sc.defs.append('<filter id="soft" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="2.6"/></filter>'
                   '<filter id="softer" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>')

    def bank(y, amp, wmin, wmax, op=1.0):
        """A bank of storm cloud hanging from the top, with a lumpy underside."""
        under = []
        x = -40
        while x < W + 40:
            w = sc.r(wmin, wmax)
            yb = y + sc.r(-amp, amp)
            under.append((x, yb, w))
            x += w
        d = f"M-40,-10 L{W + 40},-10 L{W + 40},{f(under[-1][1])} "
        for (x0, y0, w) in reversed(under):
            bulge = w * sc.r(.18, .32)
            d += f"Q{f(x0 + w / 2)},{f(y0 + bulge)} {f(x0)},{f(y0)} "
        d += "Z"
        # cloud behind this bank, lit by the flash, so the bank's edge stands dark against it
        glow = ""
        for (x0, y0, w) in under:
            cxp = x0 + w / 2
            dist = math.hypot(cxp - lx, (y0 - ly) * 1.4)
            if dist < 520:
                k = (1 - dist / 520) ** 1.3
                glow += (f'<ellipse cx="{f(cxp + sc.r(-10, 10))}" cy="{f(y0 + w * .22)}" rx="{f(w * .75)}" ry="{f(w * .3)}" '
                         f'fill="{C["flash"]}" opacity="{f(.38 * k * op)}"/>')
        if glow:
            sc.add(f'<g filter="url(#softer)">{glow}</g>')
        sc.add(f'<g filter="url(#soft)" opacity="{f(op)}"><path d="{d}" fill="url(#litbody)"/></g>')

    bank(150, 10, 70, 150, .55)
    bank(118, 14, 90, 170, .8)
    bank(84, 16, 100, 200)
    bank(46, 12, 120, 220)
    sc.add(f'<rect width="{W}" height="70" fill="{sc.lin("skyveil", [(0, "#07090c", .7), (1, "#07090c", 0)])}"/>')

    # ---------- the Thrihyrne: three horns behind the gorge ----------
    horns = [(640, 64), (792, 30), (958, 56)]
    outline = jag(sc, [(470, 232), (560, 160), (606, 104), horns[0], (668, 100), (708, 108), (752, 66), horns[1], (826, 62),
                       (872, 104), (912, 96), horns[2], (994, 98), (1060, 150), (1170, 232)], 3, .08)
    sc.add(f'<path d="{poly(outline)}" fill="{C["peak"]}"/>')
    # each horn's right flank faces the flash: a lit facet from the summit down
    for (hx, hy), w in zip(horns, (40, 52, 44)):
        facet = jag(sc, [(hx, hy), (hx + w * .55, hy + 46), (hx + w, hy + 120)], 2, .1) + [(hx + w * .25, hy + 150), (hx + 4, hy + 60)]
        sc.add(f'<path d="{poly(facet)}" fill="{C["peak_lit"]}" opacity=".55"/>')
        sc.add(f'<path d="M{hx},{hy} L{f(hx + w * .55)},{f(hy + 46)}" stroke="{C["flash"]}" stroke-opacity=".25" stroke-width="1.2"/>')
        for k in range(5):  # snow lying in the gullies
            a0 = sc.r(-.6, .7)
            l = sc.r(12, 30)
            sc.add(f'<path d="M{f(hx + sc.r(-8, 10))},{f(hy + 10 + k * 7)} l{f(a0 * l * .4)},{f(l)}" stroke="{C["snow"]}" stroke-opacity="{f(sc.r(.12, .28))}" stroke-width="{f(sc.r(.8, 1.8))}" stroke-linecap="round"/>')
    sc.add(f'<rect y="40" width="{W}" height="200" fill="{sc.lin("haze1", [(0, "#2a333e", 0), (.6, "#2a333e", .35), (1, "#2a333e", .55)])}"/>')
    sc.add(f'<rect width="{W}" height="{H}" fill="url(#r1)"/>')

    # ---------- the gorge: the Deep running back between its cliffs ----------
    sc.ridge(214, 5, [(2.3, 1), (5.1, .5)], "#1a2028", seed=3.3, x0=540, x1=1120, taper=60)
    # the inner walls of the gorge closing in toward the Deep
    sc.add(f'<path d="{poly(jag(sc, [(640, 196), (690, 150), (735, 158), (770, 196), (790, 222)], 2, .1) + [(640, 230)])}" fill="#1b2129"/>')
    sc.add(f'<path d="{poly(jag(sc, [(1030, 200), (980, 140), (930, 150), (890, 196), (866, 222)], 2, .1) + [(1030, 230)])}" fill="#1d242c"/>')
    sc.add(f'<path d="M980,140 L1000,170 L1030,200" fill="none" stroke="{C["cliff_lit"]}" stroke-opacity=".6" stroke-width="1.2"/>')
    for i in range(10):  # fires of the refugees far back in the Deep
        x = sc.r(690, 980)
        y = sc.r(214, 222)
        sc.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(sc.r(.8, 1.4))}" fill="{C["fire"]}" opacity="{f(sc.r(.35, .7))}"/>')
    # the north cliff, behind and above the Hornburg
    north = jag(sc, [(-20, 118), (60, 96), (150, 112), (230, 82), (300, 104), (370, 92), (440, 120), (520, 146), (590, 168), (640, 196), (668, 236)], 3, .14)
    sc.add(f'<path d="{poly(north + [(668, H), (-20, H)])}" fill="{C["cliff"]}"/>')
    cliff_faces(sc, north, 0, 640, C["cliff_face"], C["cliff_face"], lx)
    # the south cliff, with the lightning on its crest
    south = jag(sc, [(1000, 240), (1020, 204), (1048, 168), (1090, 140), (1150, 126), (1210, 104), (1280, 116), (1350, 96), (1430, 110), (1500, 88), (1560, 102), (1620, 96)], 3, .14)
    sc.add(f'<path d="{poly(south + [(1620, H), (1000, H)])}" fill="{C["cliff"]}"/>')
    sc.add(f'<path d="{poly(south, False)}" fill="none" stroke="{C["cliff_lit"]}" stroke-width="1.6" stroke-opacity=".8"/>')
    cliff_faces(sc, south, 1030, 1610, C["cliff_face"], C["cliff_lit"], lx)
    # the inner face of the gorge where the wall meets the southern cliff
    sc.add(f'<path d="M1000,240 L1022,{WALL_TOP_R - 8} L1040,180 L1030,250Z" fill="{C["cliff_face"]}"/>')

    # ---------- the Deeping Wall ----------
    bot = WALL_TOP_L + WALL_H
    face = [(WALL_L, WALL_TOP_L), (WALL_R, WALL_TOP_R), (WALL_R + 6, WALL_TOP_R + WALL_H + 4), (WALL_L, bot + 2)]
    sc.add(f'<path d="{poly(face)}" fill="{sc.lin("wallg", [(0, C["stone"]), (.7, C["stone_dark"]), (1, "#1a1e23")])}"/>')
    # coursed stone
    d = ""
    for k in range(1, 7):
        ya, yb = WALL_TOP_L + k * 5.4, WALL_TOP_R + k * 5.4
        d += f"M{WALL_L},{f(ya)} L{WALL_R + k},{f(yb)} "
        off = 9 if k % 2 else 0
        x = WALL_L + off
        while x < WALL_R:
            y = wall_top(x) + k * 5.4
            d += f"M{f(x)},{f(y - 5.4)} v5.4 "
            x += 18
    sc.add(f'<path d="{d}" stroke="#000" stroke-opacity=".28" stroke-width=".7"/>')
    # the parapet and its merlons on the outer side
    sc.add(f'<path d="{poly([(WALL_L, WALL_TOP_L), (WALL_R, WALL_TOP_R), (WALL_R, WALL_TOP_R - 4), (WALL_L, WALL_TOP_L - 4)])}" fill="{C["stone"]}"/>')
    sc.add(f'<path d="{crenels(WALL_L, WALL_TOP_L - 4, WALL_R, WALL_TOP_R - 4, 7, 5, 5)}" fill="{C["stone"]}"/>')
    sc.add(f'<path d="M{WALL_L},{WALL_TOP_L - 4} L{WALL_R},{WALL_TOP_R - 4}" stroke="{C["stone_lit"]}" stroke-opacity=".5" stroke-width=".8"/>')
    # buttresses
    for x in range(WALL_L + 60, WALL_R - 20, 74):
        y = wall_top(x)
        sc.add(f'<path d="M{x - 5},{f(y + 4)} L{x + 5},{f(y + 4)} L{x + 9},{f(bot + (y - WALL_TOP_L) + 3)} L{x - 9},{f(bot + (y - WALL_TOP_L) + 3)}Z" fill="{C["stone_dark"]}"/>'
               f'<path d="M{x - 5},{f(y + 4)} L{x - 9},{f(bot + (y - WALL_TOP_L) + 3)}" stroke="{C["stone_lit"]}" stroke-opacity=".25" stroke-width="1"/>')
    # the culvert where the Deeping-stream runs out under the wall
    cx = 842
    cy = wall_top(cx) + WALL_H + 3
    sc.add(f'<path d="M{cx - 10},{f(cy)} L{cx - 10},{f(cy - 9)} Q{cx},{f(cy - 17)} {cx + 10},{f(cy - 9)} L{cx + 10},{f(cy)}Z" fill="#07090b"/>')
    sc.add(f'<path d="M{cx - 7},{f(cy - 10)} V{f(cy)} M{cx - 2},{f(cy - 13)} V{f(cy)} M{cx + 3},{f(cy - 13)} V{f(cy)} M{cx + 8},{f(cy - 10)} V{f(cy)}" stroke="#3a4048" stroke-width="1"/>')
    # torchlight washing the top of the wall
    sc.add(f'<path d="{poly([(WALL_L, WALL_TOP_L - 2), (WALL_R, WALL_TOP_R - 2), (WALL_R, WALL_TOP_R + 10), (WALL_L, WALL_TOP_L + 10)])}" fill="{sc.lin("wash", [(0, C["glow"], .16), (1, C["glow"], 0)])}"/>')

    # ---------- the Hornburg on its spur ----------
    spur = jag(sc, [(360, 300), (378, 252), (396, 222), (420, 202), (470, 194), (560, 192), (622, 196), (656, 210), (676, 238), (690, 300)], 2, .1)
    sc.add(f'<path d="{poly(spur)}" fill="{C["cliff_face"]}"/>')
    sc.add(f'<path d="{poly([(396, 222), (420, 202), (470, 196), (430, 240), (400, 270)])}" fill="{C["cliff"]}" opacity=".8"/>')
    for i in range(8):  # rock seams
        x = sc.r(400, 660)
        y = sc.r(210, 250)
        sc.add(f'<path d="M{f(x)},{f(y)} l{f(sc.r(-8, 8))},{f(sc.r(10, 26))}" stroke="#000" stroke-opacity=".3" stroke-width="1"/>')
    # the hall: stone below, a steep timber roof above
    hx0, hx1, hy = 548, 628, 172
    sc.add(f'<rect x="{hx0}" y="{hy}" width="{hx1 - hx0}" height="20" fill="{C["stone_dark"]}"/>'
           f'<path d="M{hx0 - 6},{hy + 1} L{(hx0 + hx1) / 2},{hy - 26} L{hx1 + 6},{hy + 1}Z" fill="{C["wood"]}"/>'
           f'<path d="M{(hx0 + hx1) / 2},{hy - 26} L{hx1 + 6},{hy + 1} L{(hx0 + hx1) / 2 + 6},{hy + 1}Z" fill="{C["wood_dark"]}" opacity=".7"/>')
    d = ""
    for k in range(1, 6):
        t = k / 6
        d += f"M{f(hx0 - 6 + ((hx0 + hx1) / 2 - hx0 + 6) * t)},{f(hy + 1 - 27 * t)} L{f(hx1 + 6 - (hx1 + 6 - (hx0 + hx1) / 2) * t)},{f(hy + 1 - 27 * t)} "
    sc.add(f'<path d="{d}" stroke="#000" stroke-opacity=".3" stroke-width=".8"/>')
    # carved gable ends crossing above the ridge, as on the halls of Rohan
    gx = (hx0 + hx1) / 2
    sc.add(f'<path d="M{f(gx - 7)},{hy - 33} L{f(gx)},{hy - 25} L{f(gx + 7)},{hy - 33}" fill="none" stroke="{C["wood"]}" stroke-width="2.2" stroke-linecap="round"/>')
    sc.add(f'<rect x="{gx - 1.2}" y="{hy - 40}" width="2.4" height="9" fill="{C["wood_dark"]}"/>')  # a bare flagpole, no banner
    # the great tower: broad, battered at the foot, a stair turret on its shoulder
    tx0, tx1, tt = 470, 534, 84
    tm = (tx0 + tx1) / 2
    sc.add(f'<rect x="{tx0 - 16}" y="{tt + 30}" width="20" height="{196 - tt - 30}" fill="{C["stone_dark"]}"/>'
           f'<path d="{crenels(tx0 - 17, tt + 30, tx0 + 4, tt + 30, 4, 3.5, 4)}" fill="{C["stone_dark"]}"/>'
           f'<path d="M{tx0 - 19},{tt + 26} L{tx0 - 6},{tt + 12} L{tx0 + 5},{tt + 26}Z" fill="{C["wood_dark"]}"/>')
    sc.add(f'<path d="M{tx0},{tt} L{tx1},{tt} L{tx1},{168} L{tx1 + 6},196 L{tx0 - 6},196 L{tx0},168Z" fill="{C["stone"]}"/>'
           f'<path d="M{tx1 - 22},{tt} L{tx1},{tt} L{tx1},168 L{tx1 + 6},196 L{tx1 - 22},196Z" fill="{C["stone_lit"]}" opacity=".3"/>')
    d = ""
    for y in range(tt + 8, 168, 8):
        d += f"M{tx0},{y} H{tx1} "
        x = tx0 + (6 if (y // 8) % 2 else 0)
        while x < tx1:
            d += f"M{x},{y - 8} v8 "
            x += 13
    sc.add(f'<path d="{d}" stroke="#000" stroke-opacity=".2" stroke-width=".7"/>')
    sc.add(f'<path d="M{tx0},168 H{tx1}" stroke="#000" stroke-opacity=".35" stroke-width="1.4"/>')
    # a corbelled fighting-gallery at the top, battlements, and a low timber roof
    sc.add(f'<rect x="{tx0 - 5}" y="{tt - 8}" width="{tx1 - tx0 + 10}" height="9" fill="{C["stone_dark"]}"/>')
    d = ""
    for k in range(9):
        d += f"M{f(tx0 - 4 + k * 8.4)},{tt + 1} l2.2,6 l2.2,-6Z"
    sc.add(f'<path d="{d}" fill="{C["stone_dark"]}"/>')
    sc.add(f'<path d="{crenels(tx0 - 5, tt - 8, tx1 + 5, tt - 8, 5, 4, 6)}" fill="{C["stone_dark"]}"/>')
    sc.add(f'<path d="M{tx0 + 4},{tt - 11} L{tm - 10},{tt - 27} L{tm + 10},{tt - 27} L{tx1 - 4},{tt - 11}Z" fill="{C["wood"]}"/>'
           f'<path d="M{tm + 10},{tt - 27} L{tx1 - 4},{tt - 11} L{tm + 14},{tt - 11}Z" fill="{C["flash"]}" opacity=".14"/>'
           f'<path d="M{tm - 10},{tt - 27} L{tm + 10},{tt - 27}" stroke="{C["flash"]}" stroke-opacity=".3" stroke-width="1"/>')
    # lit slits and windows: a few on the tower, a row along the hall
    for x, y, w, h in [(tm - 2, 104, 4, 9), (tm - 2, 134, 4, 9), (tx0 + 10, 118, 2.5, 7), (tx1 - 13, 146, 2.5, 7), (tx0 - 8, 140, 2.5, 6),
                       (560, 178, 4, 6), (578, 178, 4, 6), (596, 178, 4, 6), (614, 178, 4, 6)]:
        sc.add(f'<circle cx="{f(x + w / 2)}" cy="{f(y + h / 2)}" r="{f(h * 1.3)}" fill="url(#halo)" opacity=".6"/>'
               f'<rect x="{f(x)}" y="{y}" width="{w}" height="{h}" fill="{C["window"]}"/>')
    # the curtain wall round the top of the rock, stepping down to meet the Deeping Wall
    cw = [(404, 214), (418, 196), (470, 190), (548, 190), (630, 192), (660, 200)]
    cwb = [(668, 230), (640, 214), (560, 210), (470, 212), (430, 222), (410, 236)]
    sc.add(f'<path d="{poly(cw + cwb)}" fill="{C["stone"]}"/>')
    sc.add(f'<path d="{poly(cw + [(660, 204), (630, 196), (548, 194), (470, 194), (418, 200), (404, 218)])}" fill="{C["stone_lit"]}" opacity=".22"/>')
    d = ""
    for k in (1, 2, 3):
        d += "M" + " L".join(f"{f(x)},{f(y + k * 6)}" for x, y in cw) + " "
    sc.add(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity=".25" stroke-width=".7"/>')
    d = ""
    for (ax, ay), (bx, by) in zip(cw, cw[1:]):
        d += crenels(ax, ay, bx, by, 5, 4, 4.5)
    sc.add(f'<path d="{d}" fill="{C["stone"]}"/>')
    # the gate tower at the end of the causeway, with timber gates
    gx0, gx1, gt = 636, 664, 188
    sc.add(f'<rect x="{gx0}" y="{gt}" width="{gx1 - gx0}" height="{238 - gt}" fill="{C["stone"]}"/>'
           f'<path d="{crenels(gx0, gt, gx1, gt, 4, 4, 5)}" fill="{C["stone"]}"/>'
           f'<path d="M{gx0 + 6},236 V{f(222)} Q{(gx0 + gx1) / 2},{f(212)} {gx1 - 6},222 V236Z" fill="{C["wood"]}"/>'
           f'<path d="M{gx0 + 6},226 H{gx1 - 6} M{gx0 + 6},231 H{gx1 - 6} M{(gx0 + gx1) / 2},214 V236" stroke="#000" stroke-opacity=".45" stroke-width=".8"/>')
    # the causeway ramp sweeping down into the coomb
    sc.add(f'<path d="M{gx0 + 4},238 L{gx1 + 4},238 L780,262 L730,266Z" fill="{C["stone_dark"]}"/>'
           f'<path d="M{gx1 + 4},238 L780,262" stroke="{C["stone_lit"]}" stroke-opacity=".3" stroke-width="1"/>')

    # torches: along the Deeping Wall, on the Hornburg, at the gate
    for x in range(WALL_L + 22, WALL_R - 4, 42):
        torch(sc, x, wall_top(x) - 4, .9)
    for x, y, s in [(424, 194, .8), (470, 188, .8), (540, 188, .8), (604, 190, .8), (gx0 - 2, 222, .9), (gx1 + 2, 222, .9)]:
        torch(sc, x, y, s)
    sc.add(f'<rect width="{W}" height="{H}" fill="url(#r2)"/>')

    # ---------- the Deeping-coomb ----------
    # scree fans at the feet of the cliffs, settling into the valley floor
    sc.ridge(236, 10, [(1.6, 1), (4.2, .4)], "#191e24", seed=2.2, x0=-20, x1=430, taper=120)
    sc.ridge(240, 8, [(1.3, 1), (3.6, .5)], "#1a2026", seed=5.1, x0=1000, x1=W + 20, taper=120)
    coomb = sc.ridge(252, 4, [(1.4, 1), (3.7, .5)], C["coomb_far"], seed=1.9, taper=0)
    # the green dike across the coomb, a long low earthwork
    dike = sc.ridge(286, 3, [(1.1, 1), (2.6, .4)], "#1a1f24", seed=4.4, taper=0)
    # stones and tussocks in the wet grass
    for _ in range(26):
        x = sc.r(0, W)
        y = Scene.y_at(coomb, x) + sc.r(4, 30)
        s = sc.r(3, 9)
        sc.add(f'<path d="{poly([(x - s, y), (x - s * .6, y - s * .7), (x + s * .3, y - s * .8), (x + s, y)])}" fill="{mix(C["coomb"], C["stone_dark"], sc.r(.3, .8))}"/>')
    sc.tufts(256, 330, 260, ["#1b2226", "#20282c", "#161c20", "#242c30"], 4, 11)
    sc.ridge(322, 5, [(2.0, 1), (4.6, .4)], C["coomb"], seed=6.2)
    # the Deeping-stream, catching the torchlight as it leaves the culvert
    stream = f"M{cx},{f(cy)} C{cx + 6},{f(cy + 12)} 880,262 930,272 S1060,290 1000,312 S860,340 900,400"
    sc.add(f'<path d="{stream}" fill="none" stroke="{C["water"]}" stroke-width="2.6" stroke-linecap="round"/>'
           f'<path d="{stream}" fill="none" stroke="{C["glow"]}" stroke-opacity=".25" stroke-width="1" stroke-dasharray="6 14" stroke-linecap="round"/>')
    sc.tufts(322, 400, 220, ["#161b1f", "#1a2024", "#13171b"], 6, 15)

    # heaviest rain nearest, and the mist it raises
    sc.add(f'<rect y="180" width="{W}" height="100" fill="{sc.lin("mist", [(0, "#2a333e", 0), (.6, "#2a333e", .22), (1, "#2a333e", 0)])}"/>')
    sc.add(f'<rect width="{W}" height="{H}" fill="url(#r3)"/>')
    sc.add(f'<rect y="280" width="{W}" height="120" fill="{sc.lin("near", [(0, C["bg"], 0), (1, C["bg"], .85)])}"/>')
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build().save(f"{out}/helmsdeep.svg", "Helm's Deep in the rain")
