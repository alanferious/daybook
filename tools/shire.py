"""The Shire: Hobbiton in high summer (and, for home mode, at harvest).

Bag End's round green door under the oak on the Hill, more hobbit-holes in the
lower slopes, the Party Tree in its field, the Water with the mill and the
arched bridge, patchwork fields and hedgerows, chimney smoke, a summer sky.
"""
import math
import sys
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


def door(sc, x, y, rr, colour, brass, stone, stone_shade, wood, window=True, flip=1):
    """A round hobbit door in a stone ring, with a brass knob, and a round window beside it."""
    g = [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr * 1.28)}" fill="{stone_shade}"/>',
         f'<circle cx="{f(x)}" cy="{f(y - 1)}" r="{f(rr * 1.2)}" fill="{stone}"/>',
         f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" fill="{colour}"/>']
    for i in range(-3, 4):  # planks
        g.append(f'<path d="M{f(x + i * rr * .27)},{f(y - math.sqrt(max(0, rr * rr - (i * rr * .27) ** 2)))} V{f(y + math.sqrt(max(0, rr * rr - (i * rr * .27) ** 2)))}" stroke="#000" stroke-opacity=".14" stroke-width="1"/>')
    g.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr * .2)}" fill="{brass}"/>')
    g.append(f'<circle cx="{f(x - rr * .06)}" cy="{f(y - rr * .06)}" r="{f(rr * .08)}" fill="#fff6c9" opacity=".8"/>')
    g.append(f'<rect x="{f(x - rr * 1.25)}" y="{f(y + rr * .98)}" width="{f(rr * 2.5)}" height="{f(rr * .22)}" fill="{stone_shade}"/>')
    if window:
        wx = x + flip * rr * 2.15
        g.append(f'<circle cx="{f(wx)}" cy="{f(y - rr * .1)}" r="{f(rr * .52)}" fill="{wood}"/>')
        g.append(f'<circle cx="{f(wx)}" cy="{f(y - rr * .1)}" r="{f(rr * .4)}" fill="#f6dc8a"/>')
        g.append(f'<path d="M{f(wx - rr * .4)},{f(y - rr * .1)} H{f(wx + rr * .4)} M{f(wx)},{f(y - rr * .5)} V{f(y + rr * .3)}" stroke="{wood}" stroke-width="1.6"/>')
        # window box of flowers
        for k in range(6):
            g.append(f'<circle cx="{f(wx - rr * .45 + k * rr * .18)}" cy="{f(y + rr * .5)}" r="{f(rr * .12)}" fill="{["#e5683d", "#f4d443", "#ffffff"][k % 3]}"/>')
    sc.add("".join(g))


def fence(sc, x0, y0, x1, y1, n, wood):
    g = [f'<path d="M{f(x0)},{f(y0 - 6)} L{f(x1)},{f(y1 - 6)} M{f(x0)},{f(y0 - 2)} L{f(x1)},{f(y1 - 2)}" stroke="{wood}" stroke-width="1.6"/>']
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        g.append(f'<rect x="{f(x - 1.3)}" y="{f(y - 10)}" width="2.6" height="11" fill="{wood}"/>')
    sc.add("".join(g))


def build(P, seed=7):
    sc = Scene(seed)
    sc.sky(sc.lin("sky", P["sky"]))
    sc.add(f'<circle cx="1210" cy="58" r="190" fill="{sc.rad("sun", [(0, P["sun"], .95), (.25, P["sun"], .45), (1, P["sun"], 0)])}"/>')
    for cx, cy, s, op in [(250, 72, 38, .95), (610, 44, 26, .8), (980, 96, 30, .9), (1420, 70, 44, .95), (1560, 118, 22, .7), (90, 130, 20, .6)]:
        sc.cloud(cx, cy, s, P["cloud"], P["cloud_shade"], op)
    sc.birds([(520, 92), (538, 84), (552, 95), (1080, 60), (1094, 66)], P["bird"], .9)

    # far country: the hills beyond Hobbiton, softened by haze
    far = sc.ridge(182, 9, [(1.3, 1), (3.1, .5), (7, .25)], P["far1"], seed=1.2)
    sc.add(f'<rect y="160" width="{W}" height="60" fill="{sc.lin("haze", [(0, P["haze"], 0), (1, P["haze"], .55)])}"/>')
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

    # the Party Field and its great tree, left
    right = sc.ridge(250, 9, [(1.2, 1), (2.9, .5)], P["hill_shade"], seed=6.7)
    party = sc.ridge(246, 10, [(1.1, 1), (2.6, .5)], sc.lin("partyg", [(0, P["hill_light"]), (.5, P["hill"])], x2=1, y2=0), seed=4.1, x1=1000)
    sc.tree(205, sc.y_at(party, 205) + 10, 62, P["leaf"], P["leaf_shade"], P["leaf_light"], P["trunk"], kind="big")
    # bunting on the Party Tree
    bx = [150, 175, 200, 225, 250, 275]
    for i, x in enumerate(bx):
        y = sc.y_at(party, 205) - 34 + abs(x - 212) * .12
        sc.add(f'<path d="M{f(x)},{f(y)} l5,9 l5,-9Z" fill="{["#e5683d", "#f4d443", "#3b6ea8", "#ffffff"][i % 4]}"/>')
    sc.add(f'<path d="M145,{f(sc.y_at(party, 205) - 36)} Q212,{f(sc.y_at(party, 205) - 24)} 285,{f(sc.y_at(party, 205) - 36)}" fill="none" stroke="#6b4a2e" stroke-width=".8"/>')

    # the Hill, with Bag End under its oak
    hill_pts = []
    for x in range(520, 1141, 6):
        t = (x - 830) / 310
        hill_pts.append((x, 158 + 150 * (t * t) ** 1.15 + 6 * math.sin(x / 37)))
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in hill_pts) + f" L1140,{H} L520,{H}Z"
    # lit from the sun on the right? no: the sun sits high right, so the left flank is in light haze and the right in full sun
    sc.add(f'<path d="{d}" fill="{sc.lin("hillg", [(0, P["hill"]), (.45, P["hill_light"]), (1, P["hill"])], x2=1, y2=0)}"/>')
    sc.add(f'<path d="{d}" fill="{sc.lin("hillv", [(0, P["hill_shade"], 0), (.55, P["hill_shade"], 0), (1, P["hill_shade"], .55)])}"/>')
    # hedges stepping round the Hill's shoulders
    for k, (a0, a1, dy) in enumerate([(560, 700, 30), (960, 1110, 34), (640, 760, 62), (900, 1040, 66)]):
        sc.hedge([(x, sc.y_at(hill_pts, x) + dy) for x in range(a0, a1, 7)], 3.2, P["hedge"], P["hedge_shade"])
    sc.tree(872, 172, 52, P["leaf"], P["leaf_shade"], P["leaf_light"], P["trunk"], kind="big")  # the oak over Bag End
    sc.add(f'<rect x="776" y="196" width="5" height="18" fill="#6b5a4a"/><rect x="774" y="194" width="9" height="4" fill="#4e4136"/>')
    sc.smoke(778, 188, 9, P["smoke"], .55, 1.2)
    # garden terraces and the path down
    sc.add(f'<path d="M760,276 Q790,268 830,270 Q880,272 905,282 L905,290 Q860,281 830,280 Q790,279 760,286Z" fill="{P["stone"]}" opacity=".8"/>')
    fence(sc, 742, 283, 790, 276, 6, P["wood"])
    fence(sc, 870, 276, 920, 285, 6, P["wood"])
    door(sc, 830, 248, 19, P["doors"][0], P["brass"], P["stone"], P["stone_shade"], P["wood"], flip=1)
    sc.add(f'<circle cx="788" cy="243" r="9" fill="{P["wood"]}"/><circle cx="788" cy="243" r="7" fill="#f6dc8a"/>')
    sc.flowers(262, 282, 60, P["flowers"], 1.4, 2.6, 740, 930)
    sc.add(f'<rect x="872" y="262" width="22" height="3" fill="{P["wood"]}"/><rect x="874" y="265" width="2" height="6" fill="{P["wood"]}"/><rect x="890" y="265" width="2" height="6" fill="{P["wood"]}"/>')  # bench

    # lower slopes with more hobbit-holes: Bagshot Row
    row = sc.ridge(258, 8, [(1.4, 1), (3.3, .4)], P["hill"], seed=5.3, x0=300, x1=820, taper=110)
    door(sc, 452, 285, 13, P["doors"][1], P["brass"], P["stone"], P["stone_shade"], P["wood"], flip=1)
    door(sc, 612, 288, 12, P["doors"][2], P["brass"], P["stone"], P["stone_shade"], P["wood"], flip=-1)
    sc.add(f'<rect x="478" y="{f(sc.y_at(row, 478) - 6)}" width="4" height="12" fill="#6b5a4a"/>')
    sc.smoke(480, sc.y_at(row, 478) - 10, 7, P["smoke"], .45, .9)
    # washing line between two posts
    sc.add(f'<path d="M520,282 V266 M570,284 V268 M520,267 Q545,272 570,269" stroke="{P["wood"]}" stroke-width="1.3" fill="none"/>')
    for i, c in enumerate(["#ffffff", "#c56cb2", "#3b6ea8", "#f4d443"]):
        sc.add(f'<rect x="{528 + i * 9}" y="{269 + (1.5 if i in (1, 2) else 0)}" width="6" height="{8 if i % 2 else 6}" fill="{c}"/>')
    sc.flowers(280, 300, 45, P["flowers"], 1.2, 2.2, 400, 700)
    for i in range(5):  # vegetable rows
        sc.add(f'<path d="M{660 + i * 2},{296 + i * 4} h46" stroke="{P["leaf"]}" stroke-width="2.5" stroke-dasharray="3 3"/>')

    # right slopes: another smial, orchards
    right = sc.ridge(256, 8, [(1.2, 1), (2.9, .5)], P["hill"], seed=6.7, x0=1010, x1=W + 120, taper=110)
    door(sc, 1190, 282, 13, P["doors"][3], P["brass"], P["stone"], P["stone_shade"], P["wood"], flip=-1)
    sc.add(f'<rect x="1222" y="{f(sc.y_at(right, 1222) - 4)}" width="4" height="11" fill="#6b5a4a"/>')
    sc.smoke(1224, sc.y_at(right, 1222) - 8, 7, P["smoke"], .45, 1.1)
    for x in range(1290, 1600, 46):  # orchard
        y = sc.y_at(right, x) + 26
        sc.tree(x, y, 15, P["leaf"], P["leaf_shade"], P["leaf_light"], P["trunk"])
        for k in range(4):
            sc.add(f'<circle cx="{f(x + sc.r(-9, 9))}" cy="{f(y - 16 + sc.r(-6, 6))}" r="1.8" fill="{"#d9483a" if not P["harvest"] else "#e08a2a"}"/>')

    # the Water, the bridge, and the mill
    wy = 318
    sc.add(f'<path d="M-20,{wy} Q300,{wy - 10} 620,{wy + 2} T1180,{wy - 4} T1620,{wy + 2} L1620,{wy + 22} Q1200,{wy + 16} 900,{wy + 24} T-20,{wy + 20}Z" fill="{P["water"]}"/>')
    for i in range(40):
        x = sc.r(0, W)
        sc.add(f'<path d="M{f(x)},{f(wy + 6 + sc.r(0, 10))} h{f(sc.r(8, 22))}" stroke="{P["water_light"]}" stroke-width="1.3" stroke-linecap="round" opacity=".8"/>')
    # stone bridge
    sc.add(f'<path d="M930,{wy - 6} Q990,{wy - 30} 1050,{wy - 6} L1050,{wy + 16} L1030,{wy + 16} Q990,{wy - 12} 950,{wy + 16} L930,{wy + 16}Z" fill="{P["stone"]}"/>')
    sc.add(f'<path d="M930,{wy - 6} Q990,{wy - 30} 1050,{wy - 6}" fill="none" stroke="{P["stone_shade"]}" stroke-width="3"/>')
    for i in range(7):
        sc.add(f'<path d="M{938 + i * 16},{wy - 6 - (14 if 2 <= i <= 4 else 8)} v5" stroke="{P["stone_shade"]}" stroke-width="1"/>')
    # mill with wheel
    mx, my = 1340, wy - 2
    sc.add(f'<rect x="{mx}" y="{my - 44}" width="66" height="44" fill="{P["stone"]}"/>'
           f'<path d="M{mx - 6},{my - 44} L{mx + 33},{my - 70} L{mx + 72},{my - 44}Z" fill="{P["roof"]}"/>'
           f'<rect x="{mx + 44}" y="{my - 66}" width="7" height="14" fill="{P["stone_shade"]}"/>'
           f'<rect x="{mx + 12}" y="{my - 30}" width="12" height="14" fill="#f6dc8a"/><rect x="{mx + 38}" y="{my - 24}" width="13" height="24" fill="{P["wood"]}"/>')
    cx, cy = mx - 8, my - 6
    sc.add(f'<circle cx="{cx}" cy="{cy}" r="20" fill="none" stroke="{P["wood"]}" stroke-width="3"/>' +
           "".join(f'<path d="M{cx},{cy} L{f(cx + 20 * math.cos(a))},{f(cy + 20 * math.sin(a))}" stroke="{P["wood"]}" stroke-width="2"/>' for a in [i * math.pi / 4 for i in range(8)]))
    sc.smoke(mx + 47, my - 72, 8, P["smoke"], .5, 1.3)

    # the lane from the bridge up to Bagshot Row and the Hill
    lane = f"M1000,{wy - 16} C960,300 900,300 870,292 C850,287 838,282 830,276"
    branch = "M900,298 C820,304 700,306 620,300 C560,296 500,296 455,299"
    for dpath, wdt in [(lane, 11), (branch, 8)]:
        sc.add(f'<path d="{dpath}" fill="none" stroke="{P["path_edge"]}" stroke-width="{wdt + 3}" stroke-linecap="round"/>'
               f'<path d="{dpath}" fill="none" stroke="{P["path"]}" stroke-width="{wdt}" stroke-linecap="round"/>')

    # foreground: long grass, wildflowers, a fence along the lane
    sc.ridge(345, 6, [(2.1, 1), (5, .4)], P["hill_shade"], seed=8.8)
    sc.tufts(338, 400, 900, P["grass"], 6, 18)
    sc.flowers(340, 398, 180, P["flowers"], 1.6, 3.2)
    fence(sc, 20, 372, 330, 352, 12, P["wood"])
    fence(sc, 1180, 350, 1560, 372, 14, P["wood"])
    return sc


def mirrored(sc):
    """Flip left to right: the page's cards cover the right of the banner, so the mill and bridge go left."""
    sc.parts = [f'<g transform="translate({W},0) scale(-1,1)">'] + sc.parts + ["</g>"]
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    mirrored(build(SUMMER)).save(f"{out}/shire.svg", "The Shire in summer")
    mirrored(build(HARVEST, seed=7)).save(f"{out}/home.svg", "The Shire at harvest")
