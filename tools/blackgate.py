"""The Black Gate: the Morannon under a smoking sky.

The great iron gate shut across the pass where the Ash Mountains meet the
Mountains of Shadow, the Towers of the Teeth on the hills either side, walls
climbing the cliffs, and the ash plain of Dagorlad in front: slag heaps, foul
pools, pits and stakes. Mordor's fires light the smoke from below the horizon,
and ash drifts down over everything.
"""
import math
import sys
from scene_kit import Scene, W, H, f

P = dict(
    sky=[(0, "#17130f"), (.3, "#261f1a"), (.5, "#3a2c22"), (.62, "#5a3a25"), (.7, "#7c4627")],
    glow="#ec7d3c", glow_hot="#ffb36b",
    cloud="#2a221c", cloud_lit="#6e4026", cloud_far="#3c2e25", cloud_far_lit="#8a4f2a",
    far="#45332a", far_lit="#8a5233", haze="#9a5a33",
    mid="#211a15", mid_lit="#7a4426",
    near="#16110d", near_lit="#4e2d1b",
    iron="#0f0c0a", iron_lit="#2b211b", rivet="#4a3628",
    plain="#251e18", plain_far="#34281f", plain_dark="#1b1611", bg="#16130e",
    slag="#1b1511", slag_lit="#7a4528", slag_dark="#120e0b",
    pool="#4a2a19", pool_lit="#a8582c", pool_dark="#1a130e",
    road="#3a3029", road_edge="#2a221b",
    ash="#c8b9a6", ember="#ec7d3c", smoke="#3a2e26",
)


# ---------- helpers ----------
def jag(sc, ctrl, disp=.22, depth=4):
    """Midpoint displacement between hand-placed control points: a jagged ridge.
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


def range_(sc, gid, ctrl, fill, lit, base, light_x, disp=.22, depth=4, crease=None, op=.85):
    """A jagged range closed to `base`, with the faces turned toward light_x lit from below the horizon."""
    pts = jag(sc, ctrl, disp, depth)
    sc.add(f'<path d="{poly(pts, base)}" fill="{fill}"/>')
    n = 2 ** depth
    grad = sc.lin(gid, [(0, lit, op), (.55, lit, op * .35), (1, lit, 0)])
    g = []
    for k in range(1, len(ctrl) - 1):
        px, py = ctrl[k]
        if py > ctrl[k - 1][1] or py > ctrl[k + 1][1]:
            continue  # only peaks
        j = k + 1 if light_x > px else k - 1
        seg = pts[min(k, j) * n: max(k, j) * n + 1]
        if j < k:
            seg = seg[::-1]
        vx, vy = seg[-1]
        apex = (px + (vx - px) * sc.r(.45, .7), min(base, max(py, vy) + abs(vx - px) * sc.r(.5, .9) + 10))
        face = seg + [apex]
        g.append(f'<path d="{poly(face)}" fill="{grad}"/>')
        if crease:  # a gully or two down the shadowed side
            for c in range(2):
                sx = px - (vx - px) * sc.r(.15, .5)
                sy = Scene.y_at(sorted(pts), sx) if pts[0][0] <= sx <= pts[-1][0] else py
                g.append(f'<path d="M{f(sx)},{f(sy + 2)} l{f(sc.r(-6, 6))},{f(sc.r(14, 34))}" stroke="{crease}" stroke-width="1" fill="none" opacity=".6"/>')
    # smaller facets on the lesser crags, and a rim of light on every edge facing the fire
    sub = pts[::4]
    for k in range(1, len(sub) - 1):
        px, py = sub[k]
        if not (py < sub[k - 1][1] and py < sub[k + 1][1]):
            continue
        j = k + 1 if light_x > px else k - 1
        vx, vy = sub[j]
        seg = pts[min(k, j) * 4: max(k, j) * 4 + 1]
        if j < k:
            seg = seg[::-1]
        apex = (px + (vx - px) * .55, min(base, max(py, vy) + abs(vx - px) * .7 + 6))
        g.append(f'<path d="{poly(seg + [apex])}" fill="{grad}" opacity=".7"/>')
    rim = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        mx = (ax + bx) / 2
        if (by - ay) * (1 if light_x > mx else -1) > 0:
            rim.append(f"M{f(ax)},{f(ay)} L{f(bx)},{f(by)}")
    g.append(f'<path d="{" ".join(rim)}" stroke="{lit}" stroke-width="1.1" stroke-linecap="round" fill="none" opacity="{f(op * .8)}"/>')
    sc.add("".join(g))
    return pts


def ash_cloud(sc, x, y, w, h, grad, op=1.0, puffs=9):
    """A long smoke bank: overlapping billows, dark above and lit orange along the belly (grad)."""
    g = [f'<g opacity="{op}" fill="{grad}">']
    for i in range(puffs):
        t = i / (puffs - 1)
        bx = x - w / 2 + t * w + sc.r(-w * .04, w * .04)
        rr = h * (.5 + .5 * math.sin(t * math.pi)) * sc.r(.7, 1.15)
        by = y - rr * .2 + sc.r(-h * .15, h * .15)
        g.append(f'<ellipse cx="{f(bx)}" cy="{f(by)}" rx="{f(rr * sc.r(1.5, 2.3))}" ry="{f(rr * .62)}"/>')
    g.append("</g>")
    sc.add("".join(g))


def tower(sc, x, base, top, wb, wt, lit, tilt=1):
    """One of the Towers of the Teeth: a tapering black spire in tiers, a crown of spikes, lit slits."""
    iron, iron_lit = P["iron"], P["iron_lit"]
    h = base - top
    tiers = [0, .28, .52, .72, .86]
    g = []
    # body, tier by tier: each tier slightly narrower, with a jutting ledge under it
    for i, t0 in enumerate(tiers):
        t1 = tiers[i + 1] if i + 1 < len(tiers) else 1.0
        y0, y1 = base - h * t0, base - h * t1
        w0 = wb + (wt - wb) * t0
        w1 = wb + (wt - wb) * t1
        if i == len(tiers) - 1:  # the crown
            g.append(f'<path d="M{f(x - w0 / 2 - 3)},{f(y0)} L{f(x - w0 / 2)},{f(y0 - 6)} L{f(x - w1 * .9)},{f(y1 + 6)} L{f(x - w1 * .8)},{f(y1 - 10)} L{f(x - w1 * .45)},{f(y1 + 4)} L{f(x)},{f(y1 - 22)} L{f(x + w1 * .45)},{f(y1 + 4)} L{f(x + w1 * .8)},{f(y1 - 10)} L{f(x + w1 * .9)},{f(y1 + 6)} L{f(x + w0 / 2)},{f(y0 - 6)} L{f(x + w0 / 2 + 3)},{f(y0)}Z" fill="{iron}"/>')
            continue
        g.append(f'<path d="M{f(x - w0 / 2)},{f(y0)} L{f(x - w1 / 2)},{f(y1)} L{f(x + w1 / 2)},{f(y1)} L{f(x + w0 / 2)},{f(y0)}Z" fill="{iron}"/>')
        # lit edge facing the glow
        e0, e1 = (x + tilt * w0 / 2, x + tilt * w1 / 2)
        g.append(f'<path d="M{f(e0)},{f(y0)} L{f(e1)},{f(y1)} L{f(e1 - tilt * w1 * .22)},{f(y1)} L{f(e0 - tilt * w0 * .22)},{f(y0)}Z" fill="{lit}" opacity=".55"/>')
        if i:  # ledge with fangs under it
            lw = w0 + 10
            g.append(f'<rect x="{f(x - lw / 2)}" y="{f(y0 - 4)}" width="{f(lw)}" height="5" fill="{iron}"/>')
            g.append(f'<rect x="{f(x + (tilt - 1) * lw / 4 + (lw / 2 - 6 if tilt > 0 else 0))}" y="{f(y0 - 4)}" width="6" height="2" fill="{lit}" opacity=".6"/>')
            for k in range(-2, 3):
                fx = x + k * lw / 5
                g.append(f'<path d="M{f(fx - 2)},{f(y0 + 1)} L{f(fx)},{f(y0 + 6)} L{f(fx + 2)},{f(y0 + 1)}Z" fill="{iron}"/>')
            for k in (-1, 1):  # spikes off the ledge corners
                g.append(f'<path d="M{f(x + k * lw / 2)},{f(y0 - 4)} l{f(k * 7)},-9 l{f(-k * 2)},9Z" fill="{iron}"/>')
        # window slits
        for k in range(2 if i < 2 else 1):
            sx = x + (k - (.5 if i < 2 else 0)) * w1 * .45
            sy = y0 - (y0 - y1) * sc.r(.35, .6)
            on = sc.r(0, 1) < .7
            g.append(f'<rect x="{f(sx - 1.2)}" y="{f(sy)}" width="2.4" height="{f(sc.r(6, 10))}" fill="{P["glow"] if on else "#2a1f18"}" opacity="{".9" if on else "1"}"/>')
    sc.add("".join(g))


def gate(sc, x0, x1, top, bottom):
    iron, iron_lit, rivet = P["iron"], P["iron_lit"], P["rivet"]
    cx = (x0 + x1) / 2
    g = []
    # the wall across the pass, with battlements
    g.append(f'<rect x="{f(x0)}" y="{f(top)}" width="{f(x1 - x0)}" height="{f(bottom - top)}" fill="{iron}"/>')
    x = x0
    while x < x1 - 4:
        g.append(f'<rect x="{f(x)}" y="{f(top - 7)}" width="7" height="8" fill="{iron}"/>')
        x += 12
    # buttresses
    for bx in [x0 + 14, x0 + 54, x1 - 54, x1 - 14]:
        g.append(f'<path d="M{f(bx - 7)},{f(bottom)} L{f(bx - 5)},{f(top - 12)} L{f(bx)},{f(top - 22)} L{f(bx + 5)},{f(top - 12)} L{f(bx + 7)},{f(bottom)}Z" fill="{iron}"/>')
        g.append(f'<path d="M{f(bx + (2 if bx > cx else -7))},{f(bottom)} L{f(bx + (1 if bx > cx else -5))},{f(top - 12)} L{f(bx)},{f(top - 22)} L{f(bx + (0 if bx > cx else -1))},{f(bottom)}Z" fill="{iron_lit}" opacity=".7"/>')
    # gatehouse over the doors
    gw, gt = 128, top - 30
    g.append(f'<path d="M{f(cx - gw / 2 - 8)},{f(top)} L{f(cx - gw / 2 - 8)},{f(gt + 8)} L{f(cx - gw / 2)},{f(gt)} L{f(cx + gw / 2)},{f(gt)} L{f(cx + gw / 2 + 8)},{f(gt + 8)} L{f(cx + gw / 2 + 8)},{f(top)}Z" fill="{iron}"/>')
    for k in range(11):  # spikes along the gatehouse top
        sx = cx - gw / 2 + 6 + k * (gw - 12) / 10
        hh = 10 + (6 if k in (0, 5, 10) else 0)
        g.append(f'<path d="M{f(sx - 2.5)},{f(gt)} L{f(sx)},{f(gt - hh)} L{f(sx + 2.5)},{f(gt)}Z" fill="{iron}"/>')
    # the two leaves of the gate
    dt, dw = gt + 16, gw - 20
    for side in (-1, 1):
        lx = cx if side > 0 else cx - dw / 2
        g.append(f'<rect x="{f(lx)}" y="{f(dt)}" width="{f(dw / 2)}" height="{f(bottom - dt)}" fill="#120e0b"/>')
        for k in range(1, 5):  # vertical iron ribs
            vx = lx + k * dw / 10
            g.append(f'<path d="M{f(vx)},{f(dt + 2)} V{f(bottom)}" stroke="{iron_lit}" stroke-width="1.6"/>')
        for k in range(4):  # cross straps with rivets
            yy = dt + 8 + k * (bottom - dt - 10) / 3.4
            g.append(f'<rect x="{f(lx + 2)}" y="{f(yy)}" width="{f(dw / 2 - 4)}" height="3" fill="{iron_lit}"/>')
            for r in range(6):
                g.append(f'<circle cx="{f(lx + 6 + r * (dw / 2 - 12) / 5)}" cy="{f(yy + 1.5)}" r=".9" fill="{rivet}"/>')
    g.append(f'<rect x="{f(cx - dw / 2 - 4)}" y="{f(dt - 4)}" width="{f(dw + 8)}" height="5" fill="{iron_lit}"/>')
    # Mordor's light leaking through the seam and under the doors
    g.append(f'<rect x="{f(cx - .8)}" y="{f(dt + 2)}" width="1.6" height="{f(bottom - dt - 2)}" fill="{P["glow"]}" opacity=".85"/>')
    g.append(f'<rect x="{f(cx - dw / 2)}" y="{f(bottom - 2)}" width="{f(dw)}" height="2" fill="{P["glow"]}" opacity=".7"/>')
    g.append(f'<ellipse cx="{f(cx)}" cy="{f(bottom + 2)}" rx="{f(dw * .7)}" ry="8" fill="{P["glow"]}" opacity=".16"/>')
    # watch-lights on the wall
    for wx in [x0 + 32, x0 + 90, x1 - 90, x1 - 32]:
        g.append(f'<rect x="{f(wx - 1)}" y="{f(top + 12)}" width="2.2" height="6" fill="{P["glow"]}" opacity=".8"/>')
    sc.add("".join(g))


def stepped_wall(sc, pts, h, lit_side):
    """A wall climbing a slope in steps, battlemented."""
    g = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        lo, hi = min(ax, bx), max(ax, bx)
        topy = min(ay, by) - h
        g.append(f'<rect x="{f(lo)}" y="{f(topy)}" width="{f(hi - lo + 1)}" height="{f(max(ay, by) - topy + 8)}" fill="{P["iron"]}"/>')
        x = lo
        while x < hi - 3:
            g.append(f'<rect x="{f(x)}" y="{f(topy - 4)}" width="4" height="5" fill="{P["iron"]}"/>')
            x += 8
        g.append(f'<rect x="{f(lo)}" y="{f(topy)}" width="{f(hi - lo)}" height="1.4" fill="{P["near_lit"]}" opacity=".9"/>')
    sc.add("".join(g))


def pool(sc, x, y, rx, ry, gid):
    """A still, foul pool: an irregular dark rim with the burning sky in it."""
    pts = []
    for i in range(14):
        a = i / 14 * math.pi * 2
        k = sc.r(.8, 1.15)
        pts.append((x + math.cos(a) * rx * k, y + math.sin(a) * ry * k))
    rim = [(px + (px - x) * .06, py + (py - y) * .3 + 1) for px, py in pts]
    sc.add(f'<path d="{poly(rim)}" fill="{P["pool_dark"]}"/><path d="{poly(pts)}" fill="{sc.lin(gid, [(0, P["pool_lit"]), (.5, P["pool"]), (1, P["pool_dark"])])}"/>')
    for k in range(2):
        sc.add(f'<path d="M{f(x - rx * sc.r(.2, .6))},{f(y - ry * .3 + k * ry * .6)} h{f(rx * sc.r(.25, .6))}" stroke="{P["glow_hot"]}" stroke-width=".8" opacity=".4"/>')


def build(seed=11):
    sc = Scene(seed)
    sc.sky(sc.lin("sky", P["sky"]))
    # Mordor's fires below the horizon, glowing up through the pass
    sc.add(f'<ellipse cx="735" cy="250" rx="950" ry="200" fill="{sc.rad("glow", [(0, P["glow"], .5), (.35, P["glow"], .18), (1, P["glow"], 0)])}"/>')
    sc.add(f'<ellipse cx="735" cy="225" rx="280" ry="80" fill="{sc.rad("glowc", [(0, P["glow_hot"], .45), (1, P["glow"], 0)])}"/>')

    # the smoke ceiling: banks of reek, dark on top and lit from beneath
    hi = sc.lin("cl_hi", [(0, "#14100d"), (.55, "#211a15"), (.85, "#3d281c"), (1, "#57331f")])
    lo = sc.lin("cl_lo", [(0, "#211a15"), (.5, "#2c221b"), (.82, "#5e3820"), (1, "#8c4b26")])
    lo_far = sc.lin("cl_lf", [(0, "#1d1713"), (.6, "#28201a"), (1, "#5a3520")])
    for x, y, w, h, op in [(120, 14, 600, 34, 1), (700, 4, 760, 38, 1), (1300, 16, 700, 36, 1), (360, 50, 460, 26, .95), (980, 52, 520, 26, .95), (1520, 56, 360, 24, .9)]:
        ash_cloud(sc, x, y, w, h, hi, op, 13)
    for x, y, w, h, op in [(70, 98, 320, 16, .85), (1480, 92, 360, 18, .85), (1180, 118, 300, 14, .8), (300, 124, 280, 13, .8)]:
        ash_cloud(sc, x, y, w, h, lo_far, op, 9)
    for x, y, w, h, op in [(560, 104, 340, 15, .85), (930, 100, 360, 16, .85), (740, 140, 260, 11, .7)]:
        ash_cloud(sc, x, y, w, h, lo, op, 9)
    # fumes rising out of Mordor behind the gate, bending east on the wind
    for i in range(9):
        t = i / 8
        sc.add(f'<ellipse cx="{f(735 + 160 * t * t + sc.r(-10, 10))}" cy="{f(192 - t * 120)}" rx="{f(40 + t * 90)}" ry="{f(16 + t * 16)}" fill="{lo}" opacity="{f(.42 - t * .3)}"/>')

    # far peaks of the Ash Mountains beyond the pass, hazed in the glow
    far = jag(sc, [(-20, 192), (120, 172), (210, 188), (330, 164), (430, 186), (560, 170), (650, 192), (735, 186), (820, 194), (930, 168), (1040, 186), (1150, 160), (1260, 182), (1380, 156), (1480, 176), (1620, 162)], .22, 3)
    sc.add(f'<path d="{poly(far, H + 10)}" fill="{P["far"]}"/>')
    sc.add(f'<rect y="150" width="{W}" height="80" fill="{sc.lin("haze1", [(0, P["haze"], 0), (.6, P["haze"], .3), (1, P["haze"], .45)])}"/>')

    # the two ranges closing on the pass: the Mountains of Shadow (left) and the Ash Mountains (right)
    left = [(-20, 136), (30, 112), (70, 132), (120, 96), (175, 140), (230, 104), (262, 118), (300, 80), (352, 132), (400, 108), (440, 150), (490, 136), (548, 178), (600, 170), (650, 214)]
    right = [(820, 214), (868, 172), (902, 184), (952, 130), (1000, 160), (1062, 98), (1100, 124), (1140, 112), (1192, 150), (1250, 86), (1300, 128), (1352, 70), (1410, 122), (1460, 96), (1500, 112), (1556, 84), (1620, 118)]
    range_(sc, "ll", left, P["mid"], P["mid_lit"], 300, 735, .26, 4, crease="#120e0b", op=.75)
    range_(sc, "rl", right, P["mid"], P["mid_lit"], 300, 735, .26, 4, crease="#120e0b", op=.75)
    sc.add(f'<rect y="170" width="{W}" height="110" fill="{sc.lin("haze2", [(0, P["haze"], 0), (.7, P["haze"], .14), (1, P["haze"], .04)])}"/>')

    # broken foothills running down to the plain
    range_(sc, "lf", [(-20, 250), (40, 236), (90, 246), (150, 226), (210, 244), (270, 232), (330, 252), (380, 262), (420, 290)], "#1c1612", P["near_lit"], 300, 735, .2, 3, op=.5)
    range_(sc, "rf", [(1040, 290), (1100, 256), (1170, 238), (1230, 248), (1300, 222), (1370, 240), (1440, 228), (1500, 246), (1560, 230), (1620, 242)], "#1c1612", P["near_lit"], 300, 735, .2, 3, op=.5)

    # near crags either side of the pass, which the Teeth stand on
    range_(sc, "lc", [(300, 300), (372, 248), (420, 236), (462, 206), (498, 184), (520, 178), (548, 184), (576, 198), (604, 192), (640, 230)], P["near"], P["near_lit"], 330, 735, .16, 4, op=.85)
    range_(sc, "rc", [(830, 230), (866, 190), (898, 196), (926, 180), (950, 174), (982, 182), (1020, 204), (1070, 214), (1130, 236), (1200, 256), (1280, 290), (1360, 320)], P["near"], P["near_lit"], 330, 735, .16, 4, op=.85)

    # walls climbing from the gate to the towers
    stepped_wall(sc, [(614, 198), (592, 194), (566, 188), (540, 182)], 10, 1)
    stepped_wall(sc, [(858, 198), (882, 194), (906, 186), (930, 180)], 10, -1)
    gate(sc, 612, 860, 196, 272)
    # the Towers of the Teeth
    tower(sc, 522, 186, 44, 52, 24, P["near_lit"], tilt=1)
    tower(sc, 950, 182, 38, 54, 24, P["near_lit"], tilt=-1)

    # Dagorlad: the ash plain, warmest under the gate
    sc.ridge(272, 3, [(1.3, 1), (3.7, .6)], sc.lin("plaing", [(0, P["plain_far"]), (.35, P["plain"]), (1, P["bg"])]), seed=3.3)
    sc.add(f'<ellipse cx="736" cy="280" rx="420" ry="36" fill="{sc.rad("plainglow", [(0, P["glow"], .22), (1, P["glow"], 0)])}"/>')
    # the road from the plain to the gate, and a fainter track east
    road = "M736,274 C720,292 650,304 560,318 C440,336 300,352 120,380"
    sc.add(f'<path d="{road}" fill="none" stroke="{P["road_edge"]}" stroke-width="12" stroke-linecap="round"/><path d="{road}" fill="none" stroke="{P["road"]}" stroke-width="8" stroke-linecap="round" opacity=".9"/>')
    sc.add(f'<path d="M736,274 C760,290 840,300 960,312 C1080,324 1240,340 1500,368" fill="none" stroke="{P["road"]}" stroke-width="5" stroke-linecap="round" opacity=".5"/>')

    # foul pools catching the fire in the sky
    for i, (x, y, rx, ry) in enumerate([(470, 290, 40, 4.5), (884, 293, 48, 5), (240, 298, 56, 5.5), (1210, 286, 44, 4), (1440, 292, 60, 5), (60, 288, 34, 4), (640, 312, 28, 4)]):
        pool(sc, x, y, rx, ry, f"pool{i}")

    # slag heaps, some still smoking
    heaps = [(150, 302, 70, 26), (346, 288, 46, 18), (1110, 292, 56, 20), (1330, 300, 84, 32), (1550, 290, 60, 22), (430, 322, 60, 20), (990, 332, 66, 18), (30, 334, 72, 24), (590, 296, 34, 12)]
    for i, (x, y, w, h) in enumerate(heaps):
        d = f"M{f(x - w)},{f(y)} C{f(x - w * .6)},{f(y - h * .4)} {f(x - w * .35)},{f(y - h)} {f(x - w * .05)},{f(y - h)} C{f(x + w * .3)},{f(y - h * 1.02)} {f(x + w * .55)},{f(y - h * .45)} {f(x + w)},{f(y)}Z"
        ls = 1 if x < 735 else -1
        sc.add(f'<path d="{d}" fill="{P["slag"]}"/>')
        # rim light on the side facing the gate
        sx = x - w * .05
        sc.add(f'<path d="M{f(sx)},{f(y - h)} C{f(x + ls * w * .3)},{f(y - h)} {f(x + ls * w * .55)},{f(y - h * .45)} {f(x + ls * w)},{f(y)} Q{f(x + ls * w * .4)},{f(y - h * .45)} {f(sx)},{f(y - h)}Z" fill="{P["slag_lit"]}" opacity=".6"/>')
        # ridges of clinker running down the heap
        for k in range(4):
            t = sc.r(-.6, .6)
            sc.add(f'<path d="M{f(x + t * w * .4)},{f(y - h * .85)} q{f(t * w * .3)},{f(h * .4)} {f(t * w * .7)},{f(h * .8)}" stroke="{P["slag_dark"]}" stroke-width="1.2" fill="none"/>')
        if i in (0, 3, 2):
            sc.smoke(x, y - h - 2, 11, "#6a584a", .3, .9 if x < 735 else -.9)
    # pits and old craters
    for x, y, rx in [(300, 312, 22), (700, 332, 18), (860, 320, 26), (1250, 320, 24), (180, 346, 30), (1460, 334, 28)]:
        sc.add(f'<ellipse cx="{x}" cy="{y}" rx="{f(rx + 4)}" ry="{f(rx * .22 + 2)}" fill="#3a2e24"/><ellipse cx="{x}" cy="{f(y + 1)}" rx="{rx}" ry="{f(rx * .2)}" fill="{P["plain_dark"]}"/>')
    # rows of stakes before the gate
    g = []
    for row, (y, x0, x1) in enumerate([(286, 560, 700), (284, 780, 920), (300, 520, 640), (298, 840, 960)]):
        x = x0
        while x < x1:
            hh = sc.r(6, 11)
            lean = sc.r(-3, 3)
            g.append(f'<path d="M{f(x)},{f(y)} l{f(lean)},{f(-hh)}" stroke="#0f0c0a" stroke-width="1.4" stroke-linecap="round"/>')
            x += sc.r(6, 10)
    sc.add("".join(g))
    # broken rocks strewn on the plain
    for _ in range(90):
        x = sc.r(-10, W + 10)
        y = sc.r(280, 360)
        s = sc.r(1.5, 4) * (1 + (y - 280) / 80)
        sc.add(f'<path d="M{f(x - s)},{f(y)} L{f(x - s * .4)},{f(y - s * .9)} L{f(x + s * .5)},{f(y - s * .7)} L{f(x + s)},{f(y)}Z" fill="{sc.rnd.choice(["#1d1712", "#241d17", "#30271f"])}"/>')

    # foreground swell fading to the page
    sc.ridge(350, 6, [(1.6, 1), (4.2, .4)], sc.lin("fg", [(0, "#1e1914"), (1, P["bg"])]), seed=5.1)
    sc.tufts(352, 400, 160, ["#2a231c", "#241e18", "#1f1a14"], 4, 10)

    # ash falling, embers lifting
    g = [f'<g fill="{P["ash"]}">']
    for _ in range(520):
        y = sc.r(0, 330)
        g.append(f'<circle cx="{f(sc.r(0, W))}" cy="{f(y)}" r="{f(sc.r(.5, 1.4))}" opacity="{f(sc.r(.12, .45))}"/>')
    g.append("</g>")
    sc.add("".join(g))
    g = [f'<g fill="{P["ash"]}">']
    for _ in range(60):  # nearer flakes, larger and tumbling
        x, y, rr = sc.r(0, W), sc.r(10, 320), sc.r(1.4, 2.4)
        g.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rr)}" ry="{f(rr * .55)}" transform="rotate({f(sc.r(-40, 40))} {f(x)} {f(y)})" opacity="{f(sc.r(.18, .4))}"/>')
    g.append("</g>")
    sc.add("".join(g))
    g = [f'<g fill="{P["ember"]}">']
    for _ in range(60):
        x = 735 + sc.r(-260, 260)
        y = sc.r(120, 280)
        g.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(sc.r(.6, 1.4))}" opacity="{f(sc.r(.4, .9))}"/>')
    g.append("</g>")
    sc.add("".join(g))
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build().save(f"{out}/blackgate.svg", "The Black Gate")
