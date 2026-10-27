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

WALL_L, WALL_R = 912, 1236    # the Deeping Wall runs between these x
WALL_TOP_L, WALL_TOP_R = 196, 202
WALL_H = 50
RAIN_P = 200                  # the rain repeats every RAIN_P px so the viewer can loop it


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
    sc.add(f'<g><circle cx="{f(x)}" cy="{f(y - 7 * s)}" r="{f(22 * s)}" fill="url(#halo)"/>'
           f'<rect x="{f(x - .7 * s)}" y="{f(y - 6 * s)}" width="{f(1.4 * s)}" height="{f(7 * s)}" fill="{C["wood_dark"]}"/>'
           f'<path d="M{f(x - 2.2 * s)},{f(y - 6 * s)} Q{f(x - 2 * s)},{f(y - 10 * s)} {f(x + .6 * s)},{f(y - 13.5 * s)} Q{f(x + .4 * s)},{f(y - 10 * s)} {f(x + 2.2 * s)},{f(y - 6 * s)}Z" fill="{C["fire"]}"/>'
           f'<ellipse cx="{f(x)}" cy="{f(y - 7.5 * s)}" rx="{f(.9 * s)}" ry="{f(1.6 * s)}" fill="{C["fire_core"]}"/></g>')


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


def rain(sc, n, op, sw, ln, slant=.26):
    """A sheet of rain: streaks scattered over a band RAIN_P tall, drawn at -P, 0 and +P so the loop is seamless."""
    d = ""
    for _ in range(n):
        x, y, l = sc.r(-40, W + 60), sc.r(0, RAIN_P), sc.r(*ln)
        d += f"M{x:.0f},{y:.0f}l{f(-l * slant)},{f(l)}"
    with sc.fx("rain", RAIN_P):
        sc.add(f'<g stroke="{C["rain"]}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round">'
               + "".join(f'<path d="{d}" transform="translate(0 {o})"/>' for o in (-RAIN_P, 0, RAIN_P)) + "</g>")


def build(seed=21):
    sc = Scene(seed)
    sc.defs.append(f'<radialGradient id="halo"><stop offset="0" stop-color="{C["glow"]}" stop-opacity=".55"/>'
                   f'<stop offset=".35" stop-color="{C["glow"]}" stop-opacity=".18"/><stop offset="1" stop-color="{C["glow"]}" stop-opacity="0"/></radialGradient>')
    sc.defs.append('<filter id="soft" x="-5%" y="-20%" width="110%" height="140%"><feGaussianBlur stdDeviation="2.6"/></filter>'
                   '<filter id="softer" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>')
    lx, ly = 1330, 70   # the lightning, off to the south behind the cloud
    sc.defs.append(f'<radialGradient id="litbody" gradientUnits="userSpaceOnUse" cx="{lx}" cy="{ly}" r="640">'
                   f'<stop offset="0" stop-color="{C["cloud_lit"]}"/><stop offset=".35" stop-color="#262e39"/>'
                   f'<stop offset="1" stop-color="{C["cloud"]}"/></radialGradient>')

    # ================= sky and storm =================
    with sc.layer("sky", 0):
        sc.sky(sc.lin("sky", C["sky"]))
        sc.add(f'<rect y="60" width="{W}" height="180" fill="{sc.lin("low", [(0, "#2b3542", 0), (.7, "#2b3542", .6), (1, "#2b3542", .2)])}"/>')
        sc.add(f'<ellipse cx="{lx}" cy="{ly + 10}" rx="460" ry="200" fill="{sc.rad("flash", [(0, C["flash"], .6), (.3, C["flash"], .22), (1, C["flash"], 0)])}"/>')

        def bank(y, amp, wmin, wmax, op=1.0):
            """A bank of storm cloud hanging from the top, with a lumpy underside."""
            under = []
            x = -40
            while x < W + 40:
                w = sc.r(wmin, wmax)
                under.append((x, y + sc.r(-amp, amp), w))
                x += w
            d = f"M-40,-10 L{W + 40},-10 L{W + 40},{f(under[-1][1])} "
            for (x0, y0, w) in reversed(under):
                d += f"Q{f(x0 + w / 2)},{f(y0 + w * sc.r(.18, .32))} {f(x0)},{f(y0)} "
            d += "Z"
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

        bank(146, 10, 70, 150, .55)
        bank(114, 14, 90, 170, .8)
        bank(80, 16, 100, 200)
        bank(42, 12, 120, 220)
        sc.add(f'<rect width="{W}" height="70" fill="{sc.lin("skyveil", [(0, "#07090c", .7), (1, "#07090c", 0)])}"/>')
        # ragged scud driving low under the storm
        for x, y, w in [(170, 150, 190), (560, 132, 140), (1010, 164, 210), (1440, 150, 170)]:
            with sc.fx("cloud"):
                g = "".join(f'<ellipse cx="{f(x + sc.r(-.5, .5) * w)}" cy="{f(y + sc.r(-6, 6))}" rx="{f(w * sc.r(.2, .38))}" ry="{f(sc.r(5, 10))}"/>' for _ in range(5))
                sc.add(f'<g filter="url(#soft)" fill="{C["cloud_mid"]}" opacity=".75">{g}</g>')

    # ================= the Thrihyrne beyond the gorge =================
    with sc.layer("peaks", .15):
        horns = [(1004, 70), (1104, 32), (1214, 62)]
        outline = jag(sc, [(800, 240), (880, 172), (940, 114), horns[0], (1032, 104), (1066, 110), (1086, 66), horns[1], (1134, 62),
                           (1170, 106), (1194, 98), horns[2], (1246, 100), (1306, 152), (1410, 240)], 3, .08)
        sc.add(f'<path d="{poly(outline)}" fill="{C["peak"]}"/>')
        for (hx, hy), w in zip(horns, (40, 52, 44)):
            facet = jag(sc, [(hx, hy), (hx + w * .55, hy + 46), (hx + w, hy + 120)], 2, .1) + [(hx + w * .25, hy + 150), (hx + 4, hy + 60)]
            sc.add(f'<path d="{poly(facet)}" fill="{C["peak_lit"]}" opacity=".55"/>')
            sc.add(f'<path d="M{hx},{hy} L{f(hx + w * .55)},{f(hy + 46)}" stroke="{C["flash"]}" stroke-opacity=".25" stroke-width="1.2"/>')
            for k in range(5):  # snow lying in the gullies
                a0 = sc.r(-.6, .7)
                l = sc.r(12, 30)
                sc.add(f'<path d="M{f(hx + sc.r(-8, 10))},{f(hy + 10 + k * 7)} l{f(a0 * l * .4)},{f(l)}" stroke="{C["snow"]}" stroke-opacity="{f(sc.r(.12, .28))}" stroke-width="{f(sc.r(.8, 1.8))}" stroke-linecap="round"/>')
        sc.add(f'<rect x="-30" y="40" width="{W + 60}" height="200" fill="{sc.lin("haze1", [(0, "#2a333e", 0), (.6, "#2a333e", .35), (1, "#2a333e", .55)])}"/>')

    # ================= the cliffs of the gorge =================
    with sc.layer("cliffs", .4):
        sc.ridge(208, 5, [(2.3, 1), (5.1, .5)], "#1a2028", seed=3.3, x0=880, x1=1260, taper=60)
        # the inner walls of the gorge closing in toward the Deep, with fires in the caves
        sc.add(f'<path d="{poly(jag(sc, [(900, 204), (952, 150), (1000, 158), (1044, 196), (1064, 214)], 2, .1) + [(900, 236)])}" fill="#1b2129"/>')
        sc.add(f'<path d="{poly(jag(sc, [(1240, 200), (1190, 128), (1140, 140), (1100, 190), (1076, 214)], 2, .1) + [(1240, 236)])}" fill="#1d242c"/>')
        sc.add(f'<path d="M1190,128 L1214,164 L1240,200" fill="none" stroke="{C["cliff_lit"]}" stroke-opacity=".6" stroke-width="1.2"/>')
        sc.add("".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(sc.r(.9, 1.5))}" fill="{C["fire"]}" opacity="{f(sc.r(.35, .7))}"/>'
                       for x, y in [(968, 176), (1016, 186), (1118, 184), (1156, 164), (1172, 178), (1058, 204), (1094, 202)]))
        # the north cliff, behind and above the Hornburg
        north = jag(sc, [(-20, 100), (70, 86), (160, 104), (240, 76), (320, 98), (390, 88), (450, 112), (520, 134), (580, 156), (630, 178), (680, 198), (704, 240)], 3, .14)
        sc.add(f'<path d="{poly(north + [(704, H), (-20, H)])}" fill="{C["cliff"]}"/>')
        cliff_faces(sc, north, -10, 660, C["cliff_face"], C["cliff_face"], lx)
        # the south cliff, lit along its crest by the flash
        south = jag(sc, [(1180, 250), (1204, 198), (1232, 160), (1272, 136), (1330, 124), (1390, 100), (1460, 112), (1530, 92), (1590, 104), (1640, 98)], 3, .14)
        sc.add(f'<path d="{poly(south + [(1640, H), (1180, H)])}" fill="{C["cliff"]}"/>')
        sc.add(f'<path d="{poly(south, False)}" fill="none" stroke="{C["cliff_lit"]}" stroke-width="1.6" stroke-opacity=".8"/>')
        cliff_faces(sc, south, 1210, 1630, C["cliff_face"], C["cliff_lit"], lx)
        rain(sc, 240, .14, .7, (10, 22))

    # ================= the Hornburg and the Deeping Wall =================
    with sc.layer("hornburg", .7):
        # the floor of the coomb and the scree at the feet of the cliffs
        sc.ridge(242, 10, [(1.6, 1), (4.2, .4)], "#191e24", seed=2.2, x0=-20, x1=560, taper=120)
        sc.ridge(244, 8, [(1.3, 1), (3.6, .5)], "#1a2026", seed=5.1, x0=1180, x1=W + 20, taper=120)
        coomb = sc.ridge(250, 4, [(1.4, 1), (3.7, .5)], C["coomb_far"], seed=1.9)

        # ---- the Deeping Wall ----
        bot = WALL_TOP_L + WALL_H
        face = [(WALL_L, WALL_TOP_L), (WALL_R, WALL_TOP_R), (WALL_R, WALL_TOP_R + WALL_H + 2), (WALL_L, bot + 2)]
        sc.add(f'<path d="{poly(face)}" fill="{sc.lin("wallg", [(0, C["stone"]), (.7, C["stone_dark"]), (1, "#1a1e23")])}"/>')
        d = ""
        for k in range(1, 8):
            ya, yb = WALL_TOP_L + k * 6.2, WALL_TOP_R + k * 6.2
            d += f"M{WALL_L},{f(ya)} L{WALL_R},{f(yb)} "
            x = WALL_L + (11 if k % 2 else 0)
            while x < WALL_R:
                y = wall_top(x) + k * 6.2
                d += f"M{f(x)},{f(y - 6.2)} v6.2 "
                x += 22
        sc.add(f'<path d="{d}" stroke="#000" stroke-opacity=".28" stroke-width=".7"/>')
        sc.add(f'<path d="{poly([(WALL_L, WALL_TOP_L), (WALL_R, WALL_TOP_R), (WALL_R, WALL_TOP_R - 5), (WALL_L, WALL_TOP_L - 5)])}" fill="{C["stone"]}"/>')
        sc.add(f'<path d="{crenels(WALL_L, WALL_TOP_L - 5, WALL_R, WALL_TOP_R - 5, 8, 6, 6)}" fill="{C["stone"]}"/>')
        sc.add(f'<path d="M{WALL_L},{WALL_TOP_L - 5} L{WALL_R},{WALL_TOP_R - 5}" stroke="{C["stone_lit"]}" stroke-opacity=".5" stroke-width=".8"/>')
        for x in range(WALL_L + 50, WALL_R - 20, 64):  # buttresses
            y = wall_top(x)
            yb = bot + (y - WALL_TOP_L) + 3
            sc.add(f'<path d="M{x - 6},{f(y + 5)} L{x + 6},{f(y + 5)} L{x + 11},{f(yb)} L{x - 11},{f(yb)}Z" fill="{C["stone_dark"]}"/>'
                   f'<path d="M{x + 6},{f(y + 5)} L{x + 11},{f(yb)}" stroke="{C["stone_lit"]}" stroke-opacity=".3" stroke-width="1"/>')
        sc.add(f'<path d="{poly([(WALL_L, WALL_TOP_L - 3), (WALL_R, WALL_TOP_R - 3), (WALL_R, WALL_TOP_R + 12), (WALL_L, WALL_TOP_L + 12)])}" fill="{sc.lin("wash", [(0, C["glow"], .16), (1, C["glow"], 0)])}"/>')
        # where the wall is keyed into the southern cliff
        sc.add(f'<path d="{poly(jag(sc, [(1222, 262), (1226, 222), (1238, 190), (1256, 172), (1274, 196), (1270, 264)], 2, .1))}" fill="{C["cliff"]}"/>'
               f'<path d="M1238,190 L1256,172 L1262,200 L1246,250Z" fill="{C["cliff_lit"]}" opacity=".35"/>')

        # ---- the culvert where the Deeping-stream runs out under the wall ----
        cx = 1086
        cy = wall_top(cx) + WALL_H + 2
        with sc.hot("helmsdeep-culvert", "The Culvert", "The Deeping-stream slips out under the wall through a narrow barred arch.", "splash"):
            sc.add(f'<path d="M{cx - 15},{f(cy)} L{cx - 15},{f(cy - 12)} Q{cx},{f(cy - 28)} {cx + 15},{f(cy - 12)} L{cx + 15},{f(cy)}Z" fill="#07090b"/>'
                   f'<path d="M{cx - 18},{f(cy - 12)} Q{cx},{f(cy - 32)} {cx + 18},{f(cy - 12)}" fill="none" stroke="{C["stone_lit"]}" stroke-opacity=".45" stroke-width="2"/>')
            sc.add(f'<path d="M{cx - 10},{f(cy - 15)} V{f(cy)} M{cx - 3.5},{f(cy - 19)} V{f(cy)} M{cx + 3.5},{f(cy - 19)} V{f(cy)} M{cx + 10},{f(cy - 15)} V{f(cy)}" stroke="#3a4048" stroke-width="1.3"/>')
            sc.add(f'<path d="M{cx - 14},{f(cy)} Q{cx},{f(cy - 4)} {cx + 14},{f(cy)} Q{cx + 10},{f(cy + 7)} {cx},{f(cy + 6)} Q{cx - 10},{f(cy + 7)} {cx - 14},{f(cy)}Z" fill="{C["water"]}"/>'
                   f'<path d="M{cx - 9},{f(cy + 2)} h6 M{cx + 2},{f(cy + 3)} h7" stroke="{C["rain"]}" stroke-opacity=".5" stroke-width="1"/>')

        # ---- the rock spur ----
        spur = jag(sc, [(500, 330), (522, 286), (548, 248), (580, 220), (626, 200), (700, 192), (800, 190), (866, 194), (900, 208), (924, 236), (944, 280), (958, 330)], 2, .1)
        sc.add(f'<path d="{poly(spur)}" fill="{C["cliff_face"]}"/>')
        sc.add(f'<path d="{poly([(548, 248), (580, 220), (626, 200), (680, 196), (610, 250), (566, 300), (520, 330)])}" fill="{C["cliff"]}" opacity=".8"/>')
        sc.add(f'<path d="{poly([(866, 194), (900, 208), (924, 236), (944, 280), (958, 330), (930, 330), (912, 262), (884, 214)])}" fill="{C["cliff_lit"]}" opacity=".35"/>')
        d = ""
        for _ in range(14):  # rock seams
            x = sc.r(560, 930)
            y = sc.r(214, 300)
            d += f"M{f(x)},{f(y)} l{f(sc.r(-10, 10))},{f(sc.r(12, 34))}"
        sc.add(f'<path d="{d}" stroke="#000" stroke-opacity=".3" stroke-width="1.1"/>')

        # ---- the great hall: stone below, a steep timber roof above ----
        hx0, hx1, hy = 760, 880, 146
        gx = (hx0 + hx1) / 2
        sc.add(f'<rect x="{hx0}" y="{hy}" width="{hx1 - hx0}" height="44" fill="{C["stone_dark"]}"/>'
               f'<path d="M{hx0 - 9},{hy + 2} L{gx},{hy - 40} L{hx1 + 9},{hy + 2}Z" fill="{C["wood"]}"/>'
               f'<path d="M{gx},{hy - 40} L{hx1 + 9},{hy + 2} L{gx + 9},{hy + 2}Z" fill="{C["wood_dark"]}" opacity=".7"/>'
               f'<path d="M{gx},{hy - 40} L{hx1 + 9},{hy + 2}" stroke="{C["flash"]}" stroke-opacity=".25" stroke-width="1"/>')
        d = ""
        for k in range(1, 8):
            t = k / 8
            d += f"M{f(hx0 - 9 + (gx - hx0 + 9) * t)},{f(hy + 2 - 42 * t)} L{f(hx1 + 9 - (hx1 + 9 - gx) * t)},{f(hy + 2 - 42 * t)} "
        sc.add(f'<path d="{d}" stroke="#000" stroke-opacity=".3" stroke-width=".8"/>')
        sc.add(f'<path d="M{f(gx - 10)},{hy - 50} L{f(gx)},{hy - 39} L{f(gx + 10)},{hy - 50}" fill="none" stroke="{C["wood"]}" stroke-width="3" stroke-linecap="round"/>')
        sc.add(f'<rect x="{gx - 1.4}" y="{hy - 60}" width="2.8" height="13" fill="{C["wood_dark"]}"/>')  # a bare flagpole, no banner
        for x in range(hx0 + 12, hx1 - 8, 20):
            sc.add(f'<circle cx="{x + 3}" cy="{hy + 15}" r="12" fill="url(#halo)" opacity=".6"/><rect x="{x}" y="{hy + 9}" width="6" height="11" rx="3" fill="{C["window"]}"/>')

        # ---- the great tower (click: a flash of lightning) ----
        tx0, tx1, tt = 646, 738, 62
        tm = (tx0 + tx1) / 2
        with sc.hot("helmsdeep-tower", "The Hornburg", "An old fortress-tower on its rock spur, keeping watch over the mouth of the gorge.", "flash"):
            # a short wall joining the tower to the hall
            sc.add(f'<rect x="{tx1}" y="158" width="{hx0 - tx1}" height="32" fill="{C["stone_dark"]}"/>'
                   f'<path d="{crenels(tx1, 158, hx0, 158, 5, 4, 5)}" fill="{C["stone_dark"]}"/>')
            # the stair turret on its shoulder
            sc.add(f'<rect x="{tx0 - 26}" y="{tt + 46}" width="28" height="{196 - tt - 46}" fill="{C["stone_dark"]}"/>'
                   f'<path d="M{tx0 - 30},{tt + 47} L{tx0 - 12},{tt + 22} L{tx0 + 6},{tt + 47}Z" fill="{C["wood_dark"]}"/>'
                   f'<path d="M{tx0 - 12},{tt + 22} L{tx0 + 6},{tt + 47} L{tx0 - 6},{tt + 47}Z" fill="{C["flash"]}" opacity=".1"/>')
            sc.add(f'<path d="M{tx0},{tt} L{tx1},{tt} L{tx1},166 L{tx1 + 8},196 L{tx0 - 8},196 L{tx0},166Z" fill="{C["stone"]}"/>'
                   f'<path d="M{tx1 - 30},{tt} L{tx1},{tt} L{tx1},166 L{tx1 + 8},196 L{tx1 - 30},196Z" fill="{C["stone_lit"]}" opacity=".3"/>'
                   f'<path d="M{tx1},{tt} L{tx1},166 L{tx1 + 8},196" fill="none" stroke="{C["flash"]}" stroke-opacity=".35" stroke-width="1.2"/>')
            d = ""
            for y in range(tt + 9, 166, 9):
                d += f"M{tx0},{y} H{tx1} "
                x = tx0 + (8 if (y // 9) % 2 else 0)
                while x < tx1:
                    d += f"M{x},{y - 9} v9 "
                    x += 16
            sc.add(f'<path d="{d}" stroke="#000" stroke-opacity=".2" stroke-width=".7"/>')
            sc.add(f'<path d="M{tx0},166 H{tx1}" stroke="#000" stroke-opacity=".35" stroke-width="1.6"/>')
            # the fighting-gallery on corbels, battlements, and a low timber roof
            sc.add(f'<rect x="{tx0 - 7}" y="{tt - 10}" width="{tx1 - tx0 + 14}" height="11" fill="{C["stone_dark"]}"/>')
            d = "".join(f"M{f(tx0 - 6 + k * 9.8)},{tt + 1} l2.8,8 l2.8,-8Z" for k in range(11))
            sc.add(f'<path d="{d}" fill="{C["stone_dark"]}"/>')
            sc.add(f'<path d="{crenels(tx0 - 7, tt - 10, tx1 + 7, tt - 10, 7, 5, 8)}" fill="{C["stone_dark"]}"/>')
            sc.add(f'<path d="M{tx0 + 5},{tt - 14} L{tm - 14},{tt - 38} L{tm + 14},{tt - 38} L{tx1 - 5},{tt - 14}Z" fill="{C["wood"]}"/>'
                   f'<path d="M{tm + 14},{tt - 38} L{tx1 - 5},{tt - 14} L{tm + 18},{tt - 14}Z" fill="{C["flash"]}" opacity=".14"/>'
                   f'<path d="M{tm - 14},{tt - 38} L{tm + 14},{tt - 38}" stroke="{C["flash"]}" stroke-opacity=".3" stroke-width="1"/>')
            for x, y, w, h in [(tm - 3, 92, 6, 13), (tm - 3, 132, 6, 13), (tx0 + 14, 112, 3.5, 9), (tx1 - 18, 148, 3.5, 9),
                               (tx0 - 15, 132, 3.5, 8), (tx0 - 15, 160, 3.5, 8)]:
                sc.add(f'<circle cx="{f(x + w / 2)}" cy="{f(y + h / 2)}" r="{f(h * 1.3)}" fill="url(#halo)" opacity=".6"/>'
                       f'<rect x="{f(x)}" y="{y}" width="{w}" height="{h}" fill="{C["window"]}"/>')

        # ---- the curtain wall round the top of the rock ----
        cw = [(562, 238), (588, 208), (640, 192), (760, 188), (880, 190), (906, 198)]
        cwb = [(914, 238), (880, 216), (760, 214), (640, 218), (604, 230), (578, 254)]
        sc.add(f'<path d="{poly(cw + cwb)}" fill="{C["stone"]}"/>')
        sc.add(f'<path d="{poly(cw + [(906, 203), (880, 195), (760, 193), (640, 197), (588, 213), (562, 243)])}" fill="{C["stone_lit"]}" opacity=".22"/>')
        d = "".join("M" + " L".join(f"{f(x)},{f(y + k * 7)}" for x, y in cw) + " " for k in (1, 2, 3))
        sc.add(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity=".25" stroke-width=".7"/>')
        d = "".join(crenels(ax, ay, bx, by, 7, 5, 6) for (ax, ay), (bx, by) in zip(cw, cw[1:]))
        sc.add(f'<path d="{d}" fill="{C["stone"]}"/>')
        # steps cut in the rock, climbing from the coomb to a postern under the curtain wall
        d = ""
        for k in range(9):
            x, y = 590 + k * 7, 296 - k * 7.4
            d += f"M{f(x)},{f(y)} h11 v-3 h-11Z"
        sc.add(f'<path d="{d}" fill="{C["stone"]}"/><path d="{d.replace("h11 v-3 h-11Z", "h11")}" stroke="{C["stone_lit"]}" stroke-opacity=".6" stroke-width=".9"/>')
        sc.add(f'<path d="M650,236 v-10 q6,-7 12,0 v10Z" fill="#0b0d10"/>')

        # ---- the gate tower, its gates, and the causeway ----
        gx0, gx1, gt = 880, 930, 176
        sc.add(f'<rect x="{gx0}" y="{gt}" width="{gx1 - gx0}" height="{254 - gt}" fill="{C["stone"]}"/>'
               f'<rect x="{gx1 - 16}" y="{gt}" width="16" height="{254 - gt}" fill="{C["stone_lit"]}" opacity=".25"/>'
               f'<path d="{crenels(gx0 - 3, gt, gx1 + 3, gt, 6, 5, 7)}" fill="{C["stone"]}"/>'
               f'<rect x="{gx0 - 3}" y="{gt - 1}" width="{gx1 - gx0 + 6}" height="5" fill="{C["stone_dark"]}"/>'
               f'<rect x="{(gx0 + gx1) / 2 - 2}" y="192" width="4" height="9" fill="{C["window"]}"/>')
        ax0, ax1, aspring, atop = 891, 919, 228, 212   # the gate arch
        arch = f"M{ax0},254 V{aspring} Q{ax0},{atop} {(ax0 + ax1) / 2},{atop} Q{ax1},{atop} {ax1},{aspring} V254Z"
        with sc.hot("helmsdeep-gate", "The Gate", "Heavy timber gates at the head of the causeway, the only way in from the coomb.", "swing"):
            sc.add(f'<path d="{arch}" fill="#0b0d10"/><ellipse cx="{(ax0 + ax1) / 2}" cy="246" rx="12" ry="10" fill="url(#halo)"/>')
            sc.add(f'<g class="swing" data-origin="{ax0} 233"><path d="{arch}" fill="{C["wood"]}"/>'
                   f'<path d="M{ax0},232 H{ax1} M{ax0},245 H{ax1} M{ax0 + 7},{atop + 2} V254 M{ax0 + 14},{atop} V254 M{ax0 + 21},{atop + 2} V254" stroke="#000" stroke-opacity=".45" stroke-width=".9"/>'
                   f'<path d="M{ax0},232 H{ax1} M{ax0},245 H{ax1}" stroke="#5b636c" stroke-width="1.6" stroke-opacity=".7"/></g>')
            sc.add(f'<path d="M{ax0 - 3},254 V{aspring} Q{ax0 - 3},{atop - 4} {(ax0 + ax1) / 2},{atop - 4} Q{ax1 + 3},{atop - 4} {ax1 + 3},{aspring} V254" fill="none" stroke="{C["stone_lit"]}" stroke-opacity=".5" stroke-width="2"/>')
        with sc.hot("helmsdeep-causeway", "The Causeway", "A stone ramp climbing from the valley floor up to the Hornburg's gate.", "pulse"):
            sc.add(f'<path d="M886,254 L926,254 L934,260 L874,320 L860,318Z" fill="#1d2228"/>'
                   f'<path d="M886,254 L926,254 L864,318 L812,314Z" fill="{C["stone_dark"]}"/>'
                   f'<path d="M926,254 L864,318" stroke="{C["stone_lit"]}" stroke-opacity=".45" stroke-width="1.2"/>')
            d = ""
            for k in range(1, 9):  # cross-joints of the paving
                t = k / 9
                d += f"M{f(886 - 74 * t)},{f(254 + 60 * t)} L{f(926 - 62 * t)},{f(254 + 64 * t)} "
            sc.add(f'<path d="{d}" stroke="#000" stroke-opacity=".3" stroke-width=".8"/>')
            d = ""
            for k in range(6):  # the parapet on its outer edge
                t = k / 6
                x, y = 926 - 62 * t, 254 + 64 * t
                d += f"M{f(x)},{f(y)} l3,-6 l4,4 l-3,6Z"
            sc.add(f'<path d="{d}" fill="{C["stone"]}"/>')

        # ---- torches: along the Deeping Wall (click: they blaze up), and round the Hornburg ----
        wall_torches = [(x, wall_top(x) - 5) for x in range(936, WALL_R - 10, 40)]
        with sc.hot("helmsdeep-torches", "The Deeping Wall", "A long wall closing the gorge, its parapet lit by torches against the rain.", "light"):
            sc.add('<g class="on-lit" opacity="0">' + "".join(f'<circle cx="{f(x)}" cy="{f(y - 8)}" r="58" fill="url(#halo)"/>' for x, y in wall_torches)
                   + f'<path d="{poly([(WALL_L, WALL_TOP_L - 3), (WALL_R, WALL_TOP_R - 3), (WALL_R, WALL_TOP_R + 30), (WALL_L, WALL_TOP_L + 30)])}" fill="{sc.lin("wash2", [(0, C["glow"], .3), (1, C["glow"], 0)])}"/></g>')
            with sc.fx("flicker"):
                for x, y in wall_torches:
                    torch(sc, x, y, 1.15)
        with sc.fx("flicker"):
            for x, y, s in [(600, 203, .95), (700, 186, .95), (820, 184, .95), (874, 186, .95), (gx0 - 3, 232, 1), (gx1 + 3, 232, 1)]:
                torch(sc, x, y, s)

        # ---- the floor of the coomb in front ----
        d = ""
        for _ in range(30):
            x = sc.r(0, W)
            if 500 < x < 960:
                continue
            y = Scene.y_at(coomb, x) + sc.r(6, 46)
            s = sc.r(3, 9)
            d += poly([(x - s, y), (x - s * .6, y - s * .7), (x + s * .3, y - s * .8), (x + s, y)])
        sc.add(f'<path d="{d}" fill="{mix(C["coomb"], C["stone_dark"], .55)}"/>')
        sc.tufts(256, 316, 200, ["#1b2226", "#20282c", "#161c20", "#242c30"], 4, 11)
        # the Deeping-stream, catching the torchlight as it leaves the culvert
        stream = f"M{cx},{f(cy + 4)} C{cx + 8},{f(cy + 16)} 1130,268 1180,278 S1250,296 1190,306 S1110,316 1100,326"
        with sc.fx("water"):
            sc.add(f'<path d="{stream}" fill="none" stroke="{C["water"]}" stroke-width="3" stroke-linecap="round"/>'
                   f'<path d="{stream}" fill="none" stroke="{C["glow"]}" stroke-opacity=".3" stroke-width="1.1" stroke-dasharray="6 14" stroke-linecap="round"/>')
        rain(sc, 160, .2, .9, (16, 32))

    # ================= the near coomb =================
    with sc.layer("front", 1):
        sc.add(f'<rect x="-30" y="180" width="{W + 60}" height="100" fill="{sc.lin("mist", [(0, "#2a333e", 0), (.6, "#2a333e", .2), (1, "#2a333e", 0)])}"/>')
        sc.ridge(316, 3, [(1.1, 1), (2.6, .4)], "#1a1f24", seed=4.4)   # the green dike, a long low earthwork
        sc.ridge(338, 5, [(2.0, 1), (4.6, .4)], C["coomb"], seed=6.2)
        with sc.fx("water"):
            sc.add(f'<path d="M1102,316 C1092,336 1030,350 1010,372 S1030,396 1040,406" fill="none" stroke="{C["water"]}" stroke-width="3.4" stroke-linecap="round"/>')
        sc.tufts(312, 326, 90, ["#1a2024", "#1e252a"], 4, 10)
        sc.tufts(332, 404, 200, ["#161b1f", "#1a2024", "#13171b"], 6, 15)
        rain(sc, 32, .28, 1.1, (28, 50))
        sc.add(f'<rect x="-30" y="280" width="{W + 60}" height="130" fill="{sc.lin("near", [(0, C["bg"], 0), (1, C["bg"], .85)])}"/>')
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build().save(f"{out}/helmsdeep.svg", "Helm's Deep in the rain")
