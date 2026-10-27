"""Weathertop by night: Amon Sûl at the southern end of the Weather Hills.

A tall, steep, lonely hill crowned with the broken ring of an old watchtower's
walls; the long ridge of the Weather Hills running away north; a moon behind
torn storm cloud; cold blue light, scrub and boulders; and, in the dell under
the hill's western side, the small red glow of a campfire.
"""
import math
import sys
from scene_kit import Scene, W, H, f

P = dict(
    sky=[(0, "#080b15"), (.4, "#111628"), (.75, "#1d2540"), (1, "#28324f")],
    moon="#eef1fa", moon_glow="#9fb2ea",
    cloud="#161b2d", cloud_lit="#8492bd", cloud_mid="#232a42",
    far1="#27304b", far2="#212841", far3="#1b2136", haze="#3a4668",
    hill_dark="#181d2e", hill_mid="#262d45", hill_lit="#3d4869", crag="#59658c", crag_dark="#141826",
    stone_lit="#8893b6", stone="#535c7d", stone_dark="#272c41",
    scrub="#121624", scrub_lit="#26304a", ground="#151823", path="#3a4462",
    fire="#ffb15c", fire_core="#fff0c4", ember="#e8743a",
)


def torn_cloud(sc, cx, cy, length, thick, lit, body, rim=1.8, seed=0.0, op=1.0):
    """A long wind-torn rag of cloud: ragged edges, tapering ends, its top rim catching the moon."""
    n = 70
    top, bot = [], []
    bumps = 4 + int(length / 90)
    for i in range(n + 1):
        t = i / n
        x = cx - length / 2 + length * t
        env = math.sin(math.pi * t) ** .55
        # rounded billows along the top, smaller ones riding on the big ones
        bill = .55 + .3 * abs(math.sin(t * math.pi * bumps + seed)) ** .5 + .15 * abs(math.sin(t * math.pi * bumps * 2.7 + seed * 2)) ** .5
        lean = 1 - .35 * t  # the wind tears the trailing (east) end thinner
        top.append((x, cy - thick * env * bill * lean))
        bot.append((x, cy + thick * .22 * env * (.8 + .2 * math.sin(t * 19 + seed * 3))))
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in top + bot[::-1]) + "Z"
    d_rim = "M" + " L".join(f"{f(a)},{f(b - rim)}" for a, b in top) + " L" + " L".join(f"{f(a)},{f(b - rim)}" for a, b in bot[::-1]) + "Z"
    wisps = "".join(f'<ellipse cx="{f(cx + length * (.5 + k * .07))}" cy="{f(cy - thick * .1 + k * 3)}" rx="{f(length * (.08 - k * .015))}" ry="{f(max(1.2, thick * .08))}"/>' for k in range(3))
    sc.add(f'<g opacity="{op}"><path d="{d_rim}" fill="{lit}"/><path d="{d}" fill="{body}"/><g fill="{body}" opacity=".8">{wisps}</g></g>')


def boulder(sc, x, y, s, lit, body, dark):
    """A rounded stone sitting on the ground at (x, y), moonlit from the upper right."""
    pts = [(-1, 0), (-.9, -.45), (-.5, -.8), (.05, -.95), (.55, -.75), (.95, -.35), (1, 0)]
    d = "M" + " L".join(f"{f(x + px * s * sc.r(.9, 1.1))},{f(y + py * s * .8)}" for px, py in pts) + "Z"
    sc.add(f'<path d="{d}" fill="{body}"/>'
           f'<path d="M{f(x + .05 * s)},{f(y - .76 * s)} L{f(x + .55 * s)},{f(y - .6 * s)} L{f(x + .95 * s)},{f(y - .28 * s)} L{f(x + .7 * s)},{f(y - .2 * s)} L{f(x + .3 * s)},{f(y - .5 * s)}Z" fill="{lit}"/>'
           f'<path d="M{f(x - s)},{f(y)} L{f(x - .9 * s)},{f(y - .36 * s)} L{f(x - .55 * s)},{f(y - .15 * s)} L{f(x - .2 * s)},{f(y)}Z" fill="{dark}"/>')


def scrub(sc, x, y, s, fill, lit=None):
    g = []
    for dx, dy, rr in [(-.6, -.25, .45), (0, -.45, .6), (.6, -.25, .45), (.25, -.15, .4), (-.25, -.12, .4)]:
        g.append(f'<circle cx="{f(x + dx * s)}" cy="{f(y + dy * s)}" r="{f(rr * s * sc.r(.85, 1.15))}" fill="{fill}"/>')
    if lit:
        g.append(f'<circle cx="{f(x + .2 * s)}" cy="{f(y - .72 * s)}" r="{f(.24 * s)}" fill="{lit}"/>')
    sc.add("".join(g))


def amon_sul(x):
    """Profile of the hill: a small flat crown, steep flanks, a long spreading foot."""
    dx = abs(x - 760)
    u = max(0, dx - 58) / 285
    y = 88 + 208 * (1 - math.exp(-3.4 * u ** 1.5)) / (1 - math.exp(-3.4))
    if dx < 58:
        y += 1.2 * math.sin(x / 7)
    # shoulders: the west side a little fuller, with the dell under it
    if x < 760:
        y -= 14 * math.exp(-((x - 610) / 40) ** 2)
    else:
        y -= 8 * math.exp(-((x - 900) / 50) ** 2)
    return y + 2.5 * math.sin(x / 13) + 1.5 * math.sin(x / 5.3)


def ring_walls(sc, cx, cy, rx, ry):
    """The broken ring of the watchtower's walls, seen a little from below: back arc, then front arc."""
    segs = [  # (start angle, end angle, height) in degrees; 90 is nearest to us, 270 the far side
        (192, 236, 14), (244, 296, 18), (306, 334, 12), (342, 372, 16),  # far side
        (22, 54, 11), (64, 98, 8), (112, 150, 13), (158, 178, 7),          # near side, lower and more broken
    ]
    for a0, a1, hgt in segs:
        far = 180 < (a0 + a1) / 2 < 360
        steps = max(3, int((a1 - a0) / 4))
        base, top = [], []
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            x = cx + rx * math.cos(a)
            y = cy + ry * math.sin(a)
            # broken, jagged crest, lower toward the gaps
            edge = min(i, steps - i) / steps
            h = hgt * (.45 + .55 * min(1, edge * 3)) * sc.r(.75, 1.05)
            base.append((x, y))
            top.append((x, y - h))
        # step the crest: masonry courses
        crest = []
        for (ax, ay), (bx, by) in zip(top, top[1:]):
            crest += [(ax, ay), (bx, ay)]
        crest.append(top[-1])
        d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in base[::-1] + crest) + "Z"
        # walls facing the moon (upper right) are lit; the far arc shows its inner face
        mid = math.radians((a0 + a1) / 2)
        facing = math.cos(mid) * (-1 if far else 1)
        col = P["stone_lit"] if facing > .25 else (P["stone"] if facing > -.35 else P["stone_dark"])
        sc.add(f'<path d="{d}" fill="{col}"/>')
        courses = "".join(f"M{f(top[i][0])},{f(base[i][1] - (base[i][1] - top[i][1]) * k / 3)}L{f(top[i + 1][0])},{f(base[i + 1][1] - (base[i + 1][1] - top[i + 1][1]) * k / 3)}"
                          for k in (1, 2) for i in range(steps))
        sc.add(f'<path d="{courses}" stroke="{P["stone_dark"]}" stroke-width=".7" opacity=".6"/>')
        sc.add(f'<path d="M' + " L".join(f"{f(a)},{f(b)}" for a, b in crest) + f'" fill="none" stroke="{P["stone_lit"] if col != P["stone_dark"] else P["stone"]}" stroke-width=".9" opacity=".8"/>')


def build(seed=11):
    sc = Scene(seed)
    sc.sky(sc.lin("sky", P["sky"]))
    # stars where the sky is clear
    stars = []
    for _ in range(170):
        x, y = sc.r(0, W), sc.r(0, 200)
        stars.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(sc.r(.4, 1.2))}" opacity="{f(sc.r(.25, .85))}"/>')
    sc.add(f'<g fill="#dfe5f7">{"".join(stars)}</g>')
    # the moon and its cold halo
    mx, my = 1250, 80
    sc.add(f'<circle cx="{mx}" cy="{my}" r="230" fill="{sc.rad("halo", [(0, P["moon_glow"], .32), (.18, P["moon_glow"], .14), (1, P["moon_glow"], 0)])}"/>')
    sc.add(f'<circle cx="{mx}" cy="{my}" r="24" fill="{P["moon"]}"/>'
           f'<circle cx="{mx - 7}" cy="{my - 5}" r="6" fill="#cfd6ea" opacity=".6"/><circle cx="{mx + 6}" cy="{my + 7}" r="4" fill="#cfd6ea" opacity=".5"/>'
           f'<circle cx="{mx + 9}" cy="{my - 9}" r="3" fill="#cfd6ea" opacity=".45"/>')

    # torn storm cloud streaming across from the west, rims lit by the moon
    for cx, cy, ln, th, sd, op in [(170, 34, 520, 40, 1.1, 1), (600, 70, 560, 30, 2.3, .95), (1000, 24, 520, 36, 3.7, 1),
                                    (1500, 26, 420, 34, 4.1, 1), (1400, 136, 480, 26, 5.2, .9), (320, 132, 420, 20, 6.3, .8),
                                    (980, 150, 340, 16, 7.4, .7)]:
        near = math.exp(-((cx - mx) / 380) ** 2)
        body = "#20273f" if near < .3 else "#2a3251"
        torn_cloud(sc, cx, cy, ln, th, "#7d8bb8" if near > .3 else "#333d5e", body, rim=1.2 + 1.8 * near, seed=sd, op=op)
    # a rag of cloud dragging across the face of the moon
    torn_cloud(sc, mx - 20, my + 14, 340, 24, "#c3cdec", "#2e3657", rim=2.6, seed=8.8, op=.95)
    torn_cloud(sc, mx + 110, my - 30, 200, 10, "#aab7e0", "#283050", rim=1.8, seed=9.6, op=.85)

    # the Weather Hills: a long ridge running away north (left), and low country east
    far = sc.ridge(214, 14, [(1.8, 1), (4.2, .5), (9, .2)], P["far1"], seed=2.2)
    sc.add(f'<rect y="170" width="{W}" height="90" fill="{sc.lin("haze1", [(0, P["haze"], 0), (1, P["haze"], .35)])}"/>')
    # the ridge of hills, rising toward Weathertop from the north
    hills = []
    for x in range(-20, 700, 6):
        t = (x + 20) / 720
        y = 222 - 46 * t ** .8 - 24 * abs(math.sin(x / 70 + .6)) ** 1.6 + 4 * math.sin(x / 17)
        hills.append((x, y))
    for x in range(700, 1000, 6):
        hills.append((x, hills[-1][1] + 6 * .5))
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in hills) + f" L1000,{H} L-20,{H}Z"
    sc.add(f'<path d="{d}" fill="{sc.lin("ridgeg", [(0, P["far2"]), (1, P["far3"])], x2=1, y2=0)}"/>')
    # moonlit crests along the ridge
    sc.add('<path d="M' + " L".join(f"{f(a)},{f(b + .5)}" for a, b in hills[::2] if a < 690) + f'" fill="none" stroke="#45527a" stroke-width="1.1" opacity=".55"/>')
    for x in range(10, 680, 9):  # scrub dotted along it
        y = sc.y_at(hills, x)
        if sc.r(0, 1) < .55:
            sc.add(f'<circle cx="{f(x + sc.r(-3, 3))}" cy="{f(y + sc.r(3, 14))}" r="{f(sc.r(1.6, 3.2))}" fill="#181d30"/>')
    # low country to the east, and the Road running away toward the Last Bridge
    # far off east, the dim hills of the Trollshaws
    sc.ridge(198, 16, [(2.2, 1), (5.3, .45), (11, .15)], "#252d48", seed=5.7, x0=1040, x1=W + 60, taper=260)
    sc.add(f'<rect y="170" width="{W}" height="70" fill="{sc.lin("haze3", [(0, P["haze"], 0), (1, P["haze"], .3)])}"/>')
    east = sc.ridge(232, 7, [(1.3, 1), (3.6, .4), (8, .15)], P["far2"], seed=4.4, x0=880, x1=W + 40)
    sc.add(f'<path d="M1010,276 C1120,262 1250,252 1390,246 C1480,242 1560,241 1620,240" fill="none" stroke="{P["path"]}" stroke-width="1.6" opacity=".55"/>')
    sc.add(f'<rect x="0" y="210" width="{W}" height="70" fill="{sc.lin("haze2", [(0, P["haze"], 0), (1, P["haze"], .18)])}"/>')
    # nearer foothills either side of Amon Sûl
    lfoot = sc.ridge(250, 10, [(1.5, 1), (3.3, .4)], P["far3"], seed=1.4, x0=-20, x1=620, taper=0)
    rfoot = sc.ridge(256, 9, [(1.2, 1), (2.8, .5)], P["far3"], seed=3.3, x0=930, x1=W + 20)
    for x in list(range(0, 600, 11)) + list(range(960, W, 11)):  # thorn-scrub on the foothills
        pts = lfoot if x < 620 else rfoot
        if sc.r(0, 1) < .5:
            scrub(sc, x, sc.y_at(pts, x) + sc.r(6, 20), sc.r(4, 7), "#141929")

    # Amon Sûl
    prof = [(x, amon_sul(x)) for x in range(400, 1121, 5)]
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in prof) + f" L1120,{H} L400,{H}Z"
    sc.add(f'<path d="{d}" fill="{sc.lin("hillg", [(0, P["hill_dark"]), (.42, P["hill_mid"]), (.62, P["hill_lit"]), (1, P["hill_mid"])], x2=1, y2=0)}"/>')
    sc.add(f'<path d="{d}" fill="{sc.lin("hillv", [(0, P["hill_dark"], 0), (.45, P["hill_dark"], 0), (1, P["hill_dark"], .8)])}"/>')
    # moonlit rim along the right-hand skyline
    sc.add('<path d="M' + " L".join(f"{f(a)},{f(b + .6)}" for a, b in prof if 790 < a < 1060) + f'" fill="none" stroke="#6d7aa3" stroke-width="1.4" opacity=".7"/>')
    sc.add('<path d="M' + " L".join(f"{f(a)},{f(b + .6)}" for a, b in prof if 700 < a <= 790) + f'" fill="none" stroke="#6d7aa3" stroke-width="1" opacity=".45"/>')
    # rock ribs and gullies running down the steep flanks
    dark, lit = [], []
    for x0 in [692, 722, 748, 770, 800, 818, 840, 862, 884, 906, 930, 668, 646, 958]:
        side = 1 if x0 > 760 else -1
        y0 = amon_sul(x0) + (sc.r(6, 14) if abs(x0 - 760) > 40 else sc.r(18, 46))
        ln = sc.r(36, 100)
        x1 = x0 + side * ln * sc.r(.25, .45)
        y1 = min(amon_sul(x1) + ln * .9, 292)
        cxm = (x0 + x1) / 2 + side * sc.r(-6, 6)
        dark.append(f"M{f(x0)},{f(y0)}Q{f(cxm)},{f((y0 + y1) / 2)} {f(x1)},{f(y1)}")
        lit.append(f"M{f(x0 + 1.6)},{f(y0 + 1)}Q{f(cxm + 1.6)},{f((y0 + y1) / 2)} {f(x1 + 1.6)},{f(y1 - 6)}")
    sc.add(f'<path d="{"".join(dark)}" fill="none" stroke="#141826" stroke-width="2.2" stroke-linecap="round" opacity=".5"/>')
    sc.add(f'<path d="{"".join(lit)}" fill="none" stroke="#5b6791" stroke-width="1" stroke-linecap="round" opacity=".45"/>')
    # a few angular rocks breaking the surface
    for x0, dep, s in [(818, 14, 7), (846, 34, 6), (700, 16, 6), (684, 40, 7), (884, 60, 6), (930, 96, 7), (668, 92, 5)]:
        y0 = amon_sul(x0) + dep
        sc.add(f'<path d="M{f(x0 - s)},{f(y0)} L{f(x0 - s * .6)},{f(y0 - s * .7)} L{f(x0 + s * .2)},{f(y0 - s)} L{f(x0 + s)},{f(y0 - s * .2)} L{f(x0 + s * .9)},{f(y0)}Z" fill="#20263b"/>'
               f'<path d="M{f(x0 + s * .2)},{f(y0 - s)} L{f(x0 + s)},{f(y0 - s * .2)} L{f(x0 + s * .9)},{f(y0)} L{f(x0 + s * .3)},{f(y0)}Z" fill="{P["crag"] if x0 > 740 else "#38425f"}"/>')
    scree = "".join(f"M{f(x)},{f(amon_sul(x) + sc.r(18, 120))}l{f(sc.r(1.5, 4))},{f(sc.r(5, 12))}" for x in [sc.r(780, 1000) for _ in range(40)])
    sc.add(f'<path d="{scree}" stroke="#4d5a82" stroke-width=".9" stroke-linecap="round" opacity=".55"/>')

    # the crown: the broken ring of the old watchtower
    sc.add(f'<ellipse cx="760" cy="90" rx="66" ry="8" fill="{P["hill_mid"]}"/>')
    # a taller stump of masonry on the far side, where the tower stood
    sc.add(f'<path d="M776,84 L776,60 L781,60 L781,55 L787,55 L787,63 L793,63 L793,84Z" fill="{P["stone_lit"]}"/>'
           f'<path d="M776,84 L776,60 L781,60 L781,84Z" fill="{P["stone"]}"/>'
           f'<path d="M776,68 H793 M776,75 H793 M781,58 H787" stroke="{P["stone_dark"]}" stroke-width=".7" opacity=".7"/>')
    ring_walls(sc, 760, 89, 62, 8)
    # fallen blocks tumbled down the slopes
    for x, dy, s in [(700, 6, 3), (716, 10, 2.4), (812, 8, 3), (826, 16, 2.6), (842, 30, 3.4), (690, 22, 2.2), (858, 44, 2.6), (676, 40, 2.4)]:
        boulder(sc, x, amon_sul(x) + dy, s, P["stone_lit"], P["stone"], P["stone_dark"])

    # the path climbing the western side from the dell
    trail = "M548,262 C580,250 600,236 612,226 C628,212 664,206 676,190 C688,174 676,160 690,146 C702,134 716,124 728,112"
    sc.add(f'<path d="{trail}" fill="none" stroke="{P["path"]}" stroke-width="1.4" stroke-dasharray="5 3" opacity=".7"/>')

    # the dell under the western side, and the little fire in it
    fx, fy = 604, 231
    sc.add(f'<ellipse cx="{fx}" cy="{fy + 1}" rx="34" ry="8" fill="#10131f"/>'
           f'<path d="M{fx - 34},{fy + 1} A34,8 0 0 1 {fx + 34},{fy + 1}" fill="none" stroke="#3a4466" stroke-width="1.6"/>'
           f'<path d="M{fx - 30},{fy + 5} A30,6 0 0 0 {fx + 30},{fy + 5}" fill="none" stroke="#0b0d16" stroke-width="2.4"/>')
    sc.add(f'<circle cx="{fx}" cy="{fy}" r="46" fill="{sc.rad("fireglow", [(0, P["fire"], .55), (.3, P["ember"], .2), (1, P["ember"], 0)])}"/>')
    sc.add(f'<path d="M{fx - 3},{fy + 2} L{fx - 1},{fy - 5} L{fx + .5},{fy - 2} L{fx + 2},{fy - 7} L{fx + 3.5},{fy + 2}Z" fill="{P["fire"]}"/>'
           f'<path d="M{fx - 1},{fy + 2} L{fx + 1},{fy - 3} L{fx + 2.2},{fy + 2}Z" fill="{P["fire_core"]}"/>'
           f'<path d="M{fx - 5},{fy + 3} L{fx + 5},{fy + 1.5} M{fx - 4},{fy + 1.5} L{fx + 6},{fy + 3}" stroke="#3a2418" stroke-width="1.2"/>')
    sx = fx - 22
    sc.add(f'<path d="M{sx - 2},{fy + 2} L{sx - 1.6},{fy - 9} L{sx + 1.6},{fy - 9} L{sx + 2},{fy + 2}Z" fill="#0d0f18"/><circle cx="{sx}" cy="{fy - 10.5}" r="1.8" fill="#0d0f18"/>'
           f'<path d="M{sx + 2.4},{fy - 12} L{sx + 3.4},{fy + 2}" stroke="#0d0f18" stroke-width=".9"/>')
    sc.smoke(fx + 1, fy - 9, 7, "#5a6584", .3, -1.4)
    for k in range(6):  # sparks
        sc.add(f'<circle cx="{f(fx + sc.r(-5, 5))}" cy="{f(fy - sc.r(8, 22))}" r=".7" fill="{P["fire"]}" opacity="{f(sc.r(.4, .9))}"/>')

    # scrub, bracken and boulders on the hill's lower slopes
    for _ in range(34):
        x = sc.r(440, 1090)
        y0 = amon_sul(x)
        y = max(y0 + 26, sc.r(200, 296))
        if y > 300 or abs(x - fx) < 40 and abs(y - fy) < 14:
            continue
        scrub(sc, x, y, sc.r(2.6, 5), "#1b2033", "#2b3452" if x > 760 else None)
    for x, y, s in [(520, 268, 9), (560, 282, 7), (980, 262, 10), (1010, 278, 8), (890, 236, 7), (650, 262, 6), (930, 284, 12), (470, 286, 11)]:
        boulder(sc, x, y, s, "#4a5578", "#262c43", "#141826")

    # ground mist lying in the low places round the hill's foot
    mist = sc.rad("mist", [(0, "#8f9cc6", .16), (.6, "#8f9cc6", .07), (1, "#8f9cc6", 0)])
    for cx, cy, rx in [(300, 262, 280), (1150, 268, 320), (1470, 256, 220), (540, 286, 180)]:
        sc.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="16" fill="{mist}"/>')

    # foreground: dark heath, big stones and thorn, fading to the page
    fg = sc.ridge(300, 6, [(1.6, 1), (4.1, .4)], "#171b28", seed=6.2)
    for x in range(-10, W + 10, 13):
        if sc.r(0, 1) < .6:
            scrub(sc, x + sc.r(-5, 5), sc.y_at(fg, x) + sc.r(4, 30), sc.r(5, 10), "#11141f")
    for x, s in [(150, 18), (240, 12), (380, 22), (1180, 16), (1300, 26), (1480, 14)]:
        boulder(sc, x, sc.y_at(fg, x) + 26, s, "#38425f", "#1d2234", "#10131d")
    sc.ridge(340, 4, [(2.1, 1), (5, .4)], P["ground"], seed=8.1)
    sc.tufts(320, 400, 160, ["#1d2232", "#20263a", "#1a1e2c"], 6, 16)
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build().save(f"{out}/weathertop.svg", "Weathertop by moonlight")
