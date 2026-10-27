"""The Shire: Hobbiton in high summer (and, for home mode, at harvest).

Bag End's round green door under the oak on the Hill, more hobbit-holes in the
lower slopes, the Party Tree in its field, the Water with the mill and the
arched bridge, patchwork fields and hedgerows, chimney smoke, a summer sky.
"""
import math
import re
import sys
from contextlib import contextmanager
from scene_kit import Scene, W, H, f

SUMMER = dict(
    sky=[(0, "#86b9de"), (.55, "#bfdbe9"), (1, "#f4ecc6")], sun="#fff4c8",
    cloud="#ffffff", cloud_shade="#d6e2ea",
    far1="#a8c4b7", far2="#93b593", haze="#e9efd6",
    field=["#b9cf6a", "#cfc96c", "#a3c35c", "#d9cf84", "#8fb653"], hedge="#4d7a2f", hedge_shade="#3a6024",
    hill="#7aa84a", hill_light="#93c05a", hill_shade="#5f8c38",
    leaf="#4f8a34", leaf_shade="#3a6a26", leaf_light="#78ad4e", trunk="#5b3e22",
    water="#79b2c9", water_light="#d4ecf2", stone="#c9b896", stone_shade="#a8977a", roof="#8b5a3a", wood="#7a5230",
    path="#e3d29d", path_edge="#cbb67c",
    doors=["#2f6b3a", "#d9a72e", "#b2432f", "#3b6ea8"], brass="#e0b94e",
    grass=["#5d8f37", "#6fa043", "#4a7a2c", "#82b14f"], flowers=["#f4d443", "#ffffff", "#c56cb2", "#e5683d", "#f1a6c2"],
    smoke="#f3f1ea", bird="#4b5a63", harvest=False,
)
HARVEST = dict(SUMMER,
    sky=[(0, "#9cc3db"), (.55, "#d7dfd6"), (1, "#f6e1b0")], sun="#ffe7b0", cloud_shade="#e2d9cc",
    far1="#b9bf9c", far2="#a9b07c", haze="#efe4c4",
    field=["#e0b85a", "#d6a84a", "#c9b45c", "#e8c977", "#b9a24a"], hedge="#6b7a32", hedge_shade="#55622a",
    hill="#9aa452", hill_light="#b3b866", hill_shade="#7e8a40",
    leaf="#c0863a", leaf_shade="#9a5f27", leaf_light="#dcab55",
    grass=["#a39a48", "#8f8a3c", "#b8a957", "#7e7c34"], flowers=["#f4d443", "#e5683d", "#ffffff", "#c9862f"],
    harvest=True,
)


@contextmanager
def swing(sc, x, y):
    """The leaf of a door or gate; the viewer folds it towards its hinge at (x, y)."""
    sc.add(f'<g class="swing" data-origin="{f(x)} {f(y)}">')
    yield
    sc.add("</g>")


def door(sc, x, y, rr, colour, brass, stone, stone_shade, wood, window=True, flip=1, hinge=False, lamp=False):
    """A round hobbit door in a stone ring, with a brass knob, and a round window beside it.
    hinge: the leaf swings open on its left edge onto a lamplit hall.
    lamp: the window pane shows the sky (off-lit) until the lamps are lit (on-lit)."""
    sc.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr * 1.28)}" fill="{stone_shade}"/>'
           f'<circle cx="{f(x)}" cy="{f(y - 1)}" r="{f(rr * 1.2)}" fill="{stone}"/>')
    if hinge:  # the hall behind the door, seen when it opens
        sc.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" fill="#3a2716"/>'
               f'<circle cx="{f(x + rr * .15)}" cy="{f(y + rr * .1)}" r="{f(rr * .72)}" fill="#f2c46a" opacity=".85"/>'
               f'<rect x="{f(x - rr * .7)}" y="{f(y + rr * .55)}" width="{f(rr * 1.4)}" height="{f(rr * .3)}" fill="#8a4b2a"/>')
    g = [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" fill="{colour}"/>']
    for i in range(-3, 4):  # planks
        h = math.sqrt(max(0, rr * rr - (i * rr * .27) ** 2))
        g.append(f'<path d="M{f(x + i * rr * .27)},{f(y - h)} V{f(y + h)}" stroke="#000" stroke-opacity=".14" stroke-width="1"/>')
    g.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr * .2)}" fill="{brass}"/>')
    g.append(f'<circle cx="{f(x - rr * .06)}" cy="{f(y - rr * .06)}" r="{f(rr * .08)}" fill="#fff6c9" opacity=".8"/>')
    if hinge:
        with swing(sc, x - rr, y):
            sc.add("".join(g))
    else:
        sc.add("".join(g))
    g = [f'<rect x="{f(x - rr * 1.25)}" y="{f(y + rr * .98)}" width="{f(rr * 2.5)}" height="{f(rr * .22)}" fill="{stone_shade}"/>']
    if window:
        wx, wy = x + flip * rr * 2.15, y - rr * .1
        if lamp:
            g.append(f'<circle class="on-lit" cx="{f(wx)}" cy="{f(wy)}" r="{f(rr * 1.7)}" fill="url(#lampglow)"/>')
        g.append(f'<circle cx="{f(wx)}" cy="{f(wy)}" r="{f(rr * .52)}" fill="{wood}"/>')
        g.append(f'<circle cx="{f(wx)}" cy="{f(wy)}" r="{f(rr * .4)}" fill="#f6dc8a"/>')
        if lamp:
            g.append(f'<circle class="off-lit" cx="{f(wx)}" cy="{f(wy)}" r="{f(rr * .4)}" fill="#b9d3d6"/>'
                     f'<path class="off-lit" d="M{f(wx - rr * .25)},{f(wy + rr * .1)} l{f(rr * .3)},{f(-rr * .3)}" stroke="#fff" stroke-width="1.2" opacity=".8"/>'
                     f'<circle class="on-lit" cx="{f(wx)}" cy="{f(wy)}" r="{f(rr * .3)}" fill="#ffb84a"/>')
        g.append(f'<path d="M{f(wx - rr * .4)},{f(wy)} H{f(wx + rr * .4)} M{f(wx)},{f(wy - rr * .4)} V{f(wy + rr * .4)}" stroke="{wood}" stroke-width="1.6"/>')
        # window box of flowers
        for k in range(6):
            g.append(f'<circle cx="{f(wx - rr * .45 + k * rr * .18)}" cy="{f(y + rr * .5)}" r="{f(rr * .12)}" fill="{["#e5683d", "#f4d443", "#ffffff"][k % 3]}"/>')
    sc.add("".join(g))


def tufts(sc, y0, y1, n, cols, hmin=6, hmax=16, x0=-30, x1=W + 30, skip=None):
    """Grass blades, written compactly: whole-pixel points, one group per colour."""
    by = {c: [] for c in cols}
    for _ in range(n):
        x, y = sc.r(x0, x1), sc.r(y0, y1)
        c = sc.rnd.choice(cols)
        h, lean = sc.r(hmin, hmax), sc.r(-3, 3)
        if skip and skip(x, y):
            continue
        by[c].append(f"M{x - 2:.0f},{y:.0f}Q{x + lean:.0f},{y - h:.0f} {x + lean * 1.4:.0f},{y - h - 1:.0f}Q{x + 1:.0f},{y - h * .5:.0f} {x + 2:.0f},{y:.0f}Z")
    sc.add("".join(f'<path fill="{c}" d="{"".join(d)}"/>' for c, d in by.items() if d))


def flowers(sc, y0, y1, n, cols, rmin, rmax, x0=0, x1=W, skip=None):
    by = {c: [] for c in cols}
    for _ in range(n):
        x, y, r = sc.r(x0, x1), sc.r(y0, y1), sc.r(rmin, rmax)
        c = sc.rnd.choice(cols)
        if skip and skip(x, y):
            continue
        by[c].append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}"/>')
    sc.add("".join(f'<g fill="{c}">{"".join(v)}</g>' for c, v in by.items() if v))


def fence(sc, x0, y0, x1, y1, n, wood):
    g = [f'<path d="M{f(x0)},{f(y0 - 6)} L{f(x1)},{f(y1 - 6)} M{f(x0)},{f(y0 - 2)} L{f(x1)},{f(y1 - 2)}" stroke="{wood}" stroke-width="1.6"/>']
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        g.append(f'<rect x="{f(x - 1.3)}" y="{f(y - 10)}" width="2.6" height="11" fill="{wood}"/>')
    sc.add("".join(g))


def river_edges():
    """Top and bottom banks of the Water as (x, y) polylines, so the bridge and mill can sit on them."""
    xs = range(-40, W + 41, 20)
    top = [(x, 318 + 4 * math.sin(x / 260 + 1) + 2 * math.sin(x / 97)) for x in xs]
    bot = [(x, 341 + 3 * math.sin(x / 310 + 2) + 1.5 * math.sin(x / 83)) for x in xs]
    return top, bot


def poly(pts):
    return " L".join(f"{f(a)},{f(b)}" for a, b in pts)


def build(P, seed=7):
    sc = Scene(seed)
    sc.rad("lampglow", [(0, "#ffd27a", .9), (.4, "#ffc35a", .35), (1, "#ffc35a", 0)])
    with sc.layer("sky", 0):
        sc.sky(sc.lin("sky", P["sky"]))
        sc.add(f'<circle cx="1210" cy="58" r="190" fill="{sc.rad("sun", [(0, P["sun"], .95), (.25, P["sun"], .45), (1, P["sun"], 0)])}"/>')
        for cx, cy, s, op in [(250, 72, 38, .95), (610, 44, 26, .8), (980, 96, 30, .9), (1420, 70, 44, .95), (1560, 118, 22, .7), (90, 130, 20, .6)]:
            with sc.fx("cloud"):
                sc.cloud(cx, cy, s, P["cloud"], P["cloud_shade"], op)
        with sc.fx("birds"):
            sc.birds([(520, 92), (538, 84), (552, 95), (1080, 60), (1094, 66)], P["bird"], .9)

    with sc.layer("far", .15):
        # far country: the hills beyond Hobbiton, softened by haze
        far = sc.ridge(182, 9, [(1.3, 1), (3.1, .5), (7, .25)], P["far1"], seed=1.2)
        sc.add(f'<rect x="-30" y="160" width="{W + 60}" height="60" fill="{sc.lin("haze", [(0, P["haze"], 0), (1, P["haze"], .55)])}"/>')
        for i in range(70):  # copses on the far hills
            x = sc.r(0, W)
            y = sc.y_at(far, x)
            sc.add(f'<circle cx="{f(x)}" cy="{f(y + 2)}" r="{f(sc.r(2.5, 5))}" fill="{P["far2"]}"/>')
        mid = sc.ridge(208, 10, [(1.7, 1), (4.3, .4)], P["far2"], seed=2.4)

        # patchwork fields with hedgerows on the middle slopes
        for x0 in range(-20, W, 62):
            if 470 < x0 < 1160:
                continue
            w = sc.r(46, 70)
            y0 = sc.y_at(mid, x0) + 4
            col = sc.rnd.choice(P["field"])
            d = f"M{f(x0)},{f(y0)} L{f(x0 + w)},{f(sc.y_at(mid, x0 + w) + 4)} L{f(x0 + w + 6)},{f(y0 + 26)} L{f(x0 + 4)},{f(y0 + 28)}Z"
            sc.add(f'<path d="{d}" fill="{col}"/>')
            for k in range(3):  # crop rows
                yy = y0 + 7 + k * 7
                sc.add(f'<path d="M{f(x0 + 3)},{f(yy)} L{f(x0 + w + 2)},{f(yy - 1)}" stroke="#000" stroke-opacity=".07" stroke-width="1.2"/>')
            if P["harvest"] and sc.r(0, 1) < .5:  # stooks of wheat
                for k in range(3):
                    hx, hy = x0 + 10 + k * 16, y0 + 18
                    sc.add(f'<path d="M{f(hx - 4)},{f(hy)} L{f(hx)},{f(hy - 9)} L{f(hx + 4)},{f(hy)}Z" fill="#c99a3a"/>')
            sc.hedge([(x0 + t, sc.y_at(mid, x0 + t) + 4) for t in range(0, int(w), 6)], 2.6, P["hedge"], P["hedge_shade"])
        for x in [60, 180, 330, 1230, 1330, 1510]:  # hedgerow trees
            sc.tree(x, sc.y_at(mid, x) + 6, sc.r(14, 20), P["leaf"], P["leaf_shade"], P["leaf_light"], P["trunk"])

    top, bot = river_edges()
    with sc.layer("hill", .4):
        # the Party Field and its great tree, left
        right = sc.ridge(250, 9, [(1.2, 1), (2.9, .5)], P["hill_shade"], seed=6.7)
        party = sc.ridge(246, 10, [(1.1, 1), (2.6, .5)], sc.lin("partyg", [(0, P["hill_light"]), (.5, P["hill"])], x2=1, y2=0), seed=4.1, x1=1000)
        py = sc.y_at(party, 205)
        with sc.hot("shire-partytree", "The Party Tree", "The great tree in the Party Field, strung with bunting for the next birthday feast.", "leaves"):
            with sc.fx("sway"):
                sc.tree(205, py + 10, 62, P["leaf"], P["leaf_shade"], P["leaf_light"], P["trunk"], kind="big")
            # bunting on the Party Tree
            g = [f'<path d="M145,{f(py - 36)} Q212,{f(py - 24)} 285,{f(py - 36)}" fill="none" stroke="#6b4a2e" stroke-width=".8"/>']
            for i, x in enumerate([150, 175, 200, 225, 250, 275]):
                y = py - 34 + abs(x - 212) * .12
                g.append(f'<path d="M{f(x)},{f(y)} l5,9 l5,-9Z" fill="{["#e5683d", "#f4d443", "#3b6ea8", "#ffffff"][i % 4]}"/>')
            sc.add("".join(g))

        # the Hill, with Bag End under its oak
        hill_pts = []
        for x in range(520, 1141, 6):
            t = (x - 830) / 310
            hill_pts.append((x, 158 + 150 * (t * t) ** 1.15 + 6 * math.sin(x / 37)))
        d = "M" + poly(hill_pts) + f" L1140,{H} L520,{H}Z"
        # the sun sits high right, so the left flank is in light haze and the right in full sun
        sc.add(f'<path d="{d}" fill="{sc.lin("hillg", [(0, P["hill"]), (.45, P["hill_light"]), (1, P["hill"])], x2=1, y2=0)}"/>')
        sc.add(f'<path d="{d}" fill="{sc.lin("hillv", [(0, P["hill_shade"], 0), (.55, P["hill_shade"], 0), (1, P["hill_shade"], .55)])}"/>')
        # hedges stepping round the Hill's shoulders
        for k, (a0, a1, dy) in enumerate([(560, 700, 30), (960, 1110, 34), (640, 760, 62), (900, 1040, 66)]):
            sc.hedge([(x, sc.y_at(hill_pts, x) + dy) for x in range(a0, a1, 7)], 3.2, P["hedge"], P["hedge_shade"])
        with sc.fx("sway"):
            sc.tree(872, 172, 52, P["leaf"], P["leaf_shade"], P["leaf_light"], P["trunk"], kind="big")  # the oak over Bag End
        sc.add(f'<rect x="776" y="196" width="5" height="18" fill="#6b5a4a"/><rect x="774" y="194" width="9" height="4" fill="#4e4136"/>')
        with sc.fx("smoke"):
            sc.smoke(778, 188, 9, P["smoke"], .55, 1.2)
        # garden terraces and the path down
        sc.add(f'<path d="M760,276 Q790,268 830,270 Q880,272 905,282 L905,290 Q860,281 830,280 Q790,279 760,286Z" fill="{P["stone"]}" opacity=".8"/>')
        fence(sc, 742, 283, 790, 276, 6, P["wood"])
        fence(sc, 870, 276, 920, 285, 6, P["wood"])
        with sc.hot("shire-bagend", "Bag End", "The finest smial on the Hill, dug in under the old oak above a garden full of flowers.", "swing"):
            door(sc, 830, 248, 19, P["doors"][0], P["brass"], P["stone"], P["stone_shade"], P["wood"], flip=1, hinge=True)
            sc.add(f'<circle cx="788" cy="243" r="9" fill="{P["wood"]}"/><circle cx="788" cy="243" r="7" fill="#f6dc8a"/>')
        flowers(sc, 262, 282, 60, P["flowers"], 1.4, 2.6, 740, 930)
        sc.add(f'<rect x="872" y="262" width="22" height="3" fill="{P["wood"]}"/><rect x="874" y="265" width="2" height="6" fill="{P["wood"]}"/><rect x="890" y="265" width="2" height="6" fill="{P["wood"]}"/>')  # bench

        # lower slopes with more hobbit-holes: Bagshot Row
        row = sc.ridge(258, 8, [(1.4, 1), (3.3, .4)], P["hill"], seed=5.3, x0=300, x1=820, taper=110)
        with sc.hot("shire-bagshot", "Bagshot Row", "Smaller smials dug into the lower slope; their lamps go on as the day ends.", "light"):
            door(sc, 452, 285, 13, P["doors"][1], P["brass"], P["stone"], P["stone_shade"], P["wood"], flip=1, lamp=True)
            door(sc, 612, 288, 12, P["doors"][2], P["brass"], P["stone"], P["stone_shade"], P["wood"], flip=-1, lamp=True)
            sc.add(f'<rect x="478" y="{f(sc.y_at(row, 478) - 6)}" width="4" height="12" fill="#6b5a4a"/>')
            with sc.fx("smoke"):
                sc.smoke(480, sc.y_at(row, 478) - 10, 7, P["smoke"], .45, .9)
            # washing line between two posts
            sc.add(f'<path d="M520,282 V266 M570,284 V268 M520,267 Q545,272 570,269" stroke="{P["wood"]}" stroke-width="1.3" fill="none"/>')
            for i, c in enumerate(["#ffffff", "#c56cb2", "#3b6ea8", "#f4d443"]):
                sc.add(f'<rect x="{528 + i * 9}" y="{269 + (1.5 if i in (1, 2) else 0)}" width="6" height="{8 if i % 2 else 6}" fill="{c}"/>')
        flowers(sc, 280, 300, 45, P["flowers"], 1.2, 2.2, 400, 700)
        for i in range(5):  # vegetable rows
            sc.add(f'<path d="M{660 + i * 2},{296 + i * 4} h46" stroke="{P["leaf"]}" stroke-width="2.5" stroke-dasharray="3 3"/>')

        # right slopes: another smial, orchards
        right = sc.ridge(256, 8, [(1.2, 1), (2.9, .5)], P["hill"], seed=6.7, x0=1010, x1=W + 120, taper=110)
        door(sc, 1190, 282, 13, P["doors"][3], P["brass"], P["stone"], P["stone_shade"], P["wood"], flip=-1)
        sc.add(f'<rect x="1222" y="{f(sc.y_at(right, 1222) - 4)}" width="4" height="11" fill="#6b5a4a"/>')
        with sc.fx("smoke"):
            sc.smoke(1224, sc.y_at(right, 1222) - 8, 7, P["smoke"], .45, 1.1)
        for x in range(1290, 1600, 46):  # orchard
            y = sc.y_at(right, x) + 26
            sc.tree(x, y, 15, P["leaf"], P["leaf_shade"], P["leaf_light"], P["trunk"])
            for k in range(4):
                sc.add(f'<circle cx="{f(x + sc.r(-9, 9))}" cy="{f(y - 16 + sc.r(-6, 6))}" r="1.8" fill="{"#d9483a" if not P["harvest"] else "#e08a2a"}"/>')

        # the lanes: from the bridge up to Bag End, and along Bagshot Row past the Party Field and away
        lane = "M1052,326 C1046,310 1010,301 950,299 C905,297 878,293 862,288 C848,284 837,280 830,276"
        branch = "M905,298 C820,304 700,306 620,300 C560,296 500,297 455,300 C400,303 340,307 280,305 C200,302 110,308 -40,303"
        spur = "M452,300 V296"
        for dpath, wdt in [(lane, 11), (branch, 8), (spur, 6)]:
            sc.add(f'<path d="{dpath}" fill="none" stroke="{P["path_edge"]}" stroke-width="{wdt + 3}" stroke-linecap="round"/>')
        for dpath, wdt in [(lane, 11), (branch, 8), (spur, 6)]:
            sc.add(f'<path d="{dpath}" fill="none" stroke="{P["path"]}" stroke-width="{wdt}" stroke-linecap="round"/>')

    with sc.layer("water", .7):
        # the Water
        d = "M" + poly(top) + " L" + poly(bot[::-1]) + "Z"
        sc.add(f'<path d="{d}" fill="{P["water"]}"/>')
        sc.add(f'<path d="M{poly(top)}" fill="none" stroke="#5d9ab3" stroke-width="2" opacity=".6"/>')
        with sc.fx("water"):
            g = []
            for i in range(44):
                x = sc.r(0, W)
                y = sc.r(Scene.y_at(top, x) + 5, Scene.y_at(bot, x) - 4)
                g.append(f"M{x:.0f},{y:.0f}h{sc.r(8, 22):.0f}")
            sc.add(f'<path d="{"".join(g)}" stroke="{P["water_light"]}" stroke-width="1.3" stroke-linecap="round" opacity=".8"/>')

        # the near bank, rising to the foreground
        sc.ridge(345, 6, [(2.1, 1), (5, .4)], P["hill_shade"], seed=8.8)

        # the mill, its wheel turning in a stone mill-race
        mx, my = 1340, 318
        with sc.hot("shire-mill", "The Mill", "The miller's wheel dips into the Water and turns the stones that grind the Shire's flour.", "splash"):
            sc.add(f'<rect x="{mx}" y="{my - 44}" width="66" height="46" fill="{P["stone"]}"/>'
                   f'<path d="M{mx},{my - 30} h66 M{mx},{my - 16} h66" stroke="{P["stone_shade"]}" stroke-width=".8" opacity=".6"/>'
                   f'<path d="M{mx - 6},{my - 44} L{mx + 33},{my - 70} L{mx + 72},{my - 44}Z" fill="{P["roof"]}"/>'
                   f'<rect x="{mx + 44}" y="{my - 66}" width="7" height="14" fill="{P["stone_shade"]}"/>'
                   f'<rect x="{mx + 12}" y="{my - 32}" width="12" height="14" fill="#f6dc8a"/><rect x="{mx + 38}" y="{my - 26}" width="13" height="26" fill="{P["wood"]}"/>')
            with sc.fx("smoke"):
                sc.smoke(mx + 47, my - 72, 8, P["smoke"], .5, 1.3)
            cx, cy, rr = mx - 14, my + 2, 22
            sc.add(f'<path d="M{cx - 27},{my - 2} H{mx + 2} V{my + 13} H{cx - 27}Z" fill="#4f8ba3"/>'  # the race, walled in stone
                   f'<path d="M{cx - 29},{my - 3} H{mx}" stroke="{P["stone_shade"]}" stroke-width="3"/>'
                   f'<rect x="{cx - 32}" y="{my - 4}" width="6" height="18" fill="{P["stone"]}"/><rect x="{cx - 32}" y="{my - 4}" width="6" height="2" fill="{P["stone_shade"]}"/>')
            sc.add(f'<rect x="{cx - 3}" y="{cy - 3}" width="{mx - cx + 3}" height="6" fill="{P["wood"]}"/>'  # the axle into the mill
                   f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{P["wood"]}" stroke-width="3"/>'
                   f'<circle cx="{cx}" cy="{cy}" r="{rr - 7}" fill="none" stroke="{P["wood"]}" stroke-width="1.5"/>' +
                   "".join(f'<path d="M{cx},{cy} L{f(cx + rr * math.cos(a))},{f(cy + rr * math.sin(a))}" stroke="{P["wood"]}" stroke-width="2"/>'
                           f'<path d="M{f(cx + rr * math.cos(a))},{f(cy + rr * math.sin(a))} l{f(-5 * math.sin(a))},{f(5 * math.cos(a))}" stroke="{P["wood"]}" stroke-width="3.2"/>'
                           for a in [i * math.pi / 6 for i in range(12)]) +
                   f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="{P["stone_shade"]}"/>')
            # the water closing over the lower paddles, with foam where they bite
            sc.add(f'<path d="M{cx - 26},{my + 13} Q{cx},{my + 9} {mx + 2},{my + 13} V{my + 24} H{cx - 26}Z" fill="{P["water"]}"/>'
                   f'<path d="M{cx - 18},{my + 12} q5,-3 9,0 q5,-3 9,0 q5,-3 9,0 q5,-3 9,0" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" opacity=".9"/>'
                   f'<circle cx="{cx - 20}" cy="{my + 8}" r="1.6" fill="#fff" opacity=".8"/><circle cx="{cx - 24}" cy="{my + 4}" r="1.1" fill="#fff" opacity=".7"/>'
                   f'<path d="M{cx + 6},{my + 18} h16 M{cx - 12},{my + 21} h12" stroke="{P["water_light"]}" stroke-width="1.2" stroke-linecap="round"/>')

        # the stone bridge, hump-backed, carrying the lane over the Water from the far bank to the near
        F = (1046, Scene.y_at(top, 1046) + 1)
        N = (944, Scene.y_at(bot, 944) + 5)

        def c(u, dy=0.0):
            return (F[0] + (N[0] - F[0]) * u, F[1] + (N[1] - F[1]) * u - 13 * math.sin(math.pi * u) + dy)

        def depth(u):  # deck to waterline
            return 3 + 19 * math.sin(math.pi * u) ** .6
        us = [i / 16 for i in range(17)]
        tufts(sc, 338, 400, 620, P["grass"], 6, 18, skip=lambda x, y: y > 343 and abs(x - near_x(y)) < 9 + (y - 343) * .3)
        with sc.hot("shire-bridge", "The Bridge", "An old stone bridge where the lane from the Hill crosses the Water.", "pulse"):
            sc.add(f'<path d="M{poly([c(u, depth(u) + 1) for u in us])}" fill="none" stroke="#5d9ab3" stroke-width="5" opacity=".7"/>')  # its shadow on the water
            face = [c(u) for u in us] + [c(u, depth(u)) for u in us[::-1]]
            sc.add(f'<path d="M{poly(face)}Z" fill="{P["stone"]}"/>')
            au = [.17 + .66 * i / 14 for i in range(15)]
            arch = [c(u, depth(u) - 15 * math.sin(math.pi * (u - .17) / .66) ** .8) for u in au]
            sc.add(f'<path d="M{poly(arch)}Z" fill="#3d6c7d"/>'
                   f'<path d="M{poly([c(u, depth(u) - 1) for u in au])}" fill="none" stroke="{P["water_light"]}" stroke-width="1.2" opacity=".6"/>'
                   f'<path d="M{poly(arch)}" fill="none" stroke="{P["stone_shade"]}" stroke-width="1.6"/>')
            # voussoirs round the arch, and a few courses of stone
            vs = "".join(f"M{f(arch[i][0])},{f(arch[i][1])}v-3" for i in range(2, 13, 2))
            stones = "".join(f"M{f(c(u, 5 + k * 6)[0])},{f(c(u, 5 + k * 6)[1])}h5" for k in range(2) for u in [.06, .9])
            sc.add(f'<path d="{vs}{stones}" stroke="{P["stone_shade"]}" stroke-width="1" opacity=".8"/>')
            # the deck: far parapet, the lane between, the near parapet with its coping
            sc.add(f'<path d="M{poly([c(u, -9) for u in us])}" fill="none" stroke="{P["stone_shade"]}" stroke-width="3" stroke-linecap="round"/>'
                   f'<path d="M{poly([c(u, -7) for u in us] + [c(u, -1) for u in us[::-1]])}Z" fill="{P["path"]}"/>'
                   f'<path d="M{poly([c(u, -1) for u in us])}" fill="none" stroke="{P["stone_shade"]}" stroke-width="4" stroke-linecap="round"/>'
                   f'<path d="M{poly([c(u, -2) for u in us])}" fill="none" stroke="{P["stone"]}" stroke-width="2" stroke-linecap="round"/>')
        # the lane on the near bank, widening as it wanders down out of the picture
        cl = [(N[0] - 2 - t * 26 - 18 * t * t, N[1] - 4 + t * 80) for t in [i / 10 for i in range(11)]]
        hw = [5 + 6 * i / 10 for i in range(11)]
        lp = [(x - w, y) for (x, y), w in zip(cl, hw)] + [(x + w, y) for (x, y), w in zip(cl[::-1], hw[::-1])]
        sc.add(f'<path d="M{poly(lp)}Z" fill="{P["path"]}" stroke="{P["path_edge"]}" stroke-width="2" stroke-linejoin="round"/>')
        tufts(sc, 352, 400, 50, P["grass"], 5, 12, x0=870, x1=990, skip=lambda x, y: abs(abs(x - near_x(y)) - (5 + (y - 347) * .08)) > 4)

    with sc.layer("front", 1):
        # wildflowers, and fences along the meadow
        flowers(sc, 340, 398, 180, P["flowers"], 1.6, 3.2, skip=lambda x, y: y > 343 and abs(x - near_x(y)) < 12 + (y - 343) * .3)
        fence(sc, 20, 372, 330, 352, 12, P["wood"])
        fence(sc, 1180, 350, 1560, 372, 14, P["wood"])
    return sc


def near_x(y):
    """Rough centre of the near-bank lane at height y (for keeping grass and flowers off it)."""
    t = max(0, (y - 344) / 80)
    return 942 - t * 26 - 18 * t * t


STRUCT = ('<g class="layer"', '<g class="hot"', '<g class="fx ', '<g class="swing"')


def mirrored(sc):
    """Flip left to right: the page's cards cover the right of the banner, so the mill and bridge go left.
    The viewer's groups (layer, hot, fx, swing) stay untransformed so their boxes and hinges are in scene
    coordinates: the drawing between them is wrapped in flipped groups, and swing hinges are mirrored."""
    flip = f'<g transform="translate({W},0) scale(-1,1)">'
    out, open_ = [], False
    for p in sc.parts:
        if p.startswith(STRUCT) or p == "</g>":
            if open_:
                out.append("</g>")
                open_ = False
            if p.startswith('<g class="swing"'):
                p = re.sub(r'data-origin="([-\d.]+) ', lambda m: f'data-origin="{f(W - float(m.group(1)))} ', p)
            out.append(p)
        else:
            if not open_:
                out.append(flip)
                open_ = True
            out.append(p)
    if open_:
        out.append("</g>")
    sc.parts = out
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    mirrored(build(SUMMER)).save(f"{out}/shire.svg", "The Shire in summer")
    mirrored(build(HARVEST, seed=7)).save(f"{out}/home.svg", "The Shire at harvest")
