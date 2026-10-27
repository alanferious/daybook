"""Mount Doom: Orodruin erupting over the plain of Gorgoroth.

The great cone on its heavy shoulder, fire spilling from the crater and running
down its flanks in glowing channels, the road climbing in zigzags to the dark
door of the Sammath Naur, the reek of the eruption spreading into a red-black
sky lit from beneath, and the cracked plain with fire in its fissures. Far off
to the east, the Dark Tower stands black against the glow.
"""
import math
import sys
from scene_kit import Scene, W, H, f

P = dict(
    sky=[(0, "#0a0504"), (.3, "#140806"), (.52, "#250d08"), (.66, "#36110a"), (.78, "#4e180b")],
    glow="#ff5a1f", lava="#ff8a3d", lava_hot="#ffd27a", lava_dark="#b8361a",
    cloud_top="#100806", cloud_mid="#1c0d09", cloud_lit="#6a2210", cloud_hot="#a8401a",
    far="#2a120c", far_lit="#7a2a12", haze="#8a2e14",
    cone="#160b08", cone_lit="#3a160c", cone_dark="#0e0705", shoulder="#1a0d09",
    road="#4a2c22", road_edge="#120806", door="#050302",
    tower="#0c0605", tower_lit="#4a1a0d",
    plain="#24130d", plain_far="#3a1a0f", crack="#0d0705", bg="#110a07",
    ash="#c9ad98", ember="#ff8a3d",
)


# ---------- helpers ----------
def jag(sc, ctrl, disp=.22, depth=4):
    """Midpoint displacement between hand-placed control points: a jagged line.
    Control point k ends up at index k * 2**depth of the result."""
    pts = list(ctrl)
    for _ in range(depth):
        out = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            ln = math.hypot(bx - ax, by - ay)
            out.append(((ax + bx) / 2 + sc.r(-.08, .08) * (bx - ax), (ay + by) / 2 + sc.r(-disp, disp) * ln))
            out.append((bx, by))
        pts = out
    return pts


def poly(pts, close_to=None):
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts)
    if close_to is not None:
        d += f" L{f(pts[-1][0])},{f(close_to)} L{f(pts[0][0])},{f(close_to)}"
    return d + "Z"


def range_(sc, gid, ctrl, fill, lit, base, light_x, disp=.22, depth=4, op=.8):
    """A jagged range closed to `base`, its faces toward light_x catching the glow."""
    pts = jag(sc, ctrl, disp, depth)
    sc.add(f'<path d="{poly(pts, base)}" fill="{fill}"/>')
    n = 2 ** depth
    grad = sc.lin(gid, [(0, lit, op), (.5, lit, op * .3), (1, lit, 0)])
    g = []
    for k in range(1, len(ctrl) - 1):
        px, py = ctrl[k]
        if py > ctrl[k - 1][1] or py > ctrl[k + 1][1]:
            continue
        j = k + 1 if light_x > px else k - 1
        seg = pts[min(k, j) * n: max(k, j) * n + 1]
        if j < k:
            seg = seg[::-1]
        vx, vy = seg[-1]
        apex = (px + (vx - px) * sc.r(.45, .7), min(base, max(py, vy) + abs(vx - px) * sc.r(.5, .9) + 8))
        g.append(f'<path d="{poly(seg + [apex])}" fill="{grad}"/>')
    rim = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        if (by - ay) * (1 if light_x > (ax + bx) / 2 else -1) > 0:
            rim.append(f"M{f(ax)},{f(ay)} L{f(bx)},{f(by)}")
    g.append(f'<path d="{" ".join(rim)}" stroke="{lit}" stroke-width="1" stroke-linecap="round" fill="none" opacity="{f(op * .8)}"/>')
    sc.add("".join(g))
    return pts


def billows(sc, blobs, grad, op=1.0):
    """Overlapping smoke billows sharing one dark-to-lit gradient."""
    g = [f'<g opacity="{op}" fill="{grad}">']
    for x, y, rx, ry in blobs:
        g.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rx)}" ry="{f(ry)}"/>')
    g.append("</g>")
    sc.add("".join(g))


def smoke_bank(sc, x, y, w, h, grad, op=1.0, puffs=11):
    blobs = []
    for i in range(puffs):
        t = i / (puffs - 1)
        rr = h * (.5 + .5 * math.sin(t * math.pi)) * sc.r(.7, 1.15)
        blobs.append((x - w / 2 + t * w + sc.r(-w * .04, w * .04), y - rr * .2 + sc.r(-h * .15, h * .15), rr * sc.r(1.5, 2.3), rr * .62))
    billows(sc, blobs, grad, op)


def ribbon(pts, widths):
    """A filled ribbon along pts, its half-width given per point: for tapering lava channels."""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(0, i - 1)]
        bx, by = pts[min(len(pts) - 1, i + 1)]
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = widths[i]
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return poly(left + right[::-1])


def wiggle(sc, ctrl, step=6, amp=2.5):
    """Resample a hand-placed course every `step` px with a little meander."""
    out = []
    for (ax, ay), (bx, by) in zip(ctrl, ctrl[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        for i in range(n):
            t = i / n
            out.append((ax + (bx - ax) * t + sc.r(-amp, amp), ay + (by - ay) * t + sc.r(-amp * .4, amp * .4)))
    out.append(ctrl[-1])
    return out


def lava(sc, ctrl, w0, w1, amp=2.5, glow_op=.22):
    """A channel of lava: wide dim glow, molten body, hot core; narrowing (or widening) from w0 to w1."""
    pts = wiggle(sc, ctrl, 6, amp)
    n = len(pts) - 1 or 1
    ws = [w0 + (w1 - w0) * i / n for i in range(n + 1)]
    sc.add(f'<path d="{ribbon(pts, [w * 2.4 + 1.5 for w in ws])}" fill="{P["glow"]}" opacity="{glow_op}"/>'
           f'<path d="{ribbon(pts, ws)}" fill="{P["lava_dark"]}"/>'
           f'<path d="{ribbon(pts, [w * .62 for w in ws])}" fill="{P["lava"]}"/>'
           f'<path d="{ribbon(pts, [w * .26 for w in ws])}" fill="{P["lava_hot"]}"/>')
    return pts


def fissure(sc, x, y, length, ang, w, hot=True):
    """A jagged crack in the plain; the hot ones show fire."""
    pts = [(x, y)]
    for i in range(int(length / 9)):
        ang += sc.r(-.8, .8)
        x += math.cos(ang) * 9
        y += math.sin(ang) * 9 * .3  # foreshortened on the ground plane
        pts.append((x, y))
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts)
    if hot:
        sc.add(f'<path d="{d}" fill="none" stroke="{P["glow"]}" stroke-width="{f(w * 3.4)}" stroke-linejoin="round" opacity=".1"/>'
               f'<path d="{d}" fill="none" stroke="{P["lava_dark"]}" stroke-width="{f(w * 1.2)}" stroke-linejoin="round" opacity=".9"/>'
               f'<path d="{d}" fill="none" stroke="{P["lava"]}" stroke-width="{f(w * .45)}" stroke-linejoin="round"/>')
    else:
        sc.add(f'<path d="{d}" fill="none" stroke="{P["crack"]}" stroke-width="{f(w)}" stroke-linejoin="round"/>')
    return pts


def dark_tower(sc, x, base, top):
    """The Dark Tower on the far horizon: a black mass of spires in tiers. Silhouette only."""
    c, lit = P["tower"], P["tower_lit"]
    h = base - top
    g = []
    # the broad foot and buttresses
    g.append(f'<path d="M{f(x - 70)},{f(base)} L{f(x - 52)},{f(base - h * .22)} L{f(x - 38)},{f(base - h * .26)} L{f(x - 30)},{f(base - h * .5)} L{f(x - 22)},{f(base - h * .55)} L{f(x - 16)},{f(base - h * .8)} L{f(x - 10)},{f(base - h * .86)} L{f(x - 7)},{f(top + 8)} L{f(x - 4)},{f(top + 16)} L{f(x - 2)},{f(top - 6)} L{f(x)},{f(top)} L{f(x + 2)},{f(top - 6)} L{f(x + 4)},{f(top + 16)} L{f(x + 7)},{f(top + 8)} L{f(x + 10)},{f(base - h * .86)} L{f(x + 16)},{f(base - h * .8)} L{f(x + 22)},{f(base - h * .55)} L{f(x + 30)},{f(base - h * .5)} L{f(x + 38)},{f(base - h * .26)} L{f(x + 52)},{f(base - h * .22)} L{f(x + 70)},{f(base)}Z" fill="{c}"/>')
    # lesser spires either side
    for dx, hh, ww in [(-34, .52, 6), (34, .5, 6), (-48, .32, 5), (48, .3, 5), (-22, .7, 4), (22, .68, 4)]:
        g.append(f'<path d="M{f(x + dx - ww)},{f(base - h * .2)} L{f(x + dx - ww * .6)},{f(base - h * hh)} L{f(x + dx)},{f(base - h * hh - 12)} L{f(x + dx + ww * .6)},{f(base - h * hh)} L{f(x + dx + ww)},{f(base - h * .2)}Z" fill="{c}"/>')
    # ledges with fangs
    for t, ww in [(.22, 56), (.5, 34), (.8, 20)]:
        yy = base - h * t
        g.append(f'<rect x="{f(x - ww)}" y="{f(yy - 2)}" width="{f(ww * 2)}" height="3" fill="{c}"/>')
        for k in (-1, 1):
            g.append(f'<path d="M{f(x + k * ww)},{f(yy - 2)} l{f(k * 6)},-7 l{f(-k * 2)},7Z" fill="{c}"/>')
    # the volcano's light on its western faces
    g.append(f'<path d="M{f(x - 7)},{f(top + 8)} L{f(x - 10)},{f(base - h * .86)} L{f(x - 16)},{f(base - h * .8)} L{f(x - 22)},{f(base - h * .55)} L{f(x - 30)},{f(base - h * .5)} L{f(x - 38)},{f(base - h * .26)} L{f(x - 52)},{f(base - h * .22)} L{f(x - 70)},{f(base)}" fill="none" stroke="{lit}" stroke-width="1.2" opacity=".8"/>')
    # a few dim lights
    for dx, t in [(-3, .62), (4, .4), (-12, .3), (14, .66)]:
        g.append(f'<rect x="{f(x + dx)}" y="{f(base - h * t)}" width="1.6" height="3" fill="{P["glow"]}" opacity=".55"/>')
    sc.add("".join(g))


def build(seed=23):
    sc = Scene(seed)
    sc.sky(sc.lin("sky", P["sky"]))
    # the glow of the fires: over the horizon, and the eruption's own light around the summit
    sc.add(f'<ellipse cx="760" cy="270" rx="1000" ry="170" fill="{sc.rad("hglow", [(0, P["glow"], .3), (.5, P["glow"], .09), (1, P["glow"], 0)])}"/>')
    sc.add(f'<ellipse cx="728" cy="90" rx="380" ry="160" fill="{sc.rad("cglow", [(0, P["lava"], .5), (.3, P["glow"], .2), (1, P["glow"], 0)])}"/>')

    # the reek over Mordor: banks of smoke lit red from beneath
    hi = sc.lin("cl_hi", [(0, P["cloud_top"]), (.55, P["cloud_mid"]), (.85, "#33140b"), (1, P["cloud_lit"])])
    lo = sc.lin("cl_lo", [(0, P["cloud_mid"]), (.5, "#24100a"), (.82, P["cloud_lit"]), (1, P["cloud_hot"])])
    for x, y, w, h, op in [(130, 10, 640, 34, 1), (1400, 12, 640, 36, 1), (300, 52, 420, 22, .9), (1180, 58, 460, 24, .9), (1530, 64, 260, 18, .85), (60, 74, 260, 16, .85)]:
        smoke_bank(sc, x, y, w, h, hi, op, 13)
    for x, y, w, h, op in [(420, 112, 300, 13, .8), (1020, 110, 340, 15, .85), (1300, 134, 260, 11, .7), (160, 128, 260, 12, .7)]:
        smoke_bank(sc, x, y, w, h, lo, op, 9)

    # the eruption column: billows rising from the crater, leaning east and spreading into the ceiling
    plume = sc.lin("plume", [(0, "#0f0705"), (.55, "#1c0b07"), (.86, "#4e1a0c"), (1, "#7a2c12")])
    plume_hot = sc.lin("plumeh", [(0, "#1a0a06"), (.5, "#3a150b"), (.8, "#9a3a16"), (1, "#d8642a")])
    blobs = []
    for i in range(36):
        t = i / 35
        rx = 14 + 84 * t
        cx = 730 + 30 * t + 170 * t ** 2.2 + sc.r(-.4, .4) * rx
        cy = 80 - 100 * t + sc.r(-4, 4)
        blobs.append((cx, cy, rx * sc.r(.85, 1.1), rx * sc.r(.5, .62)))
    for i in range(16):  # the top of the column spreading east into the reek
        t = i / 15
        blobs.append((860 + 520 * t + sc.r(-20, 20), 4 + 18 * t + sc.r(-6, 6), 70 - 30 * t + sc.r(-8, 8), 26 - 8 * t))
    billows(sc, blobs[::-1], plume, .97)
    billows(sc, [(730 + (-1) ** i * sc.r(4, 12), 78 - i * 9, 12 + i * 3.5, 7 + i * 2) for i in range(4)][::-1], plume_hot, .8)

    # the distant ranges: the Mountains of Shadow far west, the Ash Mountains to the north and east
    range_(sc, "fw", [(-20, 232), (40, 214), (100, 230), (160, 206), (220, 228), (290, 210), (350, 236), (420, 244), (480, 262)], P["far"], P["far_lit"], 320, 728, .3, 4, op=.7)
    dark_tower(sc, 1400, 264, 96)  # stands behind the eastern ridge, its foot hidden
    range_(sc, "fe", [(1000, 262), (1080, 240), (1150, 226), (1200, 236), (1260, 214), (1320, 232), (1360, 240), (1400, 236), (1440, 242), (1480, 232), (1530, 216), (1580, 228), (1620, 220)], P["far"], P["far_lit"], 320, 728, .3, 4, op=.6)
    sc.add(f'<rect y="190" width="{W}" height="90" fill="{sc.lin("haze", [(0, P["haze"], 0), (.6, P["haze"], .1), (1, P["haze"], .2)])}"/>')

    # Orodruin: the heavy shoulder and the cone on top of it
    ctrl = [(290, 300), (370, 286), (440, 266), (510, 242), (570, 220), (612, 206), (648, 196), (670, 190), (684, 164), (696, 128), (706, 98), (712, 88),
            (724, 92), (736, 90), (748, 86), (756, 98), (766, 130), (778, 166), (790, 188), (812, 194), (856, 202), (910, 216), (976, 236), (1046, 260), (1116, 282), (1196, 300)]
    vol = jag(sc, ctrl, .08, 3)
    vd = poly(vol, H + 10)
    sc.defs.append(f'<clipPath id="volc"><path d="{vd}"/></clipPath>')
    sc.add(f'<path d="{vd}" fill="{sc.lin("coneg", [(0, P["cone_dark"]), (.42, P["cone"]), (.62, P["shoulder"]), (1, P["cone_dark"])], x2=1, y2=0)}"/>')
    g = ['<g clip-path="url(#volc)">']
    # the crater's light washing down the upper cone
    g.append(f'<ellipse cx="728" cy="86" rx="150" ry="120" fill="{sc.rad("crlight", [(0, P["glow"], .45), (.5, P["glow"], .12), (1, P["glow"], 0)])}"/>')
    # the shoulder's edge, where the cone stands on its base
    g.append(f'<path d="M590,214 Q640,198 672,194 Q730,204 788,192 Q850,200 900,218" fill="none" stroke="{P["cone_lit"]}" stroke-width="2" opacity=".6"/>')
    # gullies and old flows, cooled black
    for _ in range(26):
        x = sc.r(470, 1000)
        y0 = 200 + abs(x - 728) * .2 + sc.r(-10, 20)
        g.append(f'<path d="M{f(x)},{f(y0)} q{f((x - 728) * .06)},{f(sc.r(16, 30))} {f((x - 728) * .14)},{f(sc.r(40, 70))}" stroke="{P["cone_dark"]}" stroke-width="{f(sc.r(1.2, 3))}" fill="none" stroke-linecap="round"/>')
    for _ in range(14):  # on the cone
        x = sc.r(692, 772)
        g.append(f'<path d="M{f(x)},{f(102 + abs(x - 728) * .4)} l{f((x - 728) * .25)},{f(sc.r(24, 50))}" stroke="{P["cone_dark"]}" stroke-width="1.4" fill="none" stroke-linecap="round"/>')
    g.append("</g>")
    sc.add("".join(g))
    # rim light from the lava along the summit edges
    rim = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in vol if 660 <= a <= 800)
    sc.add(f'<path d="{rim}" fill="none" stroke="{P["glow"]}" stroke-width="1.4" opacity=".3"/>')

    # the road: up from the plain in zigzags to the door of the Sammath Naur
    road = [(560, 300), (640, 268), (786, 236), (712, 216), (776, 198), (722, 184), (742, 168), (722, 156), (731, 140)]
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in road)
    sc.add(f'<path d="{d}" fill="none" stroke="{P["road_edge"]}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
           f'<path d="{d}" fill="none" stroke="{P["road"]}" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round" opacity=".85"/>')
    # the door: a black opening in the cone, under a lip of rock
    sc.add(f'<path d="M724,140 L725,129 Q731,123 737,129 L738,140Z" fill="{P["door"]}"/>'
           f'<path d="M721,129 Q731,117 741,129 L739,127 Q731,120 723,127Z" fill="{P["cone_lit"]}"/>'
           f'<rect x="722" y="139.5" width="18" height="1.6" fill="{P["road"]}"/>')

    # lava: spilling from the crater and running down in channels
    lava(sc, [(716, 93), (713, 112), (709, 140), (702, 168), (690, 192), (660, 204), (632, 210), (598, 222), (562, 240), (528, 258), (496, 276), (468, 298)], 1.3, 3.4)
    lava(sc, [(632, 210), (606, 230), (580, 252), (558, 278), (540, 300)], 1.4, 2.4, 2)
    lava(sc, [(744, 91), (748, 110), (752, 138), (758, 166), (770, 190), (800, 202), (830, 206), (876, 216), (926, 234), (972, 254), (1012, 278), (1044, 300)], 1.3, 3.6)
    lava(sc, [(876, 216), (896, 240), (908, 266), (916, 296)], 1.3, 2.4, 2)
    lava(sc, [(730, 93), (728, 104), (726, 114)], 1.1, .4, .8, .16)
    for x0, y0 in [(650, 200), (840, 204), (560, 238), (950, 244)]:  # short spills and dribbles
        lava(sc, [(x0, y0), (x0 + sc.r(-8, 8), y0 + 14), (x0 + sc.r(-14, 14), y0 + 28)], .9, .3, 1.5, .14)
    # the crater: a molten mouth and the fountain thrown out of it
    sc.add(f'<ellipse cx="730" cy="91" rx="20" ry="4" fill="{P["lava"]}"/><ellipse cx="730" cy="90" rx="12" ry="2.4" fill="{P["lava_hot"]}"/>')
    sc.add(f'<ellipse cx="729" cy="80" rx="70" ry="30" fill="{sc.rad("fount", [(0, P["lava_hot"], .5), (.4, P["lava"], .2), (1, P["glow"], 0)])}"/>')
    g = []
    for _ in range(46):
        vx = sc.r(-1.6, 1.6)
        vy = sc.r(2.2, 4.4)
        t = sc.r(4, 18)
        x = 729 + vx * t * 2.4
        y = 88 - vy * t + .16 * t * t
        if y > 94:
            continue
        g.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(sc.r(.6, 1.7))}" fill="{sc.rnd.choice([P["lava_hot"], P["lava"], P["lava"], P["glow"]])}" opacity="{f(sc.r(.6, 1))}"/>')
    sc.add("".join(g))

    # Gorgoroth: the cracked plain
    sc.ridge(282, 3, [(1.4, 1), (3.9, .5)], sc.lin("plaing", [(0, P["plain_far"]), (.3, P["plain"]), (1, P["bg"])]), seed=2.2, x0=-20, x1=W + 20)
    sc.add(f'<ellipse cx="728" cy="292" rx="520" ry="26" fill="{sc.rad("footglow", [(0, P["glow"], .18), (1, P["glow"], 0)])}"/>')
    # dark cracks everywhere, fire in some
    for _ in range(46):
        y = sc.r(286, 370)
        fissure(sc, sc.r(-20, W), y, sc.r(30, 110), sc.r(-.4, .4) + (math.pi if sc.r(0, 1) < .5 else 0), sc.r(.8, 1.6), hot=False)
    for x, y, ln, w in [(468, 300, 110, 1.4), (1044, 302, 120, 1.5), (540, 302, 70, 1.1), (220, 300, 120, 1.1), (650, 322, 110, 1.3), (1250, 300, 90, 1),
                        (360, 334, 130, 1.4), (830, 330, 150, 1.6), (1460, 314, 90, 1)]:
        fissure(sc, x, y, ln, sc.r(-.3, .3) + (math.pi if x > 728 else 0) * (sc.r(0, 1) < .5), w)
    # pools of lava where the flows reach the plain
    for x, y, rx in [(468, 300, 14), (1044, 302, 16), (916, 298, 9), (540, 302, 8)]:
        sc.add(f'<ellipse cx="{x}" cy="{y}" rx="{f(rx * 1.4)}" ry="{f(rx * .3)}" fill="{P["glow"]}" opacity=".12"/>'
               f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{f(rx * .18)}" fill="{P["lava_dark"]}"/><ellipse cx="{f(x - rx * .1)}" cy="{f(y - .3)}" rx="{f(rx * .55)}" ry="{f(rx * .08)}" fill="{P["lava"]}"/>')
    # rocks and spatter cones
    for _ in range(110):
        x = sc.r(-10, W + 10)
        y = sc.r(286, 372)
        s = sc.r(1.4, 3.6) * (1 + (y - 286) / 70)
        sc.add(f'<path d="M{f(x - s)},{f(y)} L{f(x - s * .3)},{f(y - s)} L{f(x + s * .6)},{f(y - s * .6)} L{f(x + s)},{f(y)}Z" fill="{sc.rnd.choice(["#0f0806", "#1a0d09", "#2a140d"])}"/>')
    for x, y, w, h in [(220, 296, 26, 10), (1180, 294, 30, 12), (1500, 300, 34, 12), (90, 330, 36, 12)]:
        sc.add(f'<path d="M{x - w},{y} L{f(x - w * .3)},{y - h} L{f(x + w * .3)},{y - h} L{x + w},{y}Z" fill="#1c0e09"/><path d="M{f(x - w * .3)},{y - h} L{f(x + w * .3)},{y - h}" stroke="{P["glow"]}" stroke-width="1.2" opacity=".6"/>')
        sc.smoke(x, y - h - 2, 9, "#4a2a20", .35, .8)
    # fumes from the hot fissures
    for x, y in [(520, 300), (1060, 292), (300, 304)]:
        sc.smoke(x, y, 8, "#5a3226", .22, 1)

    # foreground fading to the page
    sc.ridge(352, 5, [(1.7, 1), (4.1, .4)], sc.lin("fg", [(0, "#1a0f0b"), (1, P["bg"])]), seed=7.3)
    for x, y, ln in [(140, 372, 120), (900, 376, 130)]:
        fissure(sc, x, y, ln, sc.r(-.2, .2), 1.2)

    # ash drifting down, embers swept up from the crater
    g = [f'<g fill="{P["ash"]}">']
    for _ in range(420):
        g.append(f'<circle cx="{f(sc.r(0, W))}" cy="{f(sc.r(0, 330))}" r="{f(sc.r(.5, 1.3))}" opacity="{f(sc.r(.1, .38))}"/>')
    g.append("</g>")
    sc.add("".join(g))
    g = [f'<g fill="{P["ember"]}">']
    for _ in range(110):
        t = sc.r(0, 1)
        x = 729 + sc.r(-60, 60) + 500 * t * t
        y = 90 - 80 * t + sc.r(-30, 60)
        if 712 < x < 750 and 112 < y < 146:  # keep the door dark
            continue
        g.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(sc.r(.5, 1.3))}" opacity="{f(sc.r(.35, .9))}"/>')
    g.append("</g>")
    sc.add("".join(g))
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build().save(f"{out}/mountdoom.svg", "Mount Doom")
