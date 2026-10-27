"""Minas Tirith: the White City at dawn.

Looking west from the Pelennor. The seven walled circles climb the knee of
Mount Mindolluin, cut through by the great prow of rock; the slender white
tower of the Citadel takes the first sun while the lower circles are still in
the blue of early morning. The farms of the Pelennor lie in front under a
lifting mist, the wall of the outer ring runs far off across the fields, and
on a peak to the north-west a beacon has been lit.
"""
import math
import sys
from scene_kit import Scene, W, H, f

P = dict(
    sky=[(0, "#b3c2dc"), (.42, "#dcdeea"), (.78, "#f1e2e0"), (1, "#f7e9d8")], glow="#fff1dc",
    cloud="#fbefeb", cloud_shade="#e3d4dc",
    far="#bcc2d6", far_shade="#aab1c8", far_snow="#f4eaee",
    rock="#c9c4cf", rock_light="#ddd5d9", rock_shade="#a4abc1", snow="#fcefe9", snow_shade="#dde1ee",
    foot="#aab4a5", foot2="#9ba795", foot_tree="#82927f",
    stone_low="#dde2ec", stone_high="#fbf2ea", stone_shade="#bcc4d7", stone_deep="#a3acc4",
    wall0="#c8ccd8", roof="#98a2b9", roof_warm="#b9a7a2", window="#5e6782", gate="#4c536b",
    tower="#fdf8f1", tower_tip="#ffd99c", sun_touch="#ffe4bc",
    fields=["#c6cca8", "#d2d1aa", "#bac49d", "#d8d3b2", "#b2bd9b", "#cbc59a"], hedge="#929f88", hedge_shade="#7f8c77",
    farm="#efe9df", farm_roof="#b48f78", lane="#e7e0cf", lane_edge="#d3cbb7",
    tree="#8a9a83", tree_shade="#6f8070", tree_light="#b4bf9f", trunk="#6e6258",
    mist="#ffffff", bird="#5b6276", fire="#ff9a3c", fire_core="#ffe08a",
    bg="#e1e4ea",
)

CX = 760  # the axis of the city: the Great Gate, the prow and the tower line up on it


def poly(pts, close=True):
    return "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + ("Z" if close else "")


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def blobs(sc, circles, fill, extra=""):
    """Many circles drawn as round-capped dots, grouped by size: far smaller than one element each."""
    if not circles:
        return
    by = {}
    for x, y, r in circles:
        by.setdefault(max(1, round(r * 2)), []).append(f"M{x:.0f},{y:.0f}h0")
    body = "".join(f'<path d="{"".join(v)}" stroke-width="{k}"/>' for k, v in sorted(by.items()))
    sc.add(f'<g stroke="{fill}" stroke-linecap="round"{extra}>{body}</g>')


def jag(sc, a, b, n, amp):
    """Points from a to b with a rough, rocky edge."""
    pts = [a]
    for i in range(1, n):
        t = i / n
        k = amp * (1 - abs(2 * t - 1)) ** .5
        pts.append((a[0] + (b[0] - a[0]) * t + sc.r(-k, k) * .5, a[1] + (b[1] - a[1]) * t + sc.r(-k, k)))
    pts.append(b)
    return pts


def mountain(sc, px, py, wl, wr, base, col, shade, snow, snow_shade, sd, n=7, amp=7):
    """A peak with a sunlit east face, a shaded flank, and a ragged cap of snow."""
    L = jag(sc, (px - wl, base), (px, py), n, amp)
    R = jag(sc, (px, py), (px + wr, base), n, amp)
    sc.add(f'<path d="{poly(L + R[1:])}" fill="{col}"/>')
    spur = jag(sc, (px, py), (px + wr * .18, base), n, amp * 1.2)
    sc.add(f'<path d="{poly(spur + R[::-1][:-1])}" fill="{shade}" opacity=".8"/>')
    cap = [p for p in L if p[1] < py + sd] + [p for p in R[1:] if p[1] < py + sd]
    if len(cap) >= 2:
        x0, x1 = cap[0][0], cap[-1][0]
        m = 5
        teeth = [(x1 + (x0 - x1) * i / m + sc.r(-3, 3), py + sd * (sc.r(.55, .8) if i % 2 else sc.r(.95, 1.25))) for i in range(1, m)]
        sc.add(f'<path d="{poly(cap + teeth)}" fill="{snow}"/>')
        sp = [p for p in spur if p[1] < py + sd * 1.1]
        sc.add(f'<path d="{poly([p for p in R if p[1] < py + sd] + sp[::-1])}" fill="{snow_shade}"/>')


def rects(rs):
    """Rectangles (x, y, w, h) as one path."""
    return "".join(f"M{f(x)},{f(y)}h{f(w)}v{f(h)}h{f(-w)}Z" for x, y, w, h in rs)


# ---- the seven circles ----
def tier(k):
    """Geometry of circle k (0 = the lowest): top of its wall at the front, half width, bow, wall height."""
    T = 262 - 25.5 * k
    hw = 232 - 25 * k
    return T, hw, 13 * hw / 232, (24 if k == 0 else 15)


def wall_top(k, x):
    T, hw, b, _ = tier(k)
    u = (x - CX) / hw
    return T + b * (1 - u * u)


def prow_half(y):
    """Half width of the rock prow at height y (it narrows a little toward its keel above the first circle)."""
    T6, T1 = tier(6)[0], tier(1)[0]
    t = min(1, max(0, (y - T6) / (T1 - T6)))
    return 18 - 5 * t


def fields(sc, rows, near=False):
    """Patchwork fields between row lines, each boundary leaning a little toward the city."""
    for (y0, y1) in rows:
        bounds = [(-40, 0)]
        while bounds[-1][0] < W + 40:
            x = bounds[-1][0] + sc.r(40, 80) * (1 + (y0 - 252) / 60)
            bounds.append((x, (x - CX) * (y1 - y0) / 160 + sc.r(-3, 3)))
        furrows = []
        for (xa, sa), (xb, sb) in zip(bounds, bounds[1:]):
            col = sc.rnd.choice(P["fields"])
            sc.add(f'<path d="M{f(xa)},{y0} L{f(xb)},{y0} L{f(xb + sb)},{y1} L{f(xa + sa)},{y1}Z" fill="{col}"/>')
            if sc.r(0, 1) < (.65 if near else .5):
                n = 6 if near and y1 - y0 > 26 else 4
                for k in range(1, n):
                    yy = y0 + (y1 - y0) * k / n
                    furrows.append(f"M{f(xa + sa * k / n + 2)},{f(yy)}H{f(xb + sb * k / n - 2)}")
        sc.add(f'<path d="{"".join(furrows)}" stroke="#000" stroke-opacity="{".08" if near else ".05"}" stroke-width="1"/>')


def hedges(sc, y, hs):
    segs, dots = [], []
    xx = -30
    while xx < W + 30:
        ln = sc.r(30, 120)
        segs.append(f"M{xx:.0f},{y}h{ln:.0f}")
        for _ in range(int(ln / 70)):
            dots.append((xx + sc.r(0, ln), y - hs, hs * sc.r(1.1, 1.6)))
        xx += ln + sc.r(10, 60)
    sc.add(f'<path d="{"".join(segs)}" stroke="{P["hedge"]}" stroke-width="{f(hs * 1.3)}" stroke-linecap="round"/>')
    blobs(sc, dots, P["hedge"])


def farm(sc, x, y, s, smokes=None):
    """A farmstead with its orchard: white walls, warm roof, a barn in the shade."""
    w, h = 14 * s, 7 * s
    sc.add(f'<rect x="{f(x - w / 2)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="{P["farm"]}"/>'
           f'<path d="M{f(x - w / 2 - 1.5 * s)},{f(y - h)} L{f(x - w / 2 + 3 * s)},{f(y - h - 5 * s)} L{f(x + w / 2 - 3 * s)},{f(y - h - 5 * s)} L{f(x + w / 2 + 1.5 * s)},{f(y - h)}Z" fill="{P["farm_roof"]}"/>'
           f'<rect x="{f(x + w / 2 - 4 * s)}" y="{f(y - h * .7)}" width="{f(2.5 * s)}" height="{f(h * .7)}" fill="{P["window"]}" opacity=".7"/>'
           f'<rect x="{f(x + w / 2)}" y="{f(y - h * .8)}" width="{f(6 * s)}" height="{f(h * .8)}" fill="{P["stone_shade"]}"/>')
    tr = [(x - w / 2 - 5 * s - k * 6.5 * s, y - 4 * s, 3.6 * s) for k in range(3)] + [(x - w / 2 - 8 * s - k * 6.5 * s, y - 1 * s, 3.4 * s) for k in range(2)]
    sc.add("".join(f'<rect x="{f(a - .6 * s)}" y="{f(b)}" width="{f(1.2 * s)}" height="{f(4 * s)}" fill="{P["trunk"]}"/>' for a, b, r in tr))
    blobs(sc, [(a + .8, b + .8, r) for a, b, r in tr], P["tree_shade"])
    blobs(sc, [(a, b, r * .85) for a, b, r in tr], P["tree"])
    if smokes is not None:
        smokes.append(f'<path d="M{f(x + 3 * s)},{f(y - 12 * s)} q-3,-6 1,-12 t0,-12" stroke="#f6f4f4" stroke-width="{f(2.2 * s)}" fill="none" stroke-linecap="round" opacity=".7"/>')


def build(P, seed=23):
    sc = Scene(seed)

    # ================= sky =================
    with sc.layer("sky", 0):
        sc.sky(sc.lin("sky", P["sky"]))
        # dawn comes from behind the viewer (the east): the western sky is pale, warming toward the horizon
        sc.add(f'<ellipse cx="800" cy="300" rx="1100" ry="190" fill="{sc.rad("glow", [(0, P["glow"], .8), (.6, P["glow"], .25), (1, P["glow"], 0)])}"/>')
        for cx, cy, s, op in [(240, 64, 30, .85), (1040, 38, 26, .7), (1250, 84, 34, .85), (1520, 56, 26, .7), (420, 112, 18, .6)]:
            with sc.fx("cloud"):
                sc.cloud(cx, cy, s, P["cloud"], P["cloud_shade"], op)
        with sc.fx("cloud"):
            for x, y, w in [(60, 120, 180), (900, 70, 150), (1120, 120, 220), (1380, 30, 120), (330, 40, 110)]:  # long dawn-lit streaks
                sc.add(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="{P["cloud"]}" opacity=".75"/>')

    # ================= far ranges and the beacons =================
    with sc.layer("far", .12):
        # far ranges of the White Mountains, their snow touched pink by the dawn behind us
        for px, py, wl, wr, sd in [(80, 112, 140, 120, 26), (290, 124, 120, 110, 20), (1040, 128, 120, 120, 18), (1200, 100, 150, 140, 30),
                                   (1400, 92, 130, 150, 32), (1575, 118, 120, 130, 22)]:
            mountain(sc, px, py, wl, wr, 252, P["far"], P["far_shade"], P["far_snow"], mix(P["far_snow"], P["far_shade"], .4), sd)
        sc.add(f'<rect x="-30" y="80" width="{W + 60}" height="180" fill="{sc.lin("haze1", [(0, P["glow"], 0), (1, P["glow"], .6)])}"/>')
        # the beacons: one burning on its peak, the next in the chain built and waiting
        bglow = sc.rad("bglow", [(0, P["fire"], .45), (.45, P["fire"], .12), (1, P["fire"], 0)])

        def flame(bx, by, s=1.0):
            return (f'<path d="M{f(bx - 3 * s)},{by - 1} Q{f(bx - 2 * s)},{f(by - 5 * s)} {bx},{f(by - 8 * s)} Q{f(bx + 1.5 * s)},{f(by - 4 * s)} {f(bx + 3 * s)},{by - 1}Z" fill="{P["fire"]}"/>'
                    f'<path d="M{f(bx - 1.4 * s)},{by - 1} Q{f(bx - .6 * s)},{f(by - 3 * s)} {bx},{f(by - 5 * s)} Q{f(bx + .7 * s)},{f(by - 3 * s)} {f(bx + 1.4 * s)},{by - 1}Z" fill="{P["fire_core"]}"/>')

        def cairn(bx, by):
            return f'<rect x="{bx - 4}" y="{by - 1}" width="8" height="3" fill="{P["far_shade"]}"/><path d="M{bx - 3},{by - 1}l1.5,-3h3l1.5,3Z" fill="{mix(P["far_shade"], "#6e6680", .4)}"/>'

        with sc.hot("mt-beacon", "Beacon", "One hilltop fire is burning; click to send the call along the chain.", "light"):
            bx, by = 1400, 92
            sc.add(f'<circle cx="{bx}" cy="{by - 6}" r="16" fill="#000" fill-opacity="0"/>')  # a larger target than the flame
            with sc.fx("smoke"):
                sc.smoke(bx + 1, by - 6, 5, "#d4ccd0", .35, 1.5)
            sc.add(cairn(bx, by))
            with sc.fx("glow"):
                sc.add(f'<circle cx="{bx}" cy="{by - 4}" r="14" fill="{bglow}"/>' + flame(bx, by, 1.3))
            for qx, qy in [(1200, 100), (1040, 128), (1575, 118)]:
                sc.add(f'<circle cx="{qx}" cy="{qy - 4}" r="10" fill="#000" fill-opacity="0"/>' + cairn(qx, qy))
                sc.add(f'<g class="on-lit"><circle cx="{qx}" cy="{qy - 3}" r="11" fill="{bglow}"/>{flame(qx, qy, .9)}'
                       f'<path d="M{qx + 1},{qy - 9} q3,-6 7,-9 t8,-8" stroke="#d4ccd0" stroke-width="2" fill="none" stroke-linecap="round" opacity=".35"/></g>')
        sc.ridge(178, 9, [(1.4, 1), (3.2, .5), (7, .2)], mix(P["far"], P["foot"], .35), seed=2.2)
        sc.add(f'<rect x="-30" y="160" width="{W + 60}" height="100" fill="{sc.lin("haze2", [(0, P["glow"], 0), (1, P["glow"], .5)])}"/>')

    # ================= Mount Mindolluin and the foothills =================
    with sc.layer("mountain", .28):
        mm = [(150, 250), (230, 196), (300, 150), (360, 112), (410, 84), (450, 62), (486, 42), (512, 28), (530, 24), (548, 30), (570, 44), (600, 58),
              (640, 70), (690, 88), (730, 104), (770, 116), (820, 128), (880, 146), (950, 170), (1030, 196), (1120, 222), (1200, 250)]
        sc.add(f'<path d="{poly(mm)}" fill="{sc.lin("mmg", [(0, P["rock_light"]), (.45, P["rock"]), (1, P["rock_shade"])], x2=1, y2=0)}"/>')
        # gullies and ridges on its face
        gul = [(530, 24, 470, 120, 430, 200), (548, 30, 600, 110, 640, 190), (512, 28, 520, 100, 560, 170), (690, 88, 700, 140, 740, 180), (450, 62, 400, 140, 330, 210)]
        sc.add(f'<path d="{"".join(f"M{a},{b} Q{c},{d} {e},{g}" for a, b, c, d, e, g in gul)}" stroke="{P["rock_shade"]}" stroke-width="2" fill="none" opacity=".55"/>')
        snow = [(450, 62), (486, 42), (512, 28), (530, 24), (548, 30), (570, 44), (600, 58), (612, 66), (596, 72), (584, 64), (566, 78), (550, 66), (534, 84),
                (522, 62), (506, 78), (492, 68), (474, 88), (464, 76)]
        sc.add(f'<path d="{poly(snow)}" fill="{P["snow"]}"/>')
        sc.add(f'<path d="M530,24 L548,30 L570,44 L600,58 L612,66 L596,72 L584,64 L566,78 L550,66 L540,50Z" fill="{P["snow_shade"]}" opacity=".8"/>')
        sc.add(f'<path d="{poly(mm)}" fill="{sc.lin("mmh", [(0, P["glow"], 0), (.5, P["glow"], 0), (1, P["glow"], .55)])}"/>')

        # foothills along the mountains' feet, wooded in the folds
        left_f = sc.ridge(222, 10, [(1.3, 1), (3.4, .5), (8, .2)], P["foot"], seed=4.4, x1=600, taper=150)
        right_f = sc.ridge(214, 12, [(1.2, 1), (3.1, .5), (7.5, .2)], P["foot"], seed=6.1, x0=900, taper=150)
        shade_d, leaf_d, light_d = [], [], []
        for pts, a, b in [(left_f, 10, 520), (right_f, 990, W - 10)]:
            for _ in range(16):  # copses in the folds of the hills
                cx = sc.r(a, b)
                cy = sc.y_at(pts, cx) + sc.r(6, 26)
                for _ in range(int(sc.r(8, 22))):
                    x, y, r = cx + sc.r(-22, 22), cy + sc.r(-5, 5), sc.r(2.2, 3.6)
                    shade_d.append((x + .8, y + .8, r))
                    leaf_d.append((x, y, r * .85))
                    if sc.r(0, 1) < .3:
                        light_d.append((x - r * .3, y - r * .35, r * .35))
        blobs(sc, shade_d, P["foot_tree"])
        blobs(sc, leaf_d, mix(P["foot_tree"], P["foot"], .45))
        blobs(sc, light_d, P["tree_light"], ' opacity=".6"')
        sc.ridge(244, 6, [(1.7, 1), (4.1, .4)], P["foot2"], seed=7.7, x0=-30, x1=560, taper=120)
        sc.ridge(240, 7, [(1.5, 1), (3.7, .4)], P["foot2"], seed=8.3, x0=960, x1=W + 30, taper=120)

    # ================= the city on its knee of rock, and the far Pelennor =================
    with sc.layer("city", .45):
        knee = [(470, 300), (500, 236), (540, 196), (590, 160), (640, 128), (690, 108), (740, 98), (790, 98), (840, 108), (890, 128), (940, 160), (990, 200), (1030, 240), (1060, 300)]
        sc.add(f'<path d="{poly(knee)}" fill="{sc.lin("kneeg", [(0, P["rock_light"]), (.5, P["rock"]), (1, P["rock_shade"])], x2=1, y2=0)}"/>')
        ledges = []
        for _ in range(26):
            x = sc.r(560, 1020)
            y = sc.r(120, 250)
            if Scene.y_at(knee, x) < y - 4:
                ledges.append(f"M{x:.0f},{y:.0f}l{sc.r(8, 22):.0f},{sc.r(1, 4):.0f}")
        sc.add(f'<path d="{"".join(ledges)}" stroke="{P["rock_shade"]}" stroke-width="1" opacity=".55"/>')
        scrub = []
        for _ in range(90):
            x = sc.r(480, 1050)
            y = sc.r(Scene.y_at(knee, x) + 6, 290)
            scrub.append((x, y, sc.r(1.2, 2.6)))
        blobs(sc, scrub, P["foot_tree"], ' opacity=".55"')

        # the far Pelennor: fields out to the wall of the outer ring
        plain_top = 252
        sc.add(f'<rect x="-30" y="{plain_top}" width="{W + 60}" height="{H - plain_top + 10}" fill="{sc.lin("plain", [(0, "#c9cfb2"), (1, P["bg"])])}"/>')
        for y0, y1 in [(254, 264), (264, 278), (278, 300)]:
            fields(sc, [(y0, y1)])
            hedges(sc, y1, 1.2 + (y0 - 252) / 30)
        sc.add(f'<rect x="-30" y="{plain_top}" width="{W + 60}" height="20" fill="{sc.lin("plainh", [(0, P["glow"], .7), (1, P["glow"], 0)])}"/>')

        # the Rammas Echor, far off across the fields, with its guard towers
        def rammas(pts, s):
            sc.add(f'<path d="{poly(pts, False)}" stroke="{P["stone_shade"]}" stroke-width="{f(3 * s)}" fill="none"/>'
                   f'<path d="{poly([(x, y - 1.2 * s) for x, y in pts], False)}" stroke="{P["stone_low"]}" stroke-width="{f(1.4 * s)}" fill="none"/>')
            for x, y in pts[1:-1:2]:
                sc.add(f'<rect x="{f(x - 2.5 * s)}" y="{f(y - 7 * s)}" width="{f(5 * s)}" height="{f(8 * s)}" fill="{P["stone_low"]}"/><rect x="{f(x + 1 * s)}" y="{f(y - 7 * s)}" width="{f(1.5 * s)}" height="{f(8 * s)}" fill="{P["stone_shade"]}"/>')
        rammas([(-30, 262), (60, 260), (140, 259), (220, 258), (300, 256), (380, 255), (450, 254)], 1)
        rammas([(1090, 254), (1180, 255), (1270, 256), (1360, 257), (1450, 258), (1540, 259), (1630, 260)], 1)
        # side lanes running off to the outer wall
        for dpath, wdt in [("M300,346 C330,320 360,300 380,282 S420,262 440,256", 3), ("M1060,336 C1100,300 1130,280 1160,262", 3)]:
            sc.add(f'<path d="{dpath}" fill="none" stroke="{P["lane_edge"]}" stroke-width="{wdt + 2}" stroke-linecap="round"/>'
                   f'<path d="{dpath}" fill="none" stroke="{P["lane"]}" stroke-width="{wdt}" stroke-linecap="round"/>')
        # farmsteads with orchards, a thread of morning smoke from some
        smokes = []
        for x, y, s, smoke in [(120, 276, .8, True), (330, 268, .7, False), (470, 290, .9, False), (1000, 286, .9, True),
                               (1150, 272, .8, False), (210, 262, .6, False), (400, 262, .6, True), (1040, 280, .7, False)]:
            farm(sc, x, y, s, smokes if smoke else None)
        for ox, oy, cols_, rows_, s in [(300, 282, 7, 3, 1.0), (40, 268, 6, 2, .8), (1010, 262, 5, 2, .8)]:
            tr = [(ox + c * 9 * s + r * 3 * s, oy + r * 6 * s, 2.6 * s) for r in range(rows_) for c in range(cols_)]
            blobs(sc, [(x + .7, y + .7, r) for x, y, r in tr], P["tree_shade"])
            blobs(sc, [(x, y, r * .85) for x, y, r in tr], P["tree"])
        for x0, y0, dx, dy, n, s in [(520, 286, 22, 2.6, 6, 4), (160, 262, 18, -.4, 7, 3)]:
            for i in range(n):
                x, y = x0 + i * dx, y0 + i * dy
                sc.add(f'<ellipse cx="{f(x)}" cy="{f(y - s * 1.7)}" rx="{f(s * .55)}" ry="{f(s * 1.8)}" fill="{P["tree"]}"/>'
                       f'<ellipse cx="{f(x + s * .2)}" cy="{f(y - s * 1.6)}" rx="{f(s * .3)}" ry="{f(s * 1.6)}" fill="{P["tree_shade"]}" opacity=".6"/>')
        with sc.fx("smoke"):
            sc.add("".join(smokes))

        # ---- the seven circles ----
        for k in range(6, -1, -1):
            T, hw, b, wh = tier(k)
            lit = mix(P["stone_low"], P["stone_high"], k / 6)
            shade = mix(P["stone_shade"], mix(P["stone_shade"], "#e8d6d6", .5), k / 6)
            # houses and halls on circle k, standing behind its parapet and in front of the wall above
            if k < 6:
                fronts, sides, roofs, wins, towers = [], [], [], [], []
                x = CX - hw * .93
                while x < CX + hw * .93:
                    w = sc.r(6, 13)
                    if k >= 2 and abs(x + w / 2 - CX) < prow_half(T) + 3:
                        x += w + 1
                        continue
                    base = wall_top(k, x + w / 2) + 3
                    h = sc.r(6, 14)
                    if sc.r(0, 1) < .1:
                        h += sc.r(8, 12)
                        towers.append((x, base - h, w * .7, h))
                        x += w * .7 + sc.r(1, 3)
                        continue
                    fronts.append((x, base - h, w, h))
                    if x > CX:
                        sides.append((x + w * .75, base - h, w * .25, h))
                    roofs.append((x - .5, base - h - 2.4, w + 1, 2.4))
                    for i in range(int(w // 4)):
                        if sc.r(0, 1) < .6:
                            wins.append((x + 1.5 + i * 4, base - h + 3, 1.2, 2))
                    x += w + sc.r(0, 2.5)
                sc.add(f'<path d="{rects(fronts)}" fill="{lit}"/><path d="{rects(sides)}" fill="{shade}"/>'
                       f'<path d="{rects(roofs)}" fill="{P["roof"]}"/><path d="{rects(wins)}" fill="{P["window"]}" opacity=".55"/>')
                for tx, ty, tw, th in towers:
                    sc.add(f'<rect x="{f(tx)}" y="{f(ty)}" width="{f(tw)}" height="{f(th)}" fill="{lit}"/>'
                           f'<rect x="{f(tx + tw * .62)}" y="{f(ty)}" width="{f(tw * .38)}" height="{f(th)}" fill="{shade}"/>'
                           f'<rect x="{f(tx - .8)}" y="{f(ty - 2)}" width="{f(tw + 1.6)}" height="2.4" fill="{lit}"/>'
                           f'<rect x="{f(tx + tw * .4)}" y="{f(ty + 3)}" width="1.2" height="2.4" fill="{P["window"]}" opacity=".6"/>')
            else:
                # the Citadel: the court, the hall, and the white tower taking the first sun
                sc.add(f'<rect x="{CX - 62}" y="{T - 14}" width="66" height="16" fill="{lit}"/><rect x="{CX - 8}" y="{T - 14}" width="12" height="16" fill="{shade}"/>'
                       f'<path d="M{CX - 64},{T - 14} L{CX - 58},{T - 20} L{CX},{T - 20} L{CX + 6},{T - 14}Z" fill="{P["roof"]}"/>')
                sc.add(f'<path d="{rects([(CX - 58 + i * 7, T - 10, 2, 6) for i in range(7)])}" fill="{P["window"]}" opacity=".5"/>')
                with sc.hot("mt-tower", "The White Tower", "The Citadel's tower takes the sunrise while the lower circles are still in shadow."):
                    tx, tw, ttop = CX + 22, 11, 46
                    sc.add(f'<rect x="{tx - tw / 2}" y="{ttop}" width="{tw}" height="{T - ttop}" fill="{sc.lin("towerg", [(0, P["tower_tip"]), (.22, P["tower"]), (1, lit)])}"/>'
                           f'<rect x="{tx + tw / 2 - 3.5}" y="{ttop}" width="3.5" height="{T - ttop}" fill="{shade}" opacity=".8"/>'
                           f'<rect x="{tx - tw / 2 - 2}" y="{ttop - 3}" width="{tw + 4}" height="3.5" fill="{P["tower_tip"]}"/>'
                           f'<path d="M{tx - tw / 2 - 1},{ttop - 3} L{tx},{ttop - 20} L{tx + tw / 2 + 1},{ttop - 3}Z" fill="{P["tower_tip"]}"/>'
                           f'<path d="M{tx},{ttop - 20} L{tx + tw / 2 + 1},{ttop - 3} L{tx + 1},{ttop - 3}Z" fill="#e9b97c" opacity=".7"/>')
                    sc.add(f'<path d="{rects([(tx - 1.5, ttop + 8 + i * 12, 2, 4) for i in range(4)])}" fill="{P["window"]}" opacity=".5"/>')
                    with sc.fx("glow"):
                        sc.add(f'<circle cx="{tx}" cy="{ttop - 8}" r="34" fill="{sc.rad("tglow", [(0, P["sun_touch"], .7), (1, P["sun_touch"], 0)])}"/>')
            # the wall of circle k, bowed toward us, lit on the left and turning into shadow on the right
            x0, x1 = CX - hw, CX + hw
            topl = [(x, wall_top(k, x)) for x in range(int(x0), int(x1) + 1, 6)]
            botl = [(x, y + wh) for x, y in topl][::-1]
            wcol = P["wall0"] if k == 0 else lit
            gid = f"w{k}"
            fill = sc.lin(gid, [(0, mix(wcol, shade, .45)), (.12, wcol), (.6, wcol), (.9, shade), (1, mix(shade, P["stone_deep"], .5))], x2=1, y2=0)
            sc.add(f'<path d="{poly(topl + botl)}" fill="{fill}"/>')
            sc.add(f'<path d="{poly(topl, False)}" stroke="{mix(wcol, "#ffffff", .5)}" stroke-width="1.2" fill="none"/>')
            sc.add(f'<path d="{poly([(x, y + 2.2) for x, y in topl], False)}" stroke="{P["stone_deep"]}" stroke-width=".8" fill="none" opacity=".45"/>')
            if k:
                # the gate of this circle, turning from side to side up the hill
                gx = CX + (-1 if k % 2 else 1) * hw * .55
                gy = wall_top(k, gx) + wh
                sc.add(f'<path d="M{f(gx - 2.5)},{f(gy)} V{f(gy - 5.5)} A2.5,2.5 0 0,1 {f(gx + 2.5)},{f(gy - 5.5)} V{f(gy)}Z" fill="{P["gate"]}"/>')
            else:
                for side in (-1, 1):  # round bastions where the outer wall turns back toward the mountain
                    ex = CX + side * (hw - 4)
                    ey = wall_top(0, ex)
                    sc.add(f'<rect x="{f(ex - 7)}" y="{f(ey - 6)}" width="14" height="{f(wh + 8)}" rx="2" fill="{P["wall0"] if side < 0 else P["stone_shade"]}"/>'
                           f'<rect x="{f(ex + 2)}" y="{f(ey - 6)}" width="5" height="{f(wh + 8)}" fill="{P["stone_deep"]}" opacity=".5"/>'
                           f'<rect x="{f(ex - 8)}" y="{f(ey - 8)}" width="16" height="3" fill="{mix(P["wall0"], "#ffffff", .4)}"/>')
                with sc.hot("mt-gate", "The Great Gate", "The way in from the fields; every road on the Pelennor runs to it.", "swing"):
                    for dx in (-22, 16):  # gate towers
                        sc.add(f'<rect x="{CX + dx}" y="{f(wall_top(0, CX + dx) - 8)}" width="7" height="{wh + 8}" fill="{P["wall0"]}"/>'
                               f'<rect x="{CX + dx + 4.6}" y="{f(wall_top(0, CX + dx) - 8)}" width="2.4" height="{wh + 8}" fill="{P["stone_shade"]}"/>')
                    gy = wall_top(0, CX) + wh
                    gw, gh = 14, 18
                    arch = f"M{CX - gw / 2},{f(gy)} V{f(gy - gh + gw / 2)} A{gw / 2},{gw / 2} 0 0,1 {CX + gw / 2},{f(gy - gh + gw / 2)} V{f(gy)}Z"
                    # the street inside, in morning light, behind the doors
                    sc.add(f'<path d="{arch}" fill="{mix(P["stone_high"], P["sun_touch"], .4)}"/>'
                           f'<path d="M{CX - gw / 2},{f(gy - 5)} h{gw} v5 h{-gw}Z" fill="{P["stone_shade"]}"/>')
                    sc.add(f'<g class="swing" data-origin="{CX - gw / 2} {f(gy - gh / 2)}"><path d="{arch}" fill="{P["gate"]}"/>'
                           f'<path d="M{CX},{f(gy - gh)}V{f(gy)}M{CX - gw / 2},{f(gy - 10)}h{gw}M{CX - gw / 2},{f(gy - 4)}h{gw}" stroke="#7a83a0" stroke-width=".8" fill="none"/></g>')
            # the prow of rock, cut through every circle but the first, its keel toward us
            if k == 2:
                T6 = tier(6)[0]
                top, keel = T6 - 4, tier(1)[0] - 2
                lit_face = [(CX - 19, top), (CX - 3, top), (CX - 1, keel + 4), (CX - 5, keel - 2), (CX - 9, keel - 12), (CX - 13, keel - 30), (CX - 15, top + 60)]
                dark_face = [(CX - 3, top), (CX + 17, top), (CX + 14, top + 50), (CX + 12, keel - 26), (CX + 6, keel - 10), (CX - 1, keel + 4)]
                sc.add(f'<path d="{poly(lit_face)}" fill="{mix(P["rock_light"], P["rock"], .3)}"/>')
                sc.add(f'<path d="{poly(dark_face)}" fill="{mix(P["rock_shade"], P["rock"], .2)}"/>')
                sc.add(f'<path d="M{CX - 3},{top} L{CX - 1},{keel + 4}" stroke="{P["stone_high"]}" stroke-width="1.2" opacity=".8"/>')
                st = "".join(f"M{CX - 15 + i * .2:.1f},{top + 14 + i * 17} l12,{1 + i * .3:.1f}" for i in range(7))
                sd = "".join(f"M{CX - 2},{top + 22 + i * 19} l{12 - i:.0f},-2" for i in range(6))
                sc.add(f'<path d="{st}" stroke="{P["rock_shade"]}" stroke-width=".8" opacity=".5" fill="none"/><path d="{sd}" stroke="{P["stone_deep"]}" stroke-width=".8" opacity=".6" fill="none"/>')
                sc.add(f'<rect x="{CX - 21}" y="{top - 5}" width="40" height="6" fill="{P["stone_high"]}"/>'
                       f'<rect x="{CX - 3}" y="{top - 5}" width="22" height="6" fill="{mix(P["stone_shade"], "#e8d6d6", .5)}"/>'
                       f'<path d="{rects([(CX - 20 + i * 4, top - 7, 2, 2) for i in range(10)])}" fill="{P["stone_high"]}"/>')

        # the knee of the mountain closes round the ends of the circles, so each wall runs back into the rock
        for side in (-1, 1):
            inner, outer = [], []
            for k in range(6, 0, -1):
                T, hw, b, wh = tier(k)
                ex = CX + side * hw
                inner += [(ex - side * sc.r(3, 7), T - 6), (ex - side * sc.r(4, 8), T + wh + 1)]
                outer.append((ex + side * sc.r(14, 22), T - 4))
            T0, hw0 = tier(0)[0], tier(0)[1]
            inner.append((CX + side * (hw0 - 6), T0 - 2))
            outer.append((CX + side * (hw0 + 10), T0 - 2))
            cheek = inner + outer[::-1]
            sc.add(f'<path d="{poly(cheek)}" fill="{mix(P["rock_light"], P["rock"], .4) if side < 0 else mix(P["rock_shade"], P["rock"], .35)}"/>')
            cr = "".join(f"M{f(x + side * sc.r(4, 10))},{f(y + 2)} l{f(side * sc.r(2, 6))},{f(sc.r(6, 14))}" for x, y in inner[::2])
            sc.add(f'<path d="{cr}" stroke="{P["rock_shade"] if side < 0 else P["stone_deep"]}" stroke-width=".9" fill="none" opacity=".6"/>')
            blobs(sc, [(x + side * sc.r(8, 16), y + sc.r(-2, 10), sc.r(1.4, 2.4)) for x, y in outer], P["foot_tree"], ' opacity=".7"')
        # light mist lifting off the far fields
        mistg = sc.rad("mistg", [(0, P["mist"], .6), (.6, P["mist"], .25), (1, P["mist"], 0)])
        for cx, cy, rx, ry in [(260, 268, 380, 12), (1250, 266, 420, 12)]:
            sc.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{mistg}"/>')
        with sc.fx("birds"):
            sc.birds([(980, 96), (996, 90), (1012, 98)], P["bird"], .7)
        with sc.fx("birds"):
            sc.birds([(300, 168), (314, 162)], P["bird"], .7)

    # ================= the near Pelennor =================
    with sc.layer("fields", .75):
        fields(sc, [(300, 324), (324, 354), (354, 410)], near=True)
        hedges(sc, 300, 2.7)
        # dry-stone field walls, each run of stones catching the light on top
        walls, tops, stones = [], [], []
        for y, s in [(324, 2.2), (354, 3)]:
            xx = -30
            while xx < W + 30:
                ln = sc.r(60, 200)
                if sc.r(0, 1) < .7:
                    walls.append(f"M{xx:.0f},{y}h{ln:.0f}")
                    tops.append(f"M{xx:.0f},{f(y - s * .45)}h{ln:.0f}")
                    for _ in range(int(ln / 9)):
                        stones.append((xx + sc.r(0, ln), y + sc.r(-.3, .4) * s, s * .45))
                xx += ln + sc.r(20, 70)
            sc.add(f'<path d="{"".join(walls)}" stroke="{P["stone_shade"]}" stroke-width="{f(s * 1.2)}" stroke-linecap="round"/>'
                   f'<path d="{"".join(tops)}" stroke="{P["stone_low"]}" stroke-width="{f(s * .5)}" stroke-linecap="round"/>')
            blobs(sc, stones, P["stone_deep"], ' opacity=".55"')
            walls, tops, stones = [], [], []
        # the causeway from the Great Gate, running straight out toward the river, and the lanes off it
        sc.add(f'<path d="M{CX - 7},300 Q{CX - 16},350 {CX - 58},410 L{CX + 74},410 Q{CX + 30},350 {CX + 7},300Z" fill="{P["lane"]}" stroke="{P["lane_edge"]}" stroke-width="2"/>'
               f'<path d="M{CX - 3},302 Q{CX - 6},350 {CX - 22},410 M{CX + 3},302 Q{CX + 12},350 {CX + 36},410" stroke="{P["lane_edge"]}" stroke-width="1.2" fill="none" opacity=".8"/>')
        for dpath, wdt in [(f"M{CX},304 C820,320 1000,330 1300,372 S1560,400 1700,410", 6), (f"M{CX},304 C690,318 520,326 300,346 S60,372 -40,380", 5)]:
            sc.add(f'<path d="{dpath}" fill="none" stroke="{P["lane_edge"]}" stroke-width="{wdt + 2.4}" stroke-linecap="round"/>'
                   f'<path d="{dpath}" fill="none" stroke="{P["lane"]}" stroke-width="{wdt}" stroke-linecap="round"/>')
        # haystacks in the stubble
        hay = []
        for x, y, s in [(200, 318, 3), (214, 320, 3.4), (560, 340, 4), (1180, 316, 3), (1196, 318, 3.6), (1420, 344, 4.4), (90, 346, 4.6), (880, 344, 4)]:
            hay.append(f'<path d="M{f(x - s)},{y} Q{f(x - s)},{f(y - s * 1.6)} {x},{f(y - s * 1.7)} Q{f(x + s)},{f(y - s * 1.6)} {f(x + s)},{y}Z" fill="#d8c48e"/>'
                       f'<path d="M{x},{f(y - s * 1.7)} Q{f(x + s)},{f(y - s * 1.6)} {f(x + s)},{y} L{f(x + s * .3)},{y}Z" fill="#bea878"/>')
        sc.add("".join(hay))
        smokes = []
        for x, y, s, smoke in [(240, 306, 1.1, True), (60, 330, 1.3, False), (420, 334, 1.3, True), (1290, 334, 1.3, False)]:
            farm(sc, x, y, s, smokes if smoke else None)
        with sc.fx("smoke"):
            sc.add("".join(smokes))
        for ox, oy, cols_, rows_, s in [(560, 304, 6, 2, 1.2), (1330, 316, 6, 2, 1.3)]:
            tr = [(ox + c * 9 * s + r * 3 * s, oy + r * 6 * s, 2.6 * s) for r in range(rows_) for c in range(cols_)]
            blobs(sc, [(x + .7, y + .7, r) for x, y, r in tr], P["tree_shade"])
            blobs(sc, [(x, y, r * .85) for x, y, r in tr], P["tree"])
        for x0, y0, dx, dy, n, s in [(1040, 300, 20, 4, 5, 4.5)]:
            for i in range(n):
                x, y = x0 + i * dx, y0 + i * dy
                sc.add(f'<ellipse cx="{f(x)}" cy="{f(y - s * 1.7)}" rx="{f(s * .55)}" ry="{f(s * 1.8)}" fill="{P["tree"]}"/>'
                       f'<ellipse cx="{f(x + s * .2)}" cy="{f(y - s * 1.6)}" rx="{f(s * .3)}" ry="{f(s * 1.6)}" fill="{P["tree_shade"]}" opacity=".6"/>')
        # a bigger farmstead beside the road, its yard fenced, the kitchen fire lit
        with sc.hot("mt-farm", "Pelennor farm", "A farm on the townlands below the walls, its first fire of the day going.", "smoke"):
            fx_, fy, s = 930, 316, 1.7
            sm = []
            farm(sc, fx_, fy, s, sm)
            fence = "".join(f"M{f(fx_ + 22 + i * 5)},{fy}v-4" for i in range(7))
            sc.add(f'<path d="{fence}M{f(fx_ + 21)},{fy - 2.6}h31" stroke="{P["trunk"]}" stroke-width="1" fill="none"/>'
                   f'<rect x="{f(fx_ + 30)}" y="{fy - 7}" width="9" height="5" fill="#d8c48e"/><path d="M{f(fx_ + 29)},{fy - 7} l5.5,-3 l5.5,3Z" fill="#bea878"/>')
            with sc.fx("smoke"):
                sc.add("".join(sm))
        # the last of the mist, thin enough to show the fields through it
        for cx, cy, rx, ry in [(500, 306, 520, 12), (1150, 310, 560, 14)]:
            sc.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{mistg}" opacity=".7"/>')
        sc.add(f'<rect x="-30" y="300" width="{W + 60}" height="110" fill="{sc.lin("fade", [(0, P["bg"], 0), (.6, P["bg"], .4), (1, P["bg"], .8)])}"/>')
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build(P).save(f"{out}/minastirith.svg", "Minas Tirith at dawn")
