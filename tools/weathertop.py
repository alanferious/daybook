"""Weathertop by night: Amon Sûl at the southern end of the Weather Hills.

A tall, steep, lonely hill crowned with the broken ring of an old watchtower's
walls; the long ridge of the Weather Hills running away north; a moon behind
torn storm cloud; cold blue light, scrub and boulders; and, in the dell under
the hill's western side, the small red glow of a campfire.
"""
import math
import re
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
    n = 44
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




def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def pth(pts, close=True):
    return "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + ("Z" if close else "")


# ---------- Amon Sûl: a craggy hill built of stacked, broken terraces ----------
# each tier: left/right ends of its lip, lip height at each end, how far the lip bows toward us,
# the height of the rock face under the lip, and how far that face splays out at its foot
TIERS = [
    dict(a=718, b=868, tL=104, tR=100, sag=8, h=28, d=8, ph=(.3, 2.1, 4.0), gaps=[]),
    dict(a=668, b=930, tL=139, tR=133, sag=12, h=34, d=12, ph=(1.7, .4, 2.6), gaps=[(-.86, -.7), (.52, .6)]),
    dict(a=610, b=984, tL=181, tR=175, sag=13, h=28, d=16, ph=(2.9, 1.2, .8), gaps=[(-.2, -.06), (.8, .9)]),
    dict(a=556, b=1046, tL=215, tR=210, sag=11, h=20, d=20, ph=(.9, 3.3, 1.9), gaps=[(-.78, -.64), (.3, .4)]),
]


def wob(T, u, amp, k):
    p = T["ph"]
    return amp * (math.sin(u * k + p[0]) + .5 * math.sin(u * k * 2.3 + p[1]) + .25 * math.sin(u * k * 5.1 + p[2]))


def lip(T, u):
    """The front edge of a tier's ledge at u in [-1, 1]: (x, y)."""
    c, half = (T["a"] + T["b"]) / 2, (T["b"] - T["a"]) / 2
    return c + u * half, T["tL"] + (T["tR"] - T["tL"]) * (u + 1) / 2 + T["sag"] * math.sqrt(max(0.0, 1 - u * u)) + wob(T, u, 2.2, 4)


def foot(T, u):
    """The foot of the rock face under the lip: the face is taller in places, lower in others."""
    c, half = (T["a"] + T["b"]) / 2, (T["b"] - T["a"]) / 2
    return c + u * (half + T["d"]), lip(T, u)[1] + T["h"] * (1 + .22 * math.sin(u * 5 + T["ph"][2]))


def face_col(u, k):
    """Rock colour across the hill: the west (left) side in shadow, the east catching the moon."""
    t = (u + 1) / 2
    base = mix("#141827", "#4a5579", t ** 1.6)
    return mix(base, "#0f121d" if k < 0 else "#6a76a0", abs(k))


def tier(sc, T, upper, i):
    rnd = sc.r
    # the ledge top (turf), from the corner of the tier above out to this lip and back
    N = 36
    lipp = [lip(T, -1 + 2 * j / N) for j in range(N + 1)]
    if upper is None:  # the crown: a low dome
        c = (T["a"] + T["b"]) / 2
        top = [(c + (T["b"] - T["a"]) / 2 * math.cos(math.pi * j / 12),
                min(lip(T, -1)[1], lip(T, 1)[1]) - 9 * math.sin(math.pi * j / 12) + rnd(-1, 1)) for j in range(13)]
        turf = top + lipp
    else:
        ulx, uly = foot(upper, -1)
        urx, ury = foot(upper, 1)
        lx, ly = lipp[0]
        rx, ry = lipp[-1]
        left = [(ulx + (lx - ulx) * k / 4 + rnd(-1, 1), uly + (ly - uly) * k / 4 + rnd(-1.5, .5)) for k in range(5)]
        right = [(rx + (urx - rx) * k / 4 + rnd(-1, 1), ry + (ury - ry) * k / 4 + rnd(-1.5, .5)) for k in range(5)]
        turf = left + lipp[1:-1] + right
    sc.add(f'<path d="{pth(turf)}" fill="url(#turf)"/>')
    # a moonlit rim along the turf's skyline on the east side
    rim = [p for p in (turf if upper is None else right) if p[0] > 800]
    if len(rim) > 1:
        sc.add(f'<path d="{pth(rim, False)}" fill="none" stroke="#7d89b3" stroke-width="1.2" opacity=".6"/>')
    # the rock face: jointed columns between lip and foot, jagged at both ends
    cols = []
    lits = []
    u = -1.0
    while u < 1:
        du = rnd(5, 12) / ((T["b"] - T["a"]) / 2)
        u1 = min(1.0, u + du)
        (x0, y0), (x1, y1) = lip(T, u), lip(T, u1)
        (bx0, by0), (bx1, by1) = foot(T, u), foot(T, u1)
        j0, j1 = rnd(-2.5, 1), rnd(-2.5, 1)
        b0, b1 = rnd(-2, 4), rnd(-2, 4)
        if any(g0 < (u + u1) / 2 < g1 for g0, g1 in T["gaps"]):
            u = u1
            continue
        quad = [(x0, y0 + j0), (x1, y1 + j1), (bx1, by1 + b1), (bx0, by0 + b0)]
        cols.append((quad, face_col((u + u1) / 2, rnd(-.35, .3))))
        if (u + u1) / 2 > -.2 and rnd(0, 1) < .8:  # the edge of each column turned to the moon
            w = (x1 - x0) * rnd(.18, .3)
            lits.append(pth([(x1 - w, y1 + j1), (x1, y1 + j1), (bx1, by1 + b1), (bx1 - w, by1 + b1)]))
        u = u1
    sc.add("".join(f'<path d="{pth(q)}" fill="{c}"/>' for q, c in cols))
    sc.add(f'<path d="{"".join(lits)}" fill="#8792ba" opacity=".38"/>')
    # grassy breaks in the face where the slope runs down unbroken (a fan of scree at the bottom)
    for g0, g1 in T["gaps"]:
        top = [lip(T, g0 + (g1 - g0) * k / 4) for k in range(5)]
        bot = [foot(T, g1 + .05 - (g1 - g0 + .1) * k / 4) for k in range(5)]
        sc.add(f'<path d="{pth(top + [(bot[0][0], bot[0][1] + 2)] + bot[1:-1] + [(bot[-1][0], bot[-1][1] + 2)])}" fill="url(#turf)"/>')
        for k in range(3):
            uu = sc.r(g0, g1)
            (x0, y0), (x1, y1) = lip(T, uu), foot(T, uu)
            scrub(sc, x0 + (x1 - x0) * .5, y0 + (y1 - y0) * sc.r(.3, .8), sc.r(2.4, 3.6), "#151a2a")
    # cracks, and a few deep clefts
    cr = ""
    for _ in range(int((T["b"] - T["a"]) / 26)):
        uu = rnd(-.95, .95)
        (x0, y0), (x1, y1) = lip(T, uu), foot(T, uu)
        t = rnd(.0, .3)
        cr += f"M{f(x0 + (x1 - x0) * t)},{f(y0 + (y1 - y0) * t)}L{f(x0 + (x1 - x0) * .6 + rnd(-3, 3))},{f(y0 + (y1 - y0) * .6)}L{f(x1 + rnd(-2, 2))},{f(y1)}"
    sc.add(f'<path d="{cr}" fill="none" stroke="#0b0d16" stroke-width="1.3" opacity=".7"/>')
    # the lip itself: a hard edge, bright on the moon side
    sc.add(f'<path d="{pth([p for p in lipp if p[0] > 770], False)}" fill="none" stroke="#8e99c0" stroke-width="1" opacity=".42"/>')
    # the face seen edge-on at each end of the tier, the hill's stepped skyline
    for side in (-1, 1):
        (lx, ly), (fx_, fy_) = lip(T, side), foot(T, side)
        mid = (lx + (fx_ - lx) * .5 + side * rnd(1, 3), ly + (fy_ - ly) * .45)
        sc.add(f'<path d="{pth([(lx, ly - 1), mid, (fx_, fy_ + 1), (fx_ - side * 6, fy_ + 1), (lx - side * 8, ly + 2)])}" fill="{face_col(side, -.1 if side < 0 else .25)}"/>')


def buttress(sc, x, ytop, ybot, w):
    """A crag standing proud of the terraces, breaking a ledge: a front face and a moonlit east face."""
    rnd = sc.r
    u = max(-1, min(1, (x - 790) / 250))
    top = [(x - w / 2, ytop + rnd(4, 9)), (x - w * .2, ytop + rnd(0, 3)), (x + w * .1, ytop), (x + w * .35, ytop + rnd(3, 6)), (x + w / 2, ytop + rnd(8, 12))]
    body = [(x - w / 2 - 3, ybot)] + top + [(x + w / 2 + 3, ybot)]
    sc.add(f'<path d="{pth(body)}" fill="{face_col(u, -.1)}"/>')
    sc.add(f'<path d="{pth([top[2], top[3], top[4], (x + w / 2 + 3, ybot), (x + w * .15, ybot)])}" fill="{face_col(u, .45)}" opacity=".9"/>')
    sc.add(f'<path d="M{f(x - w * .15)},{f(ytop + 8)} L{f(x - w * .1)},{f(ybot)} M{f(x - w * .35)},{f(ytop + 14)} L{f(x - w * .38)},{f(ybot)}" stroke="#0b0d16" stroke-width="1.2" opacity=".7"/>')
    sc.add(f'<path d="{pth(top[1:4], False)}" fill="none" stroke="#97a2c8" stroke-width="1" opacity="{f(.25 + .4 * (u + 1) / 2)}"/>')


def block(sc, x, yb, w, h, face, lit, dark, jag=True, courses=True):
    """An upright block of masonry: a front face, its moonlit right side, a broken top."""
    rnd = sc.r
    top = [(x - w / 2, yb - h + (rnd(0, h * .12) if jag else 0)), (x - w * .1, yb - h - (rnd(0, 2) if jag else 0)),
           (x + w * .2, yb - h + (rnd(0, 3) if jag else 0)), (x + w / 2, yb - h + (rnd(0, h * .2) if jag else 0))]
    g = [f'<path d="{pth([(x - w / 2, yb)] + top + [(x + w / 2, yb)])}" fill="{face}"/>',
         f'<path d="{pth([(x + w * .22, top[2][1] + 1), top[3], (x + w / 2, yb), (x + w * .22, yb)])}" fill="{lit}" opacity=".85"/>',
         f'<path d="{pth([(x - w / 2, yb), top[0], (x - w * .3, top[0][1] + 1), (x - w * .3, yb)])}" fill="{dark}" opacity=".7"/>']
    if courses and h > 10:
        cc = "".join(f"M{f(x - w / 2)},{f(yb - k)}H{f(x + w / 2)}" for k in range(6, int(h) - 3, 6))
        g.append(f'<path d="{cc}" stroke="{dark}" stroke-width=".7" opacity=".7"/>')
    sc.add("".join(g))


def fallen(sc, x, y, w, h, ang, lit="#7d88ae", body="#454e6e"):
    sc.add(f'<g transform="translate({f(x)},{f(y)}) rotate({f(ang)})"><rect x="{f(-w / 2)}" y="{f(-h)}" width="{f(w)}" height="{f(h)}" fill="{body}"/>'
           f'<rect x="{f(-w / 2)}" y="{f(-h)}" width="{f(w)}" height="{f(h * .3)}" fill="{lit}"/></g>')


def ruin(sc, cx, cy, rx, ry):
    """The broken ring of the watchtower on the crown: far walls and a tower stump, then near piers, arches, fallen stones."""
    rnd = sc.r
    SL, S, SD = P["stone_lit"], P["stone"], P["stone_dark"]
    skyc = "#0e1322"

    def at(a):
        a = math.radians(a)
        return cx + rx * math.cos(a), cy + ry * math.sin(a)

    # a faint floor inside the ring
    sc.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#2a3150"/>')
    # far side: walls whose inner faces we see, the west part turned to the moon
    for a0, a1, hgt, arch in [(192, 228, 24, True), (236, 252, 14, False), (300, 326, 22, True), (334, 352, 13, False)]:
        steps = 6
        base = [at(a0 + (a1 - a0) * k / steps) for k in range(steps + 1)]
        crest = []
        for k, (x, y) in enumerate(base):
            e = min(k, steps - k) / steps
            hh = hgt * (.5 + .5 * min(1, e * 3)) * rnd(.8, 1.05)
            crest.append((x, y - hh))
        stepc = []
        for (ax, ay), (bx, by) in zip(crest, crest[1:]):
            stepc += [(ax, ay), (bx, ay)]
        stepc.append(crest[-1])
        col = SL if a0 < 260 else S
        sc.add(f'<path d="{pth(base[::-1] + stepc)}" fill="{col}"/>')
        cc = "".join(f"M{f(base[0][0])},{f(base[0][1] - k)}L{f(base[-1][0])},{f(base[-1][1] - k)}" for k in range(5, hgt - 4, 5))
        sc.add(f'<path d="{cc}" stroke="{SD}" stroke-width=".7" opacity=".6"/>')
        if arch:  # an arched opening with the sky behind it
            mx = (base[1][0] + base[-2][0]) / 2
            my = (base[1][1] + base[-2][1]) / 2
            aw = abs(base[-2][0] - base[1][0]) * .32
            ah = hgt * .62
            sc.add(f'<path d="M{f(mx - aw)},{f(my)} V{f(my - ah + aw)} A{f(aw)},{f(aw)} 0 0 1 {f(mx + aw)},{f(my - ah + aw)} V{f(my)}Z" fill="{skyc}"/>')
    # the tower stump at the back, its upper storey broken away
    tx, ty = at(272)
    tw, th = 38, 50
    top = [(tx - tw / 2, ty - th + 14), (tx - tw * .3, ty - th + 12), (tx - tw * .3, ty - th + 4), (tx - tw * .05, ty - th + 4),
           (tx - tw * .05, ty - th), (tx + tw * .18, ty - th), (tx + tw * .18, ty - th + 7), (tx + tw * .36, ty - th + 9), (tx + tw / 2, ty - th + 20)]
    sc.add(f'<path d="{pth([(tx - tw / 2, ty)] + top + [(tx + tw / 2, ty)])}" fill="{S}"/>'
           f'<path d="{pth([(tx + tw * .18, ty - th + 7), (tx + tw * .36, ty - th + 9), (tx + tw / 2, ty - th + 20), (tx + tw / 2, ty), (tx + tw * .18, ty)])}" fill="{SL}"/>')
    cc = "".join(f"M{f(tx - tw / 2)},{f(ty - k)}H{f(tx + tw / 2)}" for k in range(6, th - 2, 6))
    sc.add(f'<path d="{cc}" stroke="{SD}" stroke-width=".7" opacity=".55"/>')
    sc.add(f'<path d="M{f(tx - 5)},{f(ty - 20)} V{f(ty - 30)} A5,5 0 0 1 {f(tx + 5)},{f(ty - 30)} V{f(ty - 20)}Z" fill="{skyc}"/>'
           f'<path d="M{f(tx - 3)},{f(ty)} V{f(ty - 9)} A3,3 0 0 1 {f(tx + 3)},{f(ty - 9)} V{f(ty)}Z" fill="#0b0e18"/>')
    # near side: standing piers, a gateway arch, a half-fallen arch, stumps
    near = []
    for a, w, h in [(10, 9, 24), (28, 8, 15), (98, 11, 18), (120, 10, 8), (172, 8, 20)]:
        x, y = at(a)
        lit = math.cos(math.radians(a)) > 0
        near.append((y, lambda x=x, y=y, w=w, h=h, lit=lit: block(sc, x, y + 1, w, h, S if lit else "#3d4563", SL, SD)))

    def arch(a0, a1, h, broken=False):
        (x0, y0), (x1, y1) = at(a0), at(a1)
        r = (x0 - x1) / 2
        yb = max(y0, y1) + 1
        w = 8
        sp = yb - h
        if broken:
            d = f"M{f(x1)},{f(yb)} V{f(sp)} A{f(r)},{f(r)} 0 0 1 {f(x1 + r * 1.2)},{f(sp - r * .98)}"
            stub = f"M{f(x0)},{f(yb)} V{f(sp + 6)}"
        else:
            d = f"M{f(x1)},{f(yb)} V{f(sp)} A{f(r)},{f(r)} 0 0 1 {f(x0)},{f(sp)} V{f(yb)}"
            stub = ""
        g = f'<path d="{d}{stub}" fill="none" stroke="{S}" stroke-width="{w}"/>'
        g += f'<path d="{d}{stub}" fill="none" stroke="{SL}" stroke-width="2" transform="translate({w / 2 - 1},0)" opacity=".85"/>'
        g += f'<path d="M{f(x1 - w / 2)},{f(sp - 4)} H{f(x1 + w / 2)} M{f(x0 - w / 2)},{f(sp - 4 if not broken else sp + 10)} H{f(x0 + w / 2)}" stroke="{SD}" stroke-width="1"/>'
        sc.add(g)
    near.append((at(52)[1], lambda: arch(44, 70, 22)))
    near.append((at(146)[1], lambda: arch(138, 160, 18, broken=True)))
    for _, fn in sorted(near, key=lambda t: t[0]):
        fn()
    # fallen blocks on the crown and tumbled down the ledges
    for x, y, w, h, a in [(748, 112, 12, 5, 8), (822, 111, 10, 5, -12), (856, 108, 8, 4, 20), (712, 106, 9, 4, -25),
                          (700, 141, 11, 5, 14), (902, 138, 12, 6, -18), (676, 146, 8, 4, 30), (930, 182, 10, 5, 10),
                          (640, 186, 9, 5, -20), (786, 114, 7, 3, 5)]:
        fallen(sc, x, y, w, h, a)
    # a clear hit area so the whole ring is easy to click
    sc.add(f'<ellipse cx="{cx}" cy="{cy - 18}" rx="{rx + 6}" ry="30" fill="#000" fill-opacity="0"/>')


# ---------- the foreground ----------

def crag(sc, x, y, w, h):
    """An angular, broken rock: a flat-topped mass with a moonlit top and east facet, a dark west facet and a crack."""
    rnd = sc.r
    p = [(x - w / 2, y), (x - w * .46, y - h * rnd(.45, .6)), (x - w * .28, y - h * rnd(.85, 1)), (x + w * rnd(-.05, .1), y - h),
         (x + w * .3, y - h * rnd(.82, .95)), (x + w * .48, y - h * rnd(.35, .55)), (x + w / 2, y)]
    sc.add(f'<path d="{pth(p)}" fill="#1b1f2f"/>'
           f'<path d="{pth([p[2], p[3], p[4], (p[4][0] - w * .05, p[4][1] + h * .12), (p[2][0] + w * .08, p[2][1] + h * .1)])}" fill="#56618a"/>'
           f'<path d="{pth([p[4], p[5], p[6], (x + w * .28, y), (p[4][0] - w * .05, p[4][1] + h * .12)])}" fill="#363f60"/>'
           f'<path d="{pth([p[0], p[1], p[2], (p[2][0] + w * .08, p[2][1] + h * .1), (x - w * .3, y)])}" fill="#11141f"/>'
           f'<path d="M{f(x + w * rnd(-.1, .1))},{f(y - h * .85)} l{f(w * .04)},{f(h * .35)} l{f(-w * .05)},{f(h * .5)}" fill="none" stroke="#0a0c14" stroke-width="1.3"/>')


def heather(sc, x, y, s):
    """A low clump of heather: a dark mound, purple flower spikes greyed by the moon."""
    rnd = sc.r
    g = [f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(s)}" ry="{f(s * .42)}" fill="#151927"/>']
    d1 = d2 = ""
    for _ in range(int(s * 1.1)):
        px = x + rnd(-s * .9, s * .9)
        py = y - rnd(0, s * .3)
        hh = rnd(s * .25, s * .6)
        d1 += f"M{f(px)},{f(py)}l{f(rnd(-1, 1))},{f(-hh)}"
        if rnd(0, 1) < .5:
            d2 += f"M{f(px)},{f(py - hh * .7)}l0,{f(-hh * .3)}"
    g.append(f'<path d="{d1}" stroke="#30283f" stroke-width="2" stroke-linecap="round"/>')
    g.append(f'<path d="{d2}" stroke="#5b4d74" stroke-width="1.5" stroke-linecap="round" opacity=".7"/>')
    sc.add("".join(g))


def gnarl(sc, x, y, s, flip=1):
    """A wind-bent hawthorn: a twisted, leaning trunk and a ragged crown combed flat by the west wind."""
    rnd = sc.r
    k = flip
    tx, ty = x + k * s * .42, y - s * .62  # where the crown sits
    trunk = (f"M{f(x - s * .05)},{f(y)} C{f(x + k * s * .12)},{f(y - s * .22)} {f(x - k * s * .08)},{f(y - s * .36)} {f(x + k * s * .12)},{f(y - s * .46)} "
             f"S{f(tx - k * s * .1)},{f(ty + s * .02)} {f(tx)},{f(ty)}")
    br = (f"M{f(x + k * s * .1)},{f(y - s * .44)} Q{f(x - k * s * .1)},{f(y - s * .58)} {f(x - k * s * .18)},{f(y - s * .7)}"
          f"M{f(x + k * s * .2)},{f(y - s * .52)} Q{f(x + k * s * .2)},{f(y - s * .7)} {f(x + k * s * .12)},{f(y - s * .8)}"
          f"M{f(tx)},{f(ty)} Q{f(tx + k * s * .2)},{f(ty - s * .02)} {f(tx + k * s * .36)},{f(ty + s * .06)}")
    g = [f'<path d="{trunk}" fill="none" stroke="#0e111b" stroke-width="{f(s * .075)}" stroke-linecap="round"/>',
         f'<path d="{br}" fill="none" stroke="#0e111b" stroke-width="{f(s * .03)}" stroke-linecap="round"/>',
         f'<path d="{trunk}" fill="none" stroke="#424c6e" stroke-width="{f(s * .014)}" transform="translate({f(s * .022)},0)" opacity=".8"/>']
    # leaf clumps at the ends of the branches, at uneven heights, combed downwind
    dark, lit = [], []
    for cx, cy, r in [(tx + k * s * .14, ty - s * .04, s * .19), (tx + k * s * .4, ty + s * .07, s * .12), (x - k * s * .18, y - s * .72, s * .15),
                      (x + k * s * .12, y - s * .82, s * .14), (x - k * s * .02, y - s * .56, s * .1)]:
        for _ in range(7):
            ex, ey = cx + k * rnd(-r * .6, r * .9), cy + rnd(-r * .45, r * .35)
            rr = r * rnd(.3, .5)
            dark.append(f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="{f(rr * 1.3)}" ry="{f(rr * .8)}"/>')
            if ey < cy - r * .1 and rnd(0, 1) < .7:
                lit.append(f'<ellipse cx="{f(ex + rr * .3)}" cy="{f(ey - rr * .4)}" rx="{f(rr * .75)}" ry="{f(rr * .28)}"/>')
    g.append(f'<g fill="#0f121d">{"".join(dark)}</g><g fill="#323b5c" opacity=".85">{"".join(lit)}</g>')
    # bare twigs poking out of the crown
    tw = "".join(f"M{f(x + k * s * rnd(-.2, .6))},{f(y - s * rnd(.6, .8))}l{f(k * s * rnd(.05, .14))},{f(-s * rnd(.08, .16))}" for _ in range(6))
    g.append(f'<path d="{tw}" stroke="#0f121d" stroke-width="{f(s * .012)}" stroke-linecap="round"/>')
    sc.add("".join(g))


def build(seed=11):
    sc = Scene(seed)
    hill_c = 790
    sc.defs.append('<linearGradient id="turf" gradientUnits="userSpaceOnUse" x1="540" y1="0" x2="1060" y2="0">'
                   '<stop offset="0" stop-color="#1b2032"/><stop offset=".45" stop-color="#2a3150"/>'
                   '<stop offset=".72" stop-color="#465281"/><stop offset="1" stop-color="#36406a"/></linearGradient>')

    # ================= sky =================
    mx, my = 1150, 72
    with sc.layer("sky", 0):
        sc.sky(sc.lin("sky", P["sky"]))
        stars = []
        for _ in range(170):
            x, y = sc.r(0, W), sc.r(0, 200)
            stars.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(sc.r(.4, 1.2))}" opacity="{f(sc.r(.25, .85))}"/>')
        sc.add(f'<g fill="#dfe5f7">{"".join(stars)}</g>')
        sc.add(f'<circle cx="{mx}" cy="{my}" r="230" fill="{sc.rad("halo", [(0, P["moon_glow"], .32), (.18, P["moon_glow"], .14), (1, P["moon_glow"], 0)])}"/>')
        with sc.hot("weathertop-moon", "The moon", "A cold moon rides between rags of storm cloud over the hills.", "pulse"):
            sc.add(f'<circle cx="{mx}" cy="{my}" r="24" fill="{P["moon"]}"/>'
                   f'<circle cx="{mx - 7}" cy="{my - 5}" r="6" fill="#cfd6ea" opacity=".6"/><circle cx="{mx + 6}" cy="{my + 7}" r="4" fill="#cfd6ea" opacity=".5"/>'
                   f'<circle cx="{mx + 9}" cy="{my - 9}" r="3" fill="#cfd6ea" opacity=".45"/>')
        # torn storm cloud streaming across from the west, rims lit by the moon
        for cx, cy, ln, th, sd, op in [(170, 34, 520, 40, 1.1, 1), (600, 70, 560, 30, 2.3, .95), (1000, 24, 520, 36, 3.7, 1),
                                        (1500, 26, 420, 34, 4.1, 1), (1400, 136, 480, 26, 5.2, .9), (320, 132, 420, 20, 6.3, .8),
                                        (1000, 150, 300, 16, 7.4, .7)]:
            near = math.exp(-((cx - mx) / 380) ** 2)
            body = "#20273f" if near < .3 else "#2a3251"
            with sc.fx("cloud"):
                torn_cloud(sc, cx, cy, ln, th, "#7d8bb8" if near > .3 else "#333d5e", body, rim=1.2 + 1.8 * near, seed=sd, op=op)
        with sc.fx("cloud"):  # a rag of cloud dragging across the face of the moon
            torn_cloud(sc, mx - 20, my + 14, 340, 24, "#c3cdec", "#2e3657", rim=2.6, seed=8.8, op=.95)
            torn_cloud(sc, mx + 110, my - 30, 200, 10, "#aab7e0", "#283050", rim=1.8, seed=9.6, op=.85)

    # ================= far: the Weather Hills and the low country =================
    with sc.layer("far", .15):
        sc.ridge(214, 14, [(1.8, 1), (4.2, .5), (9, .2)], P["far1"], seed=2.2)
        sc.add(f'<rect x="-30" y="170" width="{W + 60}" height="90" fill="{sc.lin("haze1", [(0, P["haze"], 0), (1, P["haze"], .35)])}"/>')
        hills = []
        for x in range(-30, 700, 6):
            t = (x + 30) / 730
            y = 222 - 50 * t ** .8 - 24 * abs(math.sin(x / 70 + .6)) ** 1.6 + 4 * math.sin(x / 17)
            hills.append((x, y))
        for x in range(700, 1000, 6):
            hills.append((x, hills[-1][1] + 3))
        sc.add(f'<path d="{pth(hills + [(1000, H), (-30, H)])}" fill="{sc.lin("ridgeg", [(0, P["far2"]), (1, P["far3"])], x2=1, y2=0)}"/>')
        sc.add(f'<path d="{pth([(a, b + .5) for a, b in hills[::2] if a < 690], False)}" fill="none" stroke="#45527a" stroke-width="1.1" opacity=".55"/>')
        dots = []
        for x in range(10, 680, 9):
            y = sc.y_at(hills, x)
            if sc.r(0, 1) < .55:
                dots.append(f'<circle cx="{f(x + sc.r(-3, 3))}" cy="{f(y + sc.r(3, 14))}" r="{f(sc.r(1.6, 3.2))}"/>')
        sc.add(f'<g fill="#181d30">{"".join(dots)}</g>')
        sc.ridge(198, 16, [(2.2, 1), (5.3, .45), (11, .15)], "#252d48", seed=5.7, x0=1040, x1=W + 60, taper=260)
        sc.add(f'<rect x="-30" y="170" width="{W + 60}" height="70" fill="{sc.lin("haze3", [(0, P["haze"], 0), (1, P["haze"], .3)])}"/>')
        sc.ridge(232, 7, [(1.3, 1), (3.6, .4), (8, .15)], P["far2"], seed=4.4, x0=880, x1=W + 40)
        sc.add(f'<path d="M1060,274 C1160,262 1270,252 1400,246 C1490,242 1570,241 1640,240" fill="none" stroke="{P["path"]}" stroke-width="1.6" opacity=".55"/>')
        sc.add(f'<rect x="-30" y="210" width="{W + 60}" height="70" fill="{sc.lin("haze2", [(0, P["haze"], 0), (1, P["haze"], .18)])}"/>')

    # ================= mid: Amon Sûl, its crown, the path and the dell =================
    with sc.layer("mid", .4):
        lfoot = sc.ridge(252, 10, [(1.5, 1), (3.3, .4)], P["far3"], seed=1.4, x0=-30, x1=620)
        rfoot = sc.ridge(256, 9, [(1.2, 1), (2.8, .5)], P["far3"], seed=3.3, x0=930, x1=W + 30)
        for x in list(range(0, 600, 11)) + list(range(960, W, 11)):
            pts = lfoot if x < 620 else rfoot
            if sc.r(0, 1) < .5:
                scrub(sc, x, sc.y_at(pts, x) + sc.r(6, 20), sc.r(4, 7), "#141929")
        # the long scree slopes at the hill's foot
        l0x, l0y = foot(TIERS[-1], -1)
        r0x, r0y = foot(TIERS[-1], 1)
        base = []
        for k in range(21):
            t = k / 20
            base.append((380 + (l0x - 380) * t, 300 - (300 - l0y) * t ** 1.8 + sc.r(-1, 1)))
        for k in range(21):
            t = k / 20
            base.append((r0x + (1200 - r0x) * t, r0y + (298 - r0y) * t ** .55 + sc.r(-1, 1)))
        sc.add(f'<path d="{pth(base + [(1200, H + 10), (380, H + 10)])}" fill="url(#turf)"/>')
        sc.add(f'<path d="{pth(base + [(1200, H + 10), (380, H + 10)])}" fill="{sc.lin("basev", [(0, "#10131e", 0), (.55, "#10131e", .55), (1, "#10131e", .8)])}"/>')
        sc.add(f'<path d="{pth([p for p in base if p[0] > r0x], False)}" fill="none" stroke="#6d7aa3" stroke-width="1.2" opacity=".55"/>')
        scree = "".join(f"M{f(x)},{f(y)}l{f(sc.r(1, 3))},{f(sc.r(4, 9))}" for x, y in
                        [(sc.r(900, 1120), sc.r(236, 282)) for _ in range(34)] + [(sc.r(470, 560), sc.r(250, 286)) for _ in range(10)])
        sc.add(f'<path d="{scree}" stroke="#56628c" stroke-width=".9" stroke-linecap="round" opacity=".5"/>')
        # the tiers, lowest (nearest) first so each higher one sits back on the ledge below it
        for i in range(len(TIERS) - 1, -1, -1):
            tier(sc, TIERS[i], TIERS[i - 1] if i else None, i)
        for x, yt, yb, w in [(694, 148, 196, 20), (906, 140, 186, 24), (842, 186, 236, 22), (636, 194, 238, 18), (1004, 214, 250, 18), (760, 186, 222, 14)]:
            buttress(sc, x, yt, yb, w)
        # boulders and scrub resting on the ledges
        for i, T in enumerate(TIERS[1:], 1):
            for _ in range(7):
                u = sc.r(-.95, .95)
                x, y = lip(T, u)
                y -= sc.r(1, 3)
                if u > .1:
                    scrub(sc, x, y, sc.r(2.5, 4.5), "#1c2236", "#3a456a")
                else:
                    scrub(sc, x, y, sc.r(2.5, 4.5), "#141827")
        for x, y, s in [(944, 136, 5), (960, 178, 6), (1000, 214, 6), (640, 180, 5), (588, 216, 5), (990, 252, 8), (1060, 262, 9)]:
            boulder(sc, x, y, s, "#4a5578", "#262c43", "#141826")

        # the crown: the broken ring of the watchtower
        with sc.hot("weathertop-ruin", "Amon Sûl", "Only a broken ring of stones is left of the great watchtower.", "flash"):
            ruin(sc, 792, 100, 74, 9)

        # the old path, switching back across the ledges of the western side
        trail = [(606, 244), (584, 236), (566, 226), (572, 216), (596, 210), (606, 198), (612, 186), (630, 180),
                 (646, 174), (656, 160), (664, 146), (684, 140), (704, 134), (712, 122), (718, 110), (734, 104)]
        with sc.hot("weathertop-path", "The old path", "A worn track zigzags up the western ledges to the summit.", "pulse"):
            sc.add(f'<path d="{pth(trail, False)}" fill="none" stroke="#000" stroke-opacity="0" stroke-width="16" stroke-linejoin="round"/>')
            sc.add(f'<path d="{pth(trail, False)}" fill="none" stroke="#5a668f" stroke-width="1.5" stroke-dasharray="4 3" stroke-linejoin="round" opacity=".85"/>')

        # the dell under the western cliffs, sheltered by a horseshoe of rocks, with the campfire in it
        fx, fy = 592, 254
        with sc.hot("weathertop-camp", "The camp in the dell", "A small fire in a sheltered hollow, the only warm light for miles.", "sparks"):
            # firelit ground in the hollow
            sc.add(f'<ellipse cx="{fx}" cy="{fy + 2}" rx="64" ry="13" fill="{sc.rad("firelit", [(0, "#6b3d2a", .9), (.5, "#3c2a2c", .6), (1, "#1a1d2c", 0)])}"/>')
            # the rocks round the back of the dell, their faces turned to the fire warmed by it
            for x, y, w, h in [(536, 256, 24, 18), (558, 246, 30, 30), (590, 238, 26, 24), (616, 240, 34, 32), (646, 250, 24, 20), (664, 260, 16, 10)]:
                side = 1 if x < fx - 8 else (-1 if x > fx + 8 else 0)  # which way the fire is from this rock
                pk = (x + side * w * .1 + sc.r(-3, 3), y - h)
                pts = [(x - w / 2, y), (x - w * .46, y - h * .45), (x - w * .22, y - h * .9), pk, (x + w * .3, y - h * .85), (x + w / 2, y - h * .4), (x + w / 2, y)]
                sc.add(f'<path d="{pth(pts)}" fill="#1a1d2c"/>')
                sc.add(f'<path d="{pth([(x - w * .22, y - h * .9), pk, (x + w * .3, y - h * .85), (x + w / 2, y - h * .4), (x + w * .15, y - h * .55)])}" fill="#465174" opacity=".75"/>')
                if side > 0:  # the fire is to the right: light on the east face
                    warm = [(pk[0], pk[1] + 2), (x + w * .3, y - h * .85), (x + w / 2, y - h * .4), (x + w / 2, y), (x + w * .05, y)]
                elif side < 0:
                    warm = [(pk[0], pk[1] + 2), (x - w * .22, y - h * .9), (x - w * .46, y - h * .45), (x - w / 2, y), (x - w * .05, y)]
                else:
                    warm = [(x - w * .4, y - h * .5), (x + w * .1, y - h * .6), (x + w * .45, y - h * .38), (x + w / 2, y), (x - w / 2, y)]
                near_ = 1 - min(1, abs(x - fx) / 80)
                sc.add(f'<path d="{pth(warm)}" fill="{sc.lin(f"rw{x}", [(0, "#e08a48"), (1, "#7a3c26")])}" opacity="{f(.35 + .5 * near_)}"/>')
            # warm light spilling over the rocks and the grass
            sc.add(f'<circle cx="{fx}" cy="{fy - 6}" r="80" fill="{sc.rad("fireglow", [(0, P["fire"], .5), (.25, P["ember"], .22), (1, P["ember"], 0)])}"/>')
            grass = "".join(f"M{f(x)},{f(fy + 6 + sc.r(-3, 6))}l{f(sc.r(-1.5, 1.5))},{f(-sc.r(3, 7))}" for x in [fx + sc.r(-56, 56) for _ in range(40)])
            sc.add(f'<path d="{grass}" stroke="#a8673c" stroke-width="1" opacity=".6"/>')
            # ring of hearth stones
            for k in range(9):
                a = math.pi * 2 * k / 9
                sc.add(f'<ellipse cx="{f(fx + 11 * math.cos(a))}" cy="{f(fy + 3 + 3 * math.sin(a))}" rx="3.2" ry="2.2" fill="{"#d0894e" if math.sin(a) < .2 else "#2a2230"}"/>')
            # a hooded figure sitting by the fire, and a pack
            sx_ = fx - 26
            sc.add(f'<path d="M{sx_ - 6},{fy + 5} Q{sx_ - 6},{fy - 8} {sx_ - 1},{fy - 14} Q{sx_ + 3},{fy - 18} {sx_ + 5},{fy - 12} Q{sx_ + 7},{fy - 4} {sx_ + 7},{fy + 5}Z" fill="#0d0f18"/>'
                   f'<path d="M{sx_ + 4},{fy - 13} Q{sx_ + 7},{fy - 6} {sx_ + 7},{fy + 5}" fill="none" stroke="#c46a3a" stroke-width="1.2" opacity=".8"/>'
                   f'<rect x="{fx + 20}" y="{fy - 4}" width="9" height="9" rx="2" fill="#141625"/><path d="M{fx + 20},{fy - 3} v8" stroke="#c46a3a" stroke-width="1" opacity=".7"/>')
            with sc.fx("flicker"):
                sc.add(f'<circle cx="{fx}" cy="{fy - 4}" r="22" fill="{sc.rad("firecore", [(0, P["fire"], .55), (1, P["fire"], 0)])}"/>')
                sc.add(f'<path d="M{fx - 6},{fy + 3} Q{fx - 7},{fy - 4} {fx - 3},{fy - 9} Q{fx - 2},{fy - 4} {fx},{fy - 6} Q{fx + 1},{fy - 13} {fx + 3},{fy - 16} Q{fx + 4},{fy - 9} {fx + 6},{fy - 7} Q{fx + 8},{fy - 2} {fx + 6},{fy + 3}Z" fill="{P["fire"]}"/>'
                       f'<path d="M{fx - 2.5},{fy + 3} Q{fx - 3},{fy - 3} {fx},{fy - 8} Q{fx + 3},{fy - 3} {fx + 3},{fy + 3}Z" fill="{P["fire_core"]}"/>')
            sc.add(f'<path d="M{fx - 8},{fy + 4} L{fx + 8},{fy + 2} M{fx - 7},{fy + 2} L{fx + 9},{fy + 4.5}" stroke="#3a2418" stroke-width="2" stroke-linecap="round"/>')
            with sc.fx("smoke"):
                sc.smoke(fx + 2, fy - 20, 7, "#5a6584", .3, -1.4)
            with sc.fx("embers"):
                for k in range(9):
                    sc.add(f'<circle cx="{f(fx + sc.r(-6, 6))}" cy="{f(fy - sc.r(12, 34))}" r="{f(sc.r(.6, 1.1))}" fill="{P["fire"]}" opacity="{f(sc.r(.4, .9))}"/>')

        # scrub on the lower slopes
        for _ in range(26):
            x = sc.r(420, 1180)
            y = sc.r(250, 296)
            if abs(x - fx) < 80 and y < 270 or 540 < x < 1040 and y < 238:
                continue
            scrub(sc, x, y, sc.r(2.6, 5), "#1b2033", "#2b3452" if x > hill_c else None)

    # ================= near: the heath at the hill's foot, ground mist =================
    with sc.layer("near", .7):
        mist = sc.rad("mist", [(0, "#8f9cc6", .16), (.6, "#8f9cc6", .07), (1, "#8f9cc6", 0)])
        for cx, cy, rx in [(260, 266, 300), (1200, 270, 320), (1480, 258, 220)]:
            sc.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="16" fill="{mist}"/>')
        fg = sc.ridge(298, 6, [(1.6, 1), (4.1, .4)], "#171b28", seed=6.2, x0=-40, x1=W + 40)
        for x in range(-10, W + 10, 13):
            if sc.r(0, 1) < .6:
                scrub(sc, x + sc.r(-5, 5), sc.y_at(fg, x) + sc.r(4, 26), sc.r(5, 10), "#11141f")
        for x, s in [(150, 18), (240, 12), (420, 16), (980, 14), (1180, 16), (1300, 26), (1480, 14)]:
            boulder(sc, x, sc.y_at(fg, x) + 20, s, "#38425f", "#1d2234", "#10131d")
        for x in [60, 330, 480, 700, 860, 1080, 1390, 1540]:
            heather(sc, x + sc.r(-20, 20), sc.y_at(fg, x) + sc.r(10, 24), sc.r(10, 16))
        sc.add(f'<ellipse cx="560" cy="300" rx="200" ry="12" fill="{mist}"/>')

    # ================= front: rocks, heather and thorn right in front of us =================
    with sc.layer("front", 1):
        ground = sc.ridge(336, 5, [(2.1, 1), (5, .4)], P["ground"], seed=8.1, x0=-40, x1=W + 40)
        # clusters of broken, angular rock on either side, leaving the middle open
        for x, y, w, h in [(-10, 336, 90, 46), (70, 340, 70, 30), (150, 328, 64, 40), (250, 338, 54, 22), (36, 350, 50, 18),
                           (1360, 336, 60, 28), (1430, 330, 84, 52), (1520, 334, 70, 40), (1600, 340, 90, 50), (1490, 352, 50, 18)]:
            crag(sc, x, y, w, h)
        gnarl(sc, 205, 300, 95, 1)
        gnarl(sc, 1455, 282, 110, -1)
        gnarl(sc, 372, 332, 60, 1)
        for x, y, s in [(330, 338, 20), (560, 352, 14), (720, 346, 24), (930, 350, 18), (1120, 342, 22), (1260, 352, 16)]:
            boulder(sc, x, y, s, "#424d72", "#1b2032", "#0e111b")
        for x, y, s in [(110, 330, 22), (420, 344, 18), (640, 348, 20), (820, 352, 16), (1010, 346, 22), (1200, 348, 18), (1330, 350, 20), (1580, 330, 18)]:
            heather(sc, x, y, s)
        sc.tufts(326, 400, 120, ["#1d2232", "#20263a", "#1a1e2c"], 6, 16)
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    svg = build().svg("Weathertop by moonlight")
    # round larger coordinates to whole pixels to keep the file small
    svg = re.sub(r"(?<![\d.#])(-?\d{3,})\.\d\b", lambda m: str(round(float(m.group(0)))), svg)
    with open(f"{out}/weathertop.svg", "w") as fh:
        fh.write(svg)
