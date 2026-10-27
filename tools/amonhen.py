"""Amon Hen: Parth Galen above the Falls of Rauros, in early autumn.

Looking west across the Anduin. Amon Hen rises from its woods in the middle,
with the ruined Seat of Seeing on its summit; at its foot the lawn of Parth
Galen and a pebble shore where grey elven boats are drawn up. Downstream, on
the left, the river runs to the lip of Rauros and vanishes into spray;
upstream, on the right, the Tindrock stands out of the water with birds
wheeling round its crown.
"""
import math
import sys
from scene_kit import Scene, W, H, f

P = dict(
    sky=[(0, "#a3c2d1"), (.5, "#d2e0e5"), (1, "#f3eedb")], sun="#fff6dc",
    cloud="#fbfbf7", cloud_shade="#d9e2e4",
    far1="#bccbcf", far2="#a9bcbf", haze="#e6ecea",
    rock="#b7b4aa", rock_light="#d3d0c4", rock_shade="#959389",
    seat="#d8d4c6", seat_shade="#a8a496",
    wood_base="#6d8566",
    leaves=["#86a273", "#93ab76", "#7a976a", "#a3aa66", "#d4b660", "#cc9254", "#b97a56"],
    conifer="#5f7e66", leaf_shade="#647f62", leaf_light="#d9e2b0",
    lawn="#9fb47a", lawn_light="#b6c68a",
    pebble=["#cfcbbf", "#bab6aa", "#a8a598", "#dedad0"],
    boat="#9aa3a3", boat_light="#c6cccb", boat_in="#717b7c",
    water_top="#a2bfca", water_bot="#cad9df", water_light="#f4f8f8", mist="#ffffff",
    bird="#56676d", trunk="#6b5a48",
)


def blobs(sc, circles, fill, extra=""):
    """Many circles drawn as round-capped dots, grouped by size: far smaller than one element each."""
    if not circles:
        return
    by = {}
    for x, y, r in circles:
        by.setdefault(max(1, round(r)) * 2, []).append(f"M{x:.0f},{y:.0f}h0")
    body = "".join(f'<path d="{"".join(v)}" stroke-width="{f(k)}"/>' for k, v in sorted(by.items()))
    sc.add(f'<g stroke="{fill}" stroke-linecap="round"{extra}>{body}</g>')


def poly(pts, close=True):
    return "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + ("Z" if close else "")


def leaf_colour(sc, x, y):
    """Early autumn: mostly green, with drifts of gold and a few trees already turned orange and russet."""
    n = .55 * math.sin(x / 41 + y / 23) + .45 * math.sin(x / 17 - y / 29 + 2) + sc.r(-.45, .45)
    if n > .78:
        return 5 if n > 1.12 else 4
    if n > .5:
        return 3
    if n < -1.05:
        return 6
    return sc.rnd.choice((0, 0, 1, 2))


def forest(sc, top, x0, x1, ybot, rmin, rmax, n, cols, shade, light, conifer, cfrac=.12, band=9):
    """A wooded slope: crowns scattered under the line top(x), drawn back to front in bands,
    each crown a shaded circle, a coloured circle and a soft highlight; some dark spires among them."""
    crowns = []
    step = rmin * 1.3
    x = x0
    while x <= x1:  # the skyline row, so the silhouette is a row of crowns
        crowns.append((x, top(x) + rmin * .9, rmin * sc.r(.9, 1.2)))
        x += step * sc.r(.8, 1.2)
    for _ in range(n):
        x = sc.r(x0, x1)
        t0 = top(x)
        if ybot - t0 < 4:
            continue
        y = sc.r(t0 + rmin, ybot)
        depth = (y - t0) / max(1, ybot - t0)
        crowns.append((x, y, (rmin + (rmax - rmin) * depth) * sc.r(.8, 1.15)))
    crowns.sort(key=lambda c: c[1])
    ymin = crowns[0][1]
    nb = int((crowns[-1][1] - ymin) / band) + 1
    for b in range(nb):
        row = [c for c in crowns if ymin + b * band <= c[1] < ymin + (b + 1) * band]
        if not row:
            continue
        spires = [c for c in row if sc.r(0, 1) < cfrac]
        broad = [c for c in row if c not in spires]
        blobs(sc, [(x + r * .18, y + r * .2, r) for x, y, r in broad], shade)
        by = {}
        for c in broad:
            by.setdefault(leaf_colour(sc, c[0], c[1]), []).append(c)
        for k, cs in sorted(by.items()):
            blobs(sc, [(x, y, r * .9) for x, y, r in cs], cols[k])
        blobs(sc, [(x - r * .32, y - r * .36, r * .36) for x, y, r in broad if sc.r(0, 1) < .3], light, ' opacity=".3"')
        if spires:
            d = "".join(f"M{f(x)},{f(y - r * 2.6)}L{f(x + r * .62)},{f(y + r * .5)}L{f(x - r * .62)},{f(y + r * .5)}Z" for x, y, r in spires)
            sc.add(f'<path d="{d}" fill="{conifer}"/>')


def boat(sc, x, y, L, ang, P):
    """A grey elven boat drawn up on the shore, bow (left or right) lifted a little."""
    h = L * .12
    g = [f'<g transform="translate({f(x)},{f(y)}) rotate({f(ang)})">']
    hull = f"M{f(-L / 2)},{f(-h * 1.15)} Q{f(-L * .32)},{f(h * .55)} 0,{f(h * .6)} Q{f(L * .34)},{f(h * .55)} {f(L / 2)},{f(-h * 1.3)} Q{f(L * .1)},{f(-h * .35)} {f(-L / 2)},{f(-h * 1.15)}Z"
    g.append(f'<ellipse cx="0" cy="{f(h * .75)}" rx="{f(L * .45)}" ry="{f(h * .35)}" fill="#000" opacity=".12"/>')
    g.append(f'<path d="{hull}" fill="{P["boat"]}"/>')
    g.append(f'<path d="M{f(-L * .44)},{f(-h * .78)} Q{f(L * .05)},{f(-h * .1)} {f(L * .44)},{f(-h * .9)} Q{f(L * .05)},{f(-h * .62)} {f(-L * .44)},{f(-h * .78)}Z" fill="{P["boat_in"]}"/>')
    g.append(f'<path d="M{f(-L / 2)},{f(-h * 1.15)} Q{f(L * .05)},{f(-h * .3)} {f(L / 2)},{f(-h * 1.3)}" fill="none" stroke="{P["boat_light"]}" stroke-width="1.3"/>')
    g.append(f'<path d="M{f(-L * .38)},{f(h * .05)} Q0,{f(h * .38)} {f(L * .36)},{f(h * .02)}" fill="none" stroke="#000" stroke-opacity=".12" stroke-width="1"/>')
    g.append("</g>")
    sc.add("".join(g))


def build(P, seed=11):
    sc = Scene(seed)
    sc.sky(sc.lin("sky", P["sky"]))
    # low afternoon sun over the falls, so the spray is lit from behind
    sc.add(f'<circle cx="230" cy="96" r="230" fill="{sc.rad("sun", [(0, P["sun"], .95), (.22, P["sun"], .5), (1, P["sun"], 0)])}"/>')
    for cx, cy, s, op in [(520, 60, 30, .8), (905, 40, 22, .65), (1180, 70, 34, .85), (1490, 48, 40, .9), (40, 40, 22, .5)]:
        sc.cloud(cx, cy, s, P["cloud"], P["cloud_shade"], op)
    # thin streaks of high cloud
    for x, y, w in [(600, 104, 160), (980, 118, 120), (1300, 128, 180), (330, 30, 140)]:
        sc.add(f'<rect x="{x}" y="{y}" width="{w}" height="2.5" rx="1.2" fill="{P["cloud"]}" opacity=".6"/>')

    # far country: the hills of the west bank beyond Amon Hen, and the long fall of the land to the south
    far = sc.ridge(176, 10, [(1.1, 1), (2.7, .6), (6.3, .25)], P["far1"], seed=3.3, x0=330, taper=160)
    for i in range(70):
        x = sc.r(420, W)
        sc.add(f'<circle cx="{f(x)}" cy="{f(sc.y_at(far, x) + 3)}" r="{f(sc.r(2, 4))}" fill="{P["far2"]}"/>')
    sc.add(f'<rect y="150" width="{W}" height="95" fill="{sc.lin("haze", [(0, P["haze"], 0), (1, P["haze"], .75)])}"/>')
    # the lowlands far below Rauros, with the river winding on through them
    low = sc.ridge(214, 3, [(2, 1), (5, .4)], "#b9c9c2", seed=1.1, x0=-140, x1=440, taper=120)
    sc.ridge(224, 2, [(3, 1)], "#a9bdb4", seed=2.2, x0=-140, x1=420, taper=100)
    sc.add(f'<path d="M-20,226 C40,222 90,231 150,228 S240,221 300,226" stroke="#eef3f2" stroke-width="2" fill="none"/>')
    mid = sc.ridge(204, 9, [(1.6, 1), (3.8, .5)], P["far2"], seed=5.1, x0=860, taper=140)

    # the west-bank woods running north (right), behind the Tindrock, softened by haze
    def right_top(x):
        return 214 + 9 * math.sin(x / 61) + 6 * math.sin(x / 23 + 1) - 18 * math.exp(-((x - 1520) / 90) ** 2)
    pts = [(x, right_top(x)) for x in range(960, W + 21, 6)]
    sc.add(f'<path d="{poly(pts, False)} L{W + 20},300 L960,300Z" fill="{P["wood_base"]}"/>')
    forest(sc, right_top, 960, W + 10, 268, 4.5, 6.5, 650, P["leaves"], P["leaf_shade"], P["leaf_light"], P["conifer"], .16, 12)
    sc.add(f'<path d="{poly([(x, y + 2) for x, y in pts], False)} L{W + 20},300 L960,300Z" fill="{sc.lin("hazeR", [(0, P["haze"], .55), (1, P["haze"], .3)])}"/>')

    # the wooded ridge running down from Amon Hen to the falls, ending in grey crags at the lip
    def left_top(x):
        return 200 + .0005 * (x - 560) ** 2 + 5 * math.sin(x / 19) + 3 * math.sin(x / 7.3)
    crag = [(262, 246), (274, 238), (284, 226), (292, 222), (300, 210), (310, 206), (318, 196), (330, 192), (346, 194), (360, 200), (372, 204), (380, 226), (372, 250)]
    sc.add(f'<path d="{poly(crag)}" fill="{P["rock"]}"/>')
    sc.add(f'<path d="M292,222 L300,210 L306,240 L284,244Z M330,192 L346,194 L340,234 L326,240Z" fill="{P["rock_shade"]}" opacity=".6"/>')
    sc.add(f'<path d="M310,206 L318,196 L322,230 L312,236Z" fill="{P["rock_light"]}"/>')
    forest(sc, left_top, 340, 650, 262, 4.5, 7, 480, P["leaves"], P["leaf_shade"], P["leaf_light"], P["conifer"], .14, 12)

    # Amon Hen: steeper toward the falls, a long shoulder northward
    def hen(x):
        t = (x - 770) / (300 if x < 770 else 350)
        return 98 + 176 * abs(t) ** 1.25 - 22 * math.exp(-((x - 950) / 60) ** 2) + 4 * math.sin(x / 23) + 2.5 * math.sin(x / 8.7)
    hp = [(x, hen(x)) for x in range(440, 1131, 5)]
    sc.add(f'<path d="{poly(hp, False)} L1130,300 L440,300Z" fill="{sc.lin("henv", [(0, "#8e9f7c"), (.4, P["wood_base"]), (1, "#6a8263")])}"/>')
    # bare rock crown of the hill
    crown = [(722, 126), (732, 114), (746, 106), (760, 101), (774, 99), (790, 100), (804, 106), (816, 116), (826, 128), (806, 132), (780, 128), (750, 132)]
    sc.add(f'<path d="{poly(crown)}" fill="{P["rock"]}"/>')
    sc.add(f'<path d="M790,100 L804,106 L816,116 L826,128 L806,132 L796,120Z" fill="{P["rock_shade"]}" opacity=".6"/>')
    sc.add(f'<path d="M732,114 L746,106 L760,101 L752,116 L738,122Z" fill="{P["rock_light"]}"/>')
    # woods on the flanks, climbing almost to the crown
    def hen_wood(x):
        return max(hen(x) + 6, 122 if 722 < x < 826 else 0)
    forest(sc, hen_wood, 446, 1124, 274, 5, 9, 1500, P["leaves"], P["leaf_shade"], P["leaf_light"], P["conifer"], .14, 12)
    # light catching the flank that faces the sun
    sc.add(f'<path d="{poly(hp, False)} L1130,300 L440,300Z" fill="{sc.lin("henl", [(0, P["sun"], .4), (.4, P["sun"], 0), (1, P["sun"], 0)], x2=1, y2=0)}"/>')

    # the Seat of Seeing: a long stair up to a high seat raised on four pillars, weathered, a corner fallen
    sx, sy = 774, 100
    st, sh = P["seat"], P["seat_shade"]
    s = [f'<path d="M{sx - 24},{sy + 1} L{sx + 22},{sy + 1} L{sx + 20},{sy - 3} L{sx - 22},{sy - 3}Z" fill="{sh}"/>']
    for k in range(5):  # the stair, climbing from the left to the platform
        s.append(f'<rect x="{sx - 22 + k * 3}" y="{f(sy - 5 - k * 2.2)}" width="{14 - k * 2.4:.1f}" height="2.3" fill="{st}"/>')
    for px in (sx - 7, sx - 2, sx + 3, sx + 8):  # pillars
        s.append(f'<rect x="{px}" y="{sy - 14}" width="2.4" height="11" fill="{st}"/><rect x="{px + 1.6}" y="{sy - 14}" width=".8" height="11" fill="{sh}"/>')
    s.append(f'<rect x="{sx - 9}" y="{sy - 17}" width="21" height="3.2" fill="{st}"/><rect x="{sx - 9}" y="{f(sy - 14.4)}" width="21" height=".8" fill="{sh}"/>')  # platform slab
    # the seat itself: a squared block with a tall back and low arms, the back's top corner broken off
    s.append(f'<path d="M{sx - 2},{sy - 17} V{sy - 21} H{sx + 4} V{sy - 25} L{sx + 5},{sy - 29} H{sx + 8} L{sx + 9},{sy - 27} V{sy - 17}Z" fill="{st}"/>')
    s.append(f'<path d="M{sx - 3},{sy - 21} h3 v-2 h-3Z M{sx + 7.4},{sy - 27} L{sx + 9},{sy - 27} V{sy - 17} H{sx + 7.4}Z" fill="{sh}"/>')
    s.append(f'<path d="M{sx + 16},{sy} l3,-4 l4,1 l1,3Z M{sx + 25},{sy + 2} l2,-3 l3,1 v2Z" fill="{sh}"/>')  # fallen stones
    sc.add("".join(s))

    # the Tindrock, standing in the river upstream
    tb = [(1250, 274), (1256, 246), (1262, 226), (1260, 214), (1266, 190), (1270, 168), (1268, 156), (1276, 132), (1282, 116), (1292, 104),
          (1306, 99), (1330, 97), (1348, 100), (1362, 108), (1368, 124), (1372, 140), (1378, 166), (1376, 178), (1384, 202), (1392, 226),
          (1398, 248), (1412, 274)]
    sc.add(f'<path d="{poly(tb)}" fill="{P["rock"]}"/>')
    sc.add(f'<path d="M1348,100 L1362,108 L1368,124 L1372,140 L1378,166 L1376,178 L1384,202 L1392,226 L1398,248 L1412,274 L1350,274 L1354,212 L1346,160Z" fill="{P["rock_shade"]}" opacity=".75"/>')
    sc.add(f'<path d="M1266,190 L1270,168 L1268,156 L1276,132 L1282,116 L1292,104 L1296,140 L1288,190 L1282,260 L1258,262 L1262,226 L1260,214Z" fill="{P["rock_light"]}" opacity=".7"/>')
    cr = "".join(f"M{x},{y1} L{x + sc.r(-3, 3):.0f},{(y1 + y2) / 2:.0f} L{x + sc.r(-4, 4):.0f},{y2}" for x, y1, y2 in
                 [(1300, 118, 170), (1318, 112, 200), (1338, 126, 250), (1310, 190, 262), (1366, 150, 230), (1284, 200, 258), (1326, 206, 268), (1380, 214, 262)])
    sc.add(f'<path d="{cr}" stroke="{P["rock_shade"]}" stroke-width="1.1" fill="none" opacity=".8"/>')
    for (lx, ly, lw) in [(1270, 172, 20), (1296, 214, 26), (1352, 186, 18), (1320, 150, 14)]:  # ledges, with a little growth on them
        sc.add(f'<path d="M{lx},{ly + 1.5} h{lw}" stroke="{P["rock_shade"]}" stroke-width="1.6"/><path d="M{lx},{ly} h{lw}" stroke="{P["rock_light"]}" stroke-width="1.2"/>')
        blobs(sc, [(lx + sc.r(2, lw - 2), ly - 1.5, sc.r(1.6, 2.6)) for _ in range(3)], P["leaves"][sc.rnd.choice((0, 4, 2))])
    forest(sc, lambda x: 94 + .014 * (x - 1326) ** 2, 1290, 1362, 112, 3.5, 4.5, 60, P["leaves"], P["leaf_shade"], P["leaf_light"], P["conifer"], .3, 6)
    blobs(sc, [(1256, 268, 7), (1268, 270, 6), (1398, 268, 8), (1410, 271, 6)], P["conifer"])  # trees clinging at its feet
    sc.add(f'<path d="{poly(tb)}" fill="{sc.lin("tbh", [(0, P["haze"], .15), (1, P["haze"], .45)])}"/>')
    sc.birds([(1300, 72), (1316, 64), (1342, 70), (1360, 80), (1282, 86), (1330, 56), (1380, 66), (1400, 88)], P["bird"], .6)
    sc.birds([(640, 84), (654, 78)], P["bird"], .7)

    # Parth Galen: a green lawn at the hill's foot running down to the pebble shore
    shore = lambda x: 270 + 12 * math.exp(-((x - 590) / 150) ** 2) + 3 * math.sin(x / 41)
    lawn_top = lambda x: 258 + 4 * math.sin((x - 420) / 60) + 10 * ((x - 600) / 190) ** 2
    lawn = [(x, lawn_top(x)) for x in range(410, 801, 10)] + [(x, shore(x) + 3) for x in range(800, 409, -10)]
    sc.add(f'<path d="{poly(lawn)}" fill="{sc.lin("lawn", [(0, P["lawn_light"]), (1, P["lawn"])])}"/>')
    for tx, ts in [(452, 17), (528, 20), (712, 16)]:  # a few great trees at the lawn's edge, turning
        sc.tree(tx, lawn_top(tx) + 8, ts, P["leaves"][4], "#a9853d", "#ecd58a", P["trunk"])
    sc.tree(760, lawn_top(760) + 10, 14, P["leaves"][0], P["leaf_shade"], P["leaf_light"], P["trunk"])
    sc.tree(612, lawn_top(612) + 8, 15, P["leaves"][5], "#a4662f", "#e8b77a", P["trunk"])
    sc.flowers(262, 276, 26, ["#d4b660", "#cc9254", "#b97a56"], .8, 1.4, 430, 760)  # fallen leaves on the lawn

    # Rauros: the river drops away out of sight and its spray climbs in a lit column
    mist = sc.rad("mist", [(0, P["mist"], .85), (.5, P["mist"], .4), (1, P["mist"], 0)])
    for cx, cy, rx, ry in [(140, 234, 160, 22), (118, 208, 100, 36), (132, 172, 74, 42), (156, 134, 56, 38), (182, 100, 40, 28)]:
        sc.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{mist}"/>')
    for cx, cy, s, op in [(120, 228, 30, .7), (64, 230, 20, .6), (180, 230, 22, .55), (110, 204, 24, .55), (140, 182, 20, .45), (150, 156, 16, .35), (170, 128, 13, .25)]:
        sc.cloud(cx, cy, s, P["mist"], "#e3eaec", op)
    sc.flowers(150, 236, 40, [P["mist"]], .6, 1.3, 40, 230)  # flung droplets catching the light

    # the river, running out to the lip of Rauros on the left
    wtop = [(x, 236 + (shore(x) + 2 - 236) * min(1, max(0, (x - 250) / 170)) ** .8) for x in range(40, W + 21, 8)]
    sc.add(f'<path d="M-20,236 L40,236 {poly(wtop, False).replace("M", "L", 1)} L{W + 20},{H} L-20,{H}Z" fill="{sc.lin("water", [(0, P["water_top"]), (.62, P["water_top"]), (1, P["water_bot"])])}"/>')
    # reflections of the hill and the rock, broken by ripples
    for x0, x1, top, op, col in [(470, 1100, 280, .2, P["wood_base"]), (1252, 1410, 276, .22, P["rock_shade"])]:
        for k in range(14):
            y = top + 4 + k * 4.2
            wid = (x1 - x0) * (1 - k / 16) * sc.r(.75, 1)
            cx = (x0 + x1) / 2 + sc.r(-20, 20)
            sc.add(f'<rect x="{cx - wid / 2:.0f}" y="{f(y)}" width="{wid:.0f}" height="{f(sc.r(1.5, 3.2))}" rx="1.5" fill="{col}" opacity="{f(op * .8 * (1 - k / 15))}"/>')
    # sunlight on the water below the falls' sky
    sc.add(f'<ellipse cx="220" cy="268" rx="300" ry="46" fill="{sc.rad("glint", [(0, P["water_light"], .7), (1, P["water_light"], 0)])}"/>')
    g = []
    for i in range(110):
        x = sc.r(-10, W)
        y = sc.r(Scene.y_at(wtop, min(max(x, 40), W)) + 5, 392)
        near = (y - 240) / 150
        w = sc.r(6, 18) * (1 + near * 1.5)
        lit = abs(x - 220) < 200
        op = "" if lit else ' opacity=".5"'
        g.append(f'<path d="M{x:.0f},{y:.0f}h{w:.0f}" stroke-width="{f(1 + near)}"{op}/>')
    sc.add(f'<g stroke="{P["water_light"]}" stroke-linecap="round">{"".join(g)}</g>')
    sc.add(f'<path d="M24,238 Q150,235 290,239" stroke="{P["mist"]}" stroke-width="2.4" fill="none" opacity=".9"/>')  # foam on the lip
    sc.add(f'<rect x="10" y="226" width="300" height="16" fill="{sc.lin("lip", [(0, P["mist"], 0), (.5, P["mist"], .85), (1, P["mist"], 0)], x2=1, y2=0)}"/>')
    # the race of water toward the lip
    sc.add(f'<g stroke="{P["water_light"]}" stroke-width="1.4" fill="none" opacity=".85">' + "".join(f'<path d="M{x},{y} q30,-2 {l},-1"/>'
                   for x, y, l in [(80, 239, 70), (150, 243, 90), (60, 247, 60), (210, 246, 70), (120, 252, 100), (240, 256, 60), (30, 255, 80)]) + "</g>")
    # the rocky east-bank tip at the far left edge
    sc.add(f'<path d="M-20,150 L4,156 L18,174 L30,206 L44,240 L-20,244Z" fill="{P["rock"]}"/>'
           f'<path d="M4,156 L18,174 L30,206 L44,240 L20,242 L14,190Z" fill="{P["rock_shade"]}" opacity=".6"/>')
    forest(sc, lambda x: 144 + .45 * (x + 20), -20, 14, 166, 4, 5, 26, P["leaves"], P["leaf_shade"], P["leaf_light"], P["conifer"], .4, 6)

    # the pebble shore and the grey boats drawn up on it
    peb = [(x, shore(x) - 1) for x in range(404, 797, 8)]
    sc.add(f'<path d="{poly(peb, False)} L796,{f(shore(796) + 6)} L404,{f(shore(404) + 6)}Z" fill="{P["pebble"][0]}"/>')
    sc.add(f'<path d="{poly([(x, shore(x) + 3) for x in range(404, 797, 8)], False)} L796,{f(shore(796) + 6)} L404,{f(shore(404) + 6)}Z" fill="{P["pebble"][2]}" opacity=".6"/>')
    for k, c in enumerate(P["pebble"]):
        pts = []
        for _ in range(60):
            x = sc.r(408, 792)
            pts.append((x, shore(x) + sc.r(0, 5), sc.r(.6, 1.4)))
        blobs(sc, pts, c)
    boat(sc, 560, shore(560) + 3, 58, -3, P)
    boat(sc, 626, shore(626) + 3, 56, 2, P)
    boat(sc, 690, shore(690) + 2, 54, -2, P)
    # a leaf-bladed paddle leaning on the last boat
    sc.add(f'<path d="M716,{f(shore(716) - 16)} L726,{f(shore(726) + 3)}" stroke="{P["boat_in"]}" stroke-width="1.3"/>'
           f'<ellipse cx="727" cy="{f(shore(727) + 1)}" rx="2" ry="5" transform="rotate(-28 727 {f(shore(727) + 1)})" fill="{P["boat_in"]}"/>')

    # foreground: the near water fading to the page, a few reeds at the corners
    sc.add(f'<rect y="320" width="{W}" height="80" fill="{sc.lin("fade", [(0, "#d0dce1", 0), (1, "#d0dce1", .7)])}"/>')
    reeds = []
    for x0, x1 in [(-10, 220), (1180, 1610)]:
        for _ in range(60):
            x = sc.r(x0, x1)
            y = 400 - sc.r(0, 14)
            h = sc.r(14, 34)
            lean = sc.r(-5, 5)
            reeds.append(f'M{f(x - 1.4)},{f(y)} Q{f(x + lean * .5)},{f(y - h * .6)} {f(x + lean)},{f(y - h)} Q{f(x + 1)},{f(y - h * .5)} {f(x + 1.4)},{f(y)}Z')
    sc.add(f'<path d="{"".join(reeds)}" fill="#8d9f86" opacity=".75"/>')
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build(P).save(f"{out}/amonhen.svg", "Amon Hen above the Anduin")
