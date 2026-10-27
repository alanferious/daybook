"""Bree in the rain: a wet autumn evening at the crossroads village.

The village climbs the side of Bree-hill: timber-framed houses with steep roofs
and lamplit windows, a few hobbit-holes high on the slope, the three-storey
Prancing Pony with its hanging sign and lit stable-yard arch, the village
hedge with the West-gate and its lantern, the Chetwood dark beyond, slanting
rain, and the wet Road shining with puddles of lamplight.
"""
import math
import sys
from scene_kit import Scene, W, H, f

P = dict(
    sky=[(0, "#100e10"), (.35, "#1d1918"), (.62, "#2f2622"), (.8, "#46362a"), (1, "#3a2d22")],
    cloud="#2a2320", cloud_shade="#18140f", cloud_low="#3a2e27",
    far1="#2e2620", far2="#28211b", haze="#4a3a2e",
    wood_far="#18150f", wood="#14120d", wood_shade="#0f0d0a",
    hill="#2a2419", hill_light="#332b1e", hill_shade="#1f1a12",
    wall=["#56473a", "#5d4c3d", "#4f4236", "#635242"], wall_shade="#3f3429", stone="#4f473e", stone_shade="#383129",
    timber="#1e150e", roof=["#352a22", "#3b3029", "#2f2a28", "#43352a"], roof_wet="#6a5c50",
    lamp="#e8a957", lamp_core="#ffd88f", dark_win="#18120c",
    hedge="#1d1a11", hedge_shade="#14120c", ground="#211910", road="#33281d", road_edge="#2a2017",
    puddle="#4a3e33", rain="#b5a68f", smoke="#6a5d52", bg="#1e1710",
)


def glow_def(sc):
    sc.rad("glow", [(0, "#ffd08a", .55), (.35, P["lamp"], .22), (1, P["lamp"], 0)])


def glow(sc, x, y, rr, op=1.0):
    sc.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" fill="url(#glow)" opacity="{f(op)}"/>')


def window(sc, x, y, w, h, lit, tim):
    """A small leaded window; lit ones are warm with a cross mullion."""
    if lit:
        sc.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{P["lamp"]}"/>'
               f'<rect x="{f(x + w * .2)}" y="{f(y + h * .2)}" width="{f(w * .6)}" height="{f(h * .55)}" fill="{P["lamp_core"]}" opacity=".7"/>'
               f'<path d="M{f(x + w / 2)},{f(y)} V{f(y + h)} M{f(x)},{f(y + h * .45)} H{f(x + w)}" stroke="{tim}" stroke-width="{f(max(.6, w * .12))}"/>')
    else:
        sc.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{P["dark_win"]}"/>')


def roof_y(kind, xt, wt, ytop, roof, o, x):
    if kind == "gable":
        half = wt / 2 + o
        return ytop - roof * max(0, 1 - abs(x - (xt + wt / 2)) / half)
    return ytop - roof


def house(sc, x, base, w, storeys, sh, roof, kind="gable", lit=.6, jetty=0, s=1.0, chim=.72, door=True,
          wall=None, roofc=None, braces=True, glow_op=1.0, smoke=True, stone_ground=False):
    """A timber-framed house standing on the ground at `base`, left edge x, width w.
    kind: 'gable' shows the gable end; 'side' shows the long side under a steep roof."""
    rnd = sc.rnd
    wall = wall or rnd.choice(P["wall"])
    roofc = roofc or rnd.choice(P["roof"])
    tim = P["timber"]
    tw = max(.8, 1.7 * s)
    lights = []
    xt = wt = ytop = None
    for i in range(storeys):
        xi, wi = x - jetty * i, w + 2 * jetty * i
        y0 = base - (i + 1) * sh
        fill = P["stone"] if (stone_ground and i == 0) else wall
        g = [f'<rect x="{f(xi)}" y="{f(y0)}" width="{f(wi)}" height="{f(sh)}" fill="{fill}"/>']
        if not (stone_ground and i == 0):
            nb = max(1, round(wi / (15 * s)))
            d = ""
            for b in range(nb + 1):
                d += f"M{f(xi + wi * b / nb)},{f(y0)}V{f(y0 + sh)}"
            if braces:
                for b in range(nb):
                    if rnd.random() < .45:
                        ax = xi + wi * b / nb
                        bx = xi + wi * (b + 1) / nb
                        if rnd.random() < .5:
                            ax, bx = bx, ax
                        d += f"M{f(ax)},{f(y0 + sh)}L{f(bx)},{f(y0 + sh * .45)}"
            g.append(f'<path d="{d}" stroke="{tim}" stroke-width="{f(tw)}"/>')
        else:
            d = "".join(f"M{f(xi + k * 7 * s + (3 * s if r2 % 2 else 0))},{f(y0 + sh * (r2 + 1) / 4)}h{f(4 * s)}" for r2 in range(3) for k in range(int(wi / (7 * s))))  # stone coursing
            g.append(f'<path d="{d}" stroke="{P["stone_shade"]}" stroke-width="{f(.8 * s)}"/>')
        g.append(f'<path d="M{f(xi - .5)},{f(y0)} H{f(xi + wi + .5)}" stroke="{tim}" stroke-width="{f(tw * 1.4)}"/>')
        sc.add("".join(g))
        # windows
        ww, wh = 6 * s, 8 * s
        n = max(1, int(wi / (17 * s)))
        for k in range(n):
            cx = xi + wi * (k + .5) / n
            if i == 0 and door and n >= 2 and k == n // 2:
                continue
            on = rnd.random() < lit
            window(sc, cx - ww / 2, y0 + sh * .3, ww, wh, on, tim)
            if on:
                lights.append((cx, y0 + sh * .3 + wh / 2, ww))
        xt, wt, ytop = xi, wi, y0
    if door:
        dx = x + w / 2 if storeys == 1 or int(w / (17 * s)) < 2 else x + w * (int(w / (17 * s)) // 2 + .5) / int(w / (17 * s))
        dw, dh = 7 * s, 12 * s
        on = rnd.random() < .35
        sc.add(f'<rect x="{f(dx - dw / 2)}" y="{f(base - dh)}" width="{f(dw)}" height="{f(dh)}" fill="{P["lamp"] if on else "#1a120b"}"/>'
               f'<rect x="{f(dx - dw / 2 - 1)}" y="{f(base - dh - 1.2)}" width="{f(dw + 2)}" height="{f(1.6 * s)}" fill="{tim}"/>')
        if on:
            lights.append((dx, base - dh / 2, dw * 1.2))
    # roof
    o = 3.5 * s
    if kind == "gable":
        d = f"M{f(xt - o)},{f(ytop + 1)} L{f(xt + wt / 2)},{f(ytop - roof)} L{f(xt + wt + o)},{f(ytop + 1)}Z"
        shade = f"M{f(xt + wt / 2)},{f(ytop - roof)} L{f(xt + wt + o)},{f(ytop + 1)} L{f(xt + wt / 2)},{f(ytop + 1)}Z"
        sc.add(f'<path d="{d}" fill="{wall}"/>')  # gable wall
        inner = f"M{f(xt + 2 * s)},{f(ytop)} L{f(xt + wt / 2)},{f(ytop - roof + 5 * s)} L{f(xt + wt - 2 * s)},{f(ytop)}"
        sc.add(f'<path d="{inner}" fill="none" stroke="{tim}" stroke-width="{f(tw)}"/>'
               f'<path d="M{f(xt + wt / 2)},{f(ytop)} V{f(ytop - roof + 6 * s)}" stroke="{tim}" stroke-width="{f(tw)}"/>')
        if roof > 16 * s:
            on = rnd.random() < lit
            window(sc, xt + wt / 2 - 2.5 * s - 3.5 * s, ytop - roof * .45, 5 * s, 6 * s, on, tim)
            if on:
                lights.append((xt + wt / 2 - 3.5 * s, ytop - roof * .45 + 3 * s, 5 * s))
        # bargeboards: the roof seen edge-on as a thick dark rim
        sc.add(f'<path d="M{f(xt - o)},{f(ytop + 1)} L{f(xt + wt / 2)},{f(ytop - roof)} L{f(xt + wt + o)},{f(ytop + 1)}" fill="none" stroke="{roofc}" stroke-width="{f(4 * s)}" stroke-linejoin="round"/>'
               f'<path d="M{f(xt - o + 1)},{f(ytop - 1)} L{f(xt + wt / 2)},{f(ytop - roof - 1.6 * s)}" fill="none" stroke="{P["roof_wet"]}" stroke-width="{f(.9 * s)}" opacity=".7"/>')
    else:
        inset = wt * .1
        d = f"M{f(xt - o)},{f(ytop + 1)} L{f(xt + inset)},{f(ytop - roof)} L{f(xt + wt - inset)},{f(ytop - roof)} L{f(xt + wt + o)},{f(ytop + 1)}Z"
        sc.add(f'<path d="{d}" fill="{roofc}"/>'
               f'<path d="M{f(xt + wt - inset)},{f(ytop - roof)} L{f(xt + wt + o)},{f(ytop + 1)} L{f(xt + wt - inset - roof * .2)},{f(ytop + 1)}Z" fill="#000" opacity=".25"/>'
               f'<path d="M{f(xt + inset)},{f(ytop - roof)} H{f(xt + wt - inset)}" stroke="{P["roof_wet"]}" stroke-width="{f(1.1 * s)}" opacity=".75"/>')
        # wet sheen streaks down the roof
        d = "".join(f"M{f(xt + inset + 4 * s + k * 9 * s)},{f(ytop - roof + 2)}l{f(-1.2 * s)},{f(roof - 3)}" for k in range(int(wt / (9 * s))))
        sc.add(f'<path d="{d}" stroke="{P["roof_wet"]}" stroke-width=".7" opacity=".28"/>')
    # chimney
    if chim is not None:
        cx = xt + wt * chim
        ry = roof_y(kind, xt, wt, ytop, roof, o, cx)
        cw = 5 * s
        sc.add(f'<rect x="{f(cx - cw / 2)}" y="{f(ry - 9 * s)}" width="{f(cw)}" height="{f(10 * s)}" fill="{P["stone_shade"]}"/>'
               f'<rect x="{f(cx - cw / 2 - .8 * s)}" y="{f(ry - 10 * s)}" width="{f(cw + 1.6 * s)}" height="{f(1.8 * s)}" fill="{P["stone"]}"/>')
        if smoke:
            sc.smoke(cx, ry - 13 * s, 6, P["smoke"], .28, -1.3 * s)
    for lx, ly, lw in lights:
        glow(sc, lx, ly, lw * 3.2, glow_op)
    return xt, wt, ytop


def lantern(sc, x, y, s=1.0):
    sc.add(f'<rect x="{f(x - 3 * s)}" y="{f(y - 5 * s)}" width="{f(6 * s)}" height="{f(9 * s)}" fill="{P["lamp_core"]}"/>'
           f'<path d="M{f(x - 4 * s)},{f(y - 5 * s)} L{f(x)},{f(y - 9 * s)} L{f(x + 4 * s)},{f(y - 5 * s)}Z" fill="{P["timber"]}"/>'
           f'<rect x="{f(x - 3.6 * s)}" y="{f(y + 4 * s)}" width="{f(7.2 * s)}" height="{f(1.6 * s)}" fill="{P["timber"]}"/>'
           f'<path d="M{f(x)},{f(y - 5 * s)} V{f(y + 4 * s)}" stroke="{P["timber"]}" stroke-width="{f(.8 * s)}"/>')
    glow(sc, x, y, 34 * s, 1)
    glow(sc, x, y, 12 * s, 1)


def hobbit_hole(sc, x, y, s, flip=1):
    """A hole dug into the hillside: a turf bank, a round door, a lit round window beside it."""
    wx = x + flip * 9 * s
    sc.add(f'<ellipse cx="{f(x + flip * 4 * s)}" cy="{f(y + 5 * s)}" rx="{f(16 * s)}" ry="{f(7 * s)}" fill="#2e271b"/>'
           f'<path d="M{f(x - 4.6 * s)},{f(y + 5 * s)} V{f(y)} A{f(4.6 * s)},{f(4.6 * s)} 0 0 1 {f(x + 4.6 * s)},{f(y)} V{f(y + 5 * s)}Z" fill="{P["stone_shade"]}"/>'
           f'<path d="M{f(x - 3.4 * s)},{f(y + 5 * s)} V{f(y)} A{f(3.4 * s)},{f(3.4 * s)} 0 0 1 {f(x + 3.4 * s)},{f(y)} V{f(y + 5 * s)}Z" fill="#2a1a10"/>'
           f'<circle cx="{f(wx)}" cy="{f(y)}" r="{f(2.8 * s)}" fill="{P["lamp"]}"/>'
           f'<path d="M{f(wx - 2.8 * s)},{f(y)} H{f(wx + 2.8 * s)} M{f(wx)},{f(y - 2.8 * s)} V{f(y + 2.8 * s)}" stroke="{P["timber"]}" stroke-width="{f(.7 * s)}"/>')
    glow(sc, wx, y, 12 * s, .8)


def pony_sign(sc, x, y, s=1.0):
    """A board hanging from chains, painted with a white pony rearing."""
    w, h = 26 * s, 20 * s
    sc.add(f'<path d="M{f(x + 3 * s)},{f(y - 7 * s)} V{f(y)} M{f(x + w - 3 * s)},{f(y - 7 * s)} V{f(y)}" stroke="#2c241c" stroke-width="{f(.8 * s)}"/>'
           f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(1.5 * s)}" fill="#4a2d1c"/>'
           f'<rect x="{f(x + 1.6 * s)}" y="{f(y + 1.6 * s)}" width="{f(w - 3.2 * s)}" height="{f(h - 3.2 * s)}" fill="none" stroke="#b08a4a" stroke-width="{f(.9 * s)}"/>')
    # rearing pony, facing right, drawn in sign-local units (0..26 x 0..20)
    pts = [(7, 17), (8.5, 12), (8, 9), (10, 7.5), (13, 7), (15.5, 4.8), (17.3, 3.6), (19.2, 4.2), (19.6, 5.4), (18.2, 5.8),
           (17.4, 7.6), (19.6, 8.4), (20.6, 10.4), (19.6, 10.8), (17.6, 9.6), (15.6, 10.2), (14.2, 12.2), (14.8, 16.8), (13.6, 17),
           (12.6, 13.2), (11, 13.6), (10.2, 17), (9, 17.2), (9.6, 13), (7.8, 15.6), (6, 15.8), (7.2, 13.4)]
    d = "M" + " L".join(f"{f(x + px * s)},{f(y + py * s)}" for px, py in pts) + "Z"
    sc.add(f'<path d="{d}" fill="#efe6d4"/><path d="M{f(x + 15.2 * s)},{f(y + 5.4 * s)} l{f(-1.5 * s)},{f(2.6 * s)} l{f(-1.6 * s)},{f(-.2 * s)}" fill="none" stroke="#2c241c" stroke-width="{f(.7 * s)}"/>')


def dark_tree(sc, x, y, s, fill, top=None):
    """A night silhouette of a broadleaf tree: a trunk and a few lumps of canopy."""
    g = [f'<path d="M{f(x - s * .06)},{f(y)} L{f(x - s * .03)},{f(y - s * .7)} L{f(x + s * .03)},{f(y - s * .7)} L{f(x + s * .07)},{f(y)}Z" fill="{fill}"/>']
    for dx, dy, rr in [(-.32, -.9, .36), (.3, -.95, .38), (0, -1.2, .45), (-.12, -.78, .4), (.18, -.72, .3)]:
        g.append(f'<circle cx="{f(x + dx * s + sc.r(-.05, .05) * s)}" cy="{f(y + dy * s)}" r="{f(rr * s * sc.r(.9, 1.1))}" fill="{fill}"/>')
    if top:
        g.append(f'<circle cx="{f(x - s * .1)}" cy="{f(y - s * 1.35)}" r="{f(s * .22)}" fill="{top}"/>')
    sc.add("".join(g))


def ceiling(sc, base, amp, fill, seed, step=10, op=1.0):
    """A low ragged cloud deck hanging from the top of the sky, its underside scalloped."""
    pts = []
    x = -30
    while x <= W + 30:
        y = base + amp * (math.sin(x / 131 + seed) + .5 * math.sin(x / 53 + seed * 2.3))
        y += amp * .9 * abs(math.sin(x / 29 + seed * 3)) ** .6 * (.6 + .4 * math.sin(x / 71 + seed))  # bellies hanging from the deck
        pts.append((x, y))
        x += step
    d = "M-30,-10 L" + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + f" L{W + 30},-10Z"
    sc.add(f'<path d="{d}" fill="{fill}" opacity="{op}"/>')
    return pts


def rain(sc, n, y0, y1, length, op, width, col=None, x0=-40, x1=W + 40, slant=.28):
    d = []
    for _ in range(n):
        x, y = sc.r(x0, x1), sc.r(y0, y1)
        ln = length * sc.r(.6, 1.2)
        d.append(f"M{x:.0f},{y:.0f}l{-ln * slant:.0f},{ln:.0f}")
    sc.add(f'<path d="{"".join(d)}" stroke="{col or P["rain"]}" stroke-width="{width}" stroke-linecap="round" opacity="{op}"/>')


def build(seed=29):
    sc = Scene(seed)
    glow_def(sc)
    sc.sky(sc.lin("sky", P["sky"]))
    # a last smear of evening light low in the west, under the cloud
    sc.add(f'<ellipse cx="220" cy="210" rx="420" ry="70" fill="{sc.rad("west", [(0, "#7a5a3c", .45), (.5, "#5a4230", .2), (1, "#5a4230", 0)])}"/>')
    # the cloud ceiling: low, heavy, ragged, faintly lit from beneath by the village
    ceiling(sc, 112, 14, sc.lin("deck3", [(0, P["cloud_low"], .7), (.75, P["cloud_low"], .45), (1, P["cloud_low"], 0)]), 1.3)
    ceiling(sc, 84, 16, sc.lin("deck2", [(0, P["cloud_shade"]), (.8, P["cloud"]), (1, "#3a2e27")]), 2.9)
    ceiling(sc, 46, 14, sc.lin("deck1", [(0, "#0e0c0c"), (1, P["cloud_shade"])]), 4.4)
    for cx, cy, s in [(300, 98, 34), (690, 72, 30), (1020, 104, 36), (1380, 86, 30)]:  # torn scud below the deck
        sc.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{s * 2.6}" ry="{s * .28}" fill="{P["cloud_low"]}" opacity=".5"/>'
               f'<ellipse cx="{cx + s}" cy="{cy - 5}" rx="{s * 1.4}" ry="{s * .22}" fill="{P["cloud_low"]}" opacity=".45"/>')
    # rain curtains trailing from the cloud
    for cx, wdt in [(120, 160), (430, 110), (1180, 140), (1450, 190)]:
        sc.add(f'<path d="M{cx},70 L{cx + wdt},70 L{cx + wdt - 70},250 L{cx - 70},250Z" fill="{sc.lin(f"cur{cx}", [(0, P["rain"], 0), (.4, P["rain"], .08), (1, P["rain"], 0)])}"/>')

    # far country: the Barrow-downs and the Road west, lost in rain
    sc.ridge(214, 10, [(1.1, 1), (2.7, .5), (6.1, .2)], P["far1"], seed=0.7)
    sc.add(f'<rect y="180" width="{W}" height="80" fill="{sc.lin("haze1", [(0, P["haze"], 0), (1, P["haze"], .5)])}"/>')

    # the Chetwood, dark on the rising ground east of the village
    wood = sc.ridge(196, 12, [(1.4, 1), (3.3, .4)], P["wood_far"], seed=3.1, x0=880, x1=W + 40, taper=140)
    for x in range(900, W + 30, 9):
        y = sc.y_at(wood, x) + 4
        if sc.r(0, 1) < .55:
            sc.conifer(x + sc.r(-4, 4), y + 6, sc.r(9, 17), P["wood_far"], P["wood_shade"])
        else:
            rr = sc.r(9, 16)
            sc.add(f'<circle cx="{f(x)}" cy="{f(y - rr * .6)}" r="{f(rr)}" fill="{P["wood_far"]}"/>')
    for x in range(1120, W + 30, 16):  # a nearer rank of tall trees at the wood's edge
        y = sc.y_at(wood, x) + 40
        if sc.r(0, 1) < .6:
            sc.conifer(x, y, sc.r(16, 26), P["wood"], P["wood_shade"])
        else:
            dark_tree(sc, x, y, sc.r(24, 34), P["wood"])
    sc.add(f'<rect x="860" y="150" width="{W}" height="110" fill="{sc.lin("haze2", [(0, P["haze"], 0), (1, P["haze"], .22)])}"/>')

    # Bree-hill, the village climbing its western side
    # the outlying fields first, west of the hill, with a farm or two and their trees
    fields = sc.ridge(246, 5, [(1.6, 1), (3.9, .4)], "#2a2219", seed=1.9, x0=-20, x1=700)
    for x in range(-10, 700, 30):  # hedgerows along the far fields
        dark_tree(sc, x + sc.r(-6, 6), sc.y_at(fields, x) + 4, sc.r(8, 13), "#221d16")
    hill = []
    for x in range(-20, W + 21, 8):
        t = (x - 700) / 560
        hill.append((x, 268 - 166 * max(0, 1 - t * t) ** 1.35 + 5 * math.sin(x / 41) + 3 * math.sin(x / 17)))
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in hill) + f" L{W + 20},{H} L-20,{H}Z"
    sc.add(f'<path d="{d}" fill="{sc.lin("hillg", [(0, P["hill_shade"]), (.4, P["hill_light"]), (1, P["hill_shade"])], x2=1, y2=0)}"/>')
    # an outlying farm on the lower slope west of the village, and its trees
    house(sc, 200, sc.y_at(hill, 215) + 8, 34, 1, 15, 17, "side", lit=1, s=.62, door=False)
    house(sc, 238, sc.y_at(hill, 245) + 9, 18, 1, 12, 13, "gable", lit=0, s=.55, door=False, chim=None)
    for x, s in [(28, 32), (88, 24), (160, 36), (290, 28), (330, 22)]:
        dark_tree(sc, x, sc.y_at(hill, x) + 10, s, "#1b1711")
    # trees crowning the hill
    for x in range(560, 860, 12):
        y = sc.y_at(hill, x) + 8
        dark_tree(sc, x + sc.r(-4, 4), y, sc.r(14, 21), "#1a1711")
    # terraces, lanes and garden walls stepping up the slope
    for a0, a1, dy in [(420, 640, 46), (760, 1010, 42), (470, 700, 82), (740, 1060, 86), (360, 560, 120)]:
        pts = [(x, sc.y_at(hill, x) + dy) for x in range(a0, a1, 6)]
        sc.add('<path d="M' + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + f'" fill="none" stroke="{P["hill_shade"]}" stroke-width="3"/>')
        sc.add('<path d="M' + " L".join(f"{f(a)},{f(b - 2)}" for a, b in pts) + f'" fill="none" stroke="#4a3d2c" stroke-width=".8" opacity=".6"/>')
    # hobbit-holes high on the hill, round windows lit
    for x, dy, s, fl in [(606, 24, 1, 1), (652, 28, .9, -1), (870, 28, .95, 1), (912, 36, .9, -1)]:
        hobbit_hole(sc, x, sc.y_at(hill, x) + dy, s, fl)

    # upper village: small houses on the slope, far off
    upper = [(452, 236, 26, 1, 15, "gable"), (498, 221, 30, 2, 12, "side"), (548, 200, 24, 2, 11, "gable"),
             (590, 186, 28, 1, 13, "side"), (700, 166, 24, 2, 11, "gable"), (742, 178, 30, 1, 13, "side"),
             (812, 176, 26, 2, 11, "gable"), (930, 196, 30, 2, 12, "side"), (978, 212, 24, 1, 14, "gable"),
             (1020, 226, 30, 2, 12, "side"), (1080, 238, 26, 2, 12, "gable"), (642, 202, 26, 1, 13, "gable"),
             (868, 194, 28, 1, 13, "side")]
    for k, (x, b, w, st, sh, kind) in enumerate(upper):
        house(sc, x, b, w, st, sh, sh * 1.25, kind, lit=.55, s=.55, door=False, braces=True, smoke=k % 2 == 0)
    sc.add(f'<rect y="150" width="{W}" height="120" fill="{sc.lin("haze3", [(0, P["haze"], 0), (1, P["haze"], .16)])}"/>')
    # middle village
    mid = [(470, 268, 44, 2, 17, "side"), (520, 258, 34, 2, 17, "gable"), (580, 244, 42, 2, 16, "side"),
           (636, 236, 32, 2, 16, "gable"), (962, 246, 40, 2, 16, "gable"), (1012, 254, 46, 2, 16, "side"),
           (1066, 262, 36, 2, 17, "gable"), (1118, 250, 44, 2, 15, "side"), (1176, 258, 34, 1, 18, "gable")]
    for x, b, w, st, sh, kind in mid:
        house(sc, x, b, w, st, sh, sh * 1.3, kind, lit=.6, s=.75, door=False)
    # lower village, along the Road
    lower = [(560, 292, 50, 2, 22, "gable"), (618, 290, 48, 2, 20, "side"), (920, 294, 52, 2, 22, "side"),
             (980, 294, 40, 2, 21, "gable"), (1030, 296, 56, 2, 21, "side")]
    for x, b, w, st, sh, kind in lower:
        house(sc, x, b, w, st, sh, sh * 1.25, kind, lit=.65, s=1.0, jetty=2)

    # the Prancing Pony: three storeys, jettied, with a wing and the stable-yard arch
    ix, ib = 690, 298
    # the wing running back on the right, with the arch into the yard
    wx0, ww = 868, 70
    sc.add(f'<rect x="{wx0}" y="{ib - 64}" width="{ww}" height="64" fill="{P["wall"][2]}"/>')
    for k in range(6):
        sc.add(f'<path d="M{wx0 + k * 14},{ib - 64} V{ib}" stroke="{P["timber"]}" stroke-width="1.7"/>')
    sc.add(f'<path d="M{wx0},{ib - 32} H{wx0 + ww}" stroke="{P["timber"]}" stroke-width="2.4"/>')
    sc.add(f'<path d="M{wx0 - 4},{ib - 63} L{wx0 + 8},{ib - 92} L{wx0 + ww - 6},{ib - 92} L{wx0 + ww + 5},{ib - 63}Z" fill="{P["roof"][1]}"/>'
           f'<path d="M{wx0 + 8},{ib - 92} H{wx0 + ww - 6}" stroke="{P["roof_wet"]}" stroke-width="1.1"/>')
    for k in range(4):
        window(sc, wx0 + 8 + k * 16, ib - 56, 6, 8, k != 2, P["timber"])
        if k != 2:
            glow(sc, wx0 + 11 + k * 16, ib - 52, 20)
    ax, aw, ah = wx0 + 35, 30, 30  # the arch
    arch = f"M{ax - aw / 2},{ib} V{ib - ah + aw / 2} A{aw / 2},{aw / 2} 0 0 1 {ax + aw / 2},{ib - ah + aw / 2} V{ib}Z"
    sc.add(f'<path d="{arch}" fill="{sc.lin("yard", [(0, "#f2b866"), (.6, "#c47e3c"), (1, "#6a4224")])}"/>')
    sc.add(f'<path d="M{ax - aw / 2 + 3},{ib - 6} h{aw - 6}" stroke="#7a5030" stroke-width="2"/>'
           f'<rect x="{ax + 3}" y="{ib - 18}" width="8" height="12" fill="#5a3a22"/><rect x="{ax - 10}" y="{ib - 14}" width="6" height="8" fill="#5a3a22"/>')  # cart and barrel in the yard
    sc.add(f'<path d="{arch}" fill="none" stroke="{P["stone"]}" stroke-width="3.2"/>')
    lantern(sc, ax, ib - ah + 8, .7)
    # the main house
    xt, wt, ytop = house(sc, ix, ib, 178, 3, 34, 50, "side", lit=.85, jetty=3, s=1.15, chim=None, door=False, wall="#635242", roofc="#3b3029", stone_ground=True)
    for cx in (ix + 28, ix + 152):  # tall chimneys
        sc.add(f'<rect x="{cx - 4}" y="{ytop - 62}" width="9" height="20" fill="{P["stone_shade"]}"/><rect x="{cx - 5}" y="{ytop - 64}" width="11" height="3" fill="{P["stone"]}"/>')
        sc.smoke(cx, ytop - 70, 8, P["smoke"], .32, -1.5)
    for dxp in (40, 89, 138):  # dormers
        dx = ix + dxp
        sc.add(f'<rect x="{dx - 9}" y="{ytop - 30}" width="18" height="16" fill="#635242"/>'
               f'<path d="M{dx - 12},{ytop - 29} L{dx},{ytop - 42} L{dx + 12},{ytop - 29}Z" fill="#3b3029"/>'
               f'<path d="M{dx - 12},{ytop - 29} L{dx},{ytop - 42} L{dx + 12},{ytop - 29}" fill="none" stroke="{P["roof_wet"]}" stroke-width=".9" opacity=".7"/>')
        window(sc, dx - 4, ytop - 26, 8, 9, dxp != 138, P["timber"])
        if dxp != 138:
            glow(sc, dx, ytop - 21, 22)
    # front door, steps and the lamp over it
    dx = ix + 89
    sc.add(f'<rect x="{dx - 9}" y="{ib - 24}" width="18" height="24" fill="#f0b765"/><rect x="{dx - 6}" y="{ib - 20}" width="8" height="20" fill="#3a2414" opacity=".75"/>'
           f'<rect x="{dx - 11}" y="{ib - 26}" width="22" height="3" fill="{P["timber"]}"/>'
           f'<rect x="{dx - 16}" y="{ib - 2}" width="32" height="3" fill="{P["stone"]}"/><rect x="{dx - 20}" y="{ib + 1}" width="40" height="3" fill="{P["stone_shade"]}"/>')
    glow(sc, dx, ib - 12, 40)
    lantern(sc, dx + 22, ib - 30, .8)
    # the hanging sign on its bracket at the corner
    sx, sy = ix - 3, ib - 46
    sc.add(f'<path d="M{sx},{sy} H{sx - 36} M{sx},{sy + 12} L{sx - 16},{sy}" stroke="#1c140d" stroke-width="2.4" fill="none"/>'
           f'<circle cx="{sx - 36}" cy="{sy}" r="1.6" fill="#1c140d"/>')
    pony_sign(sc, sx - 40, sy + 7, 1.15)
    glow(sc, sx - 25, sy + 18, 30, .55)

    # the gatekeeper's lodge just inside the West-gate
    house(sc, 372, 290, 46, 1, 22, 22, "gable", lit=1, s=.9, chim=.3, door=False)

    # ground in front of the village, sloping down to the hedge
    sc.ridge(296, 3, [(1.3, 1), (3.1, .4)], P["ground"], seed=9.1)
    # the Road: in at the West-gate, along the front of the Pony and away east
    road = "M300,410 C380,360 430,322 470,306 C520,296 600,300 700,300 C900,302 1200,300 1620,296 L1620,312 C1200,316 900,318 700,316 C600,316 540,318 500,328 C460,342 440,380 420,410Z"
    sc.add(f'<path d="{road}" fill="{P["road"]}"/>')
    sc.add(f'<path d="M470,306 C520,296 600,300 700,300 C900,302 1200,300 1620,296" fill="none" stroke="{P["road_edge"]}" stroke-width="2"/>')
    # puddles, each holding a smear of lamplight
    for px, py, rx, ry, refl in [(560, 307, 26, 3.2, 600), (780, 307, 34, 3.6, 779), (720, 306, 14, 2.4, None), (900, 307, 22, 3, 903),
                                 (1000, 306, 28, 3, 1001), (468, 330, 22, 3.6, 468), (440, 356, 30, 4.4, 452), (1120, 305, 26, 2.8, None),
                                 (660, 309, 18, 2.6, 660), (1300, 303, 30, 2.8, None)]:
        sc.add(f'<ellipse cx="{px}" cy="{py}" rx="{rx}" ry="{ry}" fill="{P["puddle"]}"/>')
        sc.add(f'<ellipse cx="{px - rx * .3}" cy="{py - ry * .3}" rx="{f(rx * .5)}" ry="{f(ry * .35)}" fill="#6a5a4a" opacity=".5"/>')
        if refl:
            sc.add(f'<ellipse cx="{refl}" cy="{py}" rx="{f(min(rx * .35, 7))}" ry="{f(ry * .8)}" fill="{P["lamp"]}" opacity=".75"/>'
                   f'<ellipse cx="{refl}" cy="{py}" rx="{f(min(rx * .8, 16))}" ry="{f(ry * 1.4)}" fill="url(#glow)"/>')
        for k in range(2):  # rain rings
            rx2 = sc.r(2, 4)
            sc.add(f'<ellipse cx="{f(px + sc.r(-rx * .6, rx * .6))}" cy="{f(py + sc.r(-.5, .5))}" rx="{f(rx2)}" ry="{f(rx2 * .3)}" fill="none" stroke="#8a7a66" stroke-width=".6" opacity=".7"/>')
    # wet shine where lamplight lies along the road
    for x in [600, 780, 903, 1001, 1060, 422]:
        sc.add(f'<path d="M{x - 1},{299 if x > 470 else 300} v12" stroke="{P["lamp"]}" stroke-width="2" opacity=".25"/>')

    # the village hedge, with its dike, and the West-gate across the Road
    hl = [(x, 298 - 0.02 * (420 - x) + 2 * math.sin(x / 23)) for x in range(-20, 432, 9)]
    sc.add('<path d="M-20,312 ' + " ".join(f"L{f(a)},{f(b + 10)}" for a, b in hl) + f' L432,330 L-20,330Z" fill="{P["hedge_shade"]}"/>')
    sc.hedge(hl, 7, P["hedge"], P["hedge_shade"])
    hr = [(x, 322 + (x - 510) * .018 + 2 * math.sin(x / 19)) for x in range(512, W + 25, 12)]
    sc.hedge(hr, 9, P["hedge"], P["hedge_shade"])
    # hedge-sprigs catching the light
    sc.add("".join(f'<circle cx="{f(x)}" cy="{f(y - 5)}" r="1.4" fill="#3a3422" opacity=".8"/>' for x, y in hl[::3] + hr[::5]))
    # gateposts and the gate swung open
    for gx, top in [(430, 246), (510, 250)]:
        sc.add(f'<rect x="{gx - 5}" y="{top}" width="11" height="{334 - top}" fill="#2e2116"/><rect x="{gx - 7}" y="{top - 4}" width="15" height="5" fill="#3e2f21"/>'
               f'<path d="M{gx - 6},{top - 4} L{gx + .5},{top - 9} L{gx + 7},{top - 4}Z" fill="#3e2f21"/>'
               f'<path d="M{gx + 4},{top + 2} V332" stroke="#6a5642" stroke-width="1.1" opacity=".7"/>')
    # the gate itself, of bars, swung back against the hedge on the right
    g = []
    for k in range(5):
        g.append(f'M{515 + k * 9},{288 + k * .6} V{328 + k * .3}')
    g.append("M514,292 L556,294 M514,310 L556,311 M514,326 L556,326 M514,326 L556,294")
    sc.add(f'<path d="{" ".join(g)}" stroke="#2e2116" stroke-width="2.4" fill="none"/>')
    sc.add(f'<path d="M435,262 H456 M435,272 L447,262" stroke="#1c140d" stroke-width="2.2" fill="none"/><path d="M455,262 v4" stroke="#1c140d" stroke-width="1"/>')
    lantern(sc, 455, 275, 1.05)

    # foreground: wet grass falling away into the dark
    sc.ridge(352, 5, [(2.0, 1), (4.7, .4)], "#1e1710", seed=4.4)
    sc.tufts(340, 400, 90, ["#2a2216", "#251d13", "#30271a"], 6, 16)

    # the rain, in two depths, with streaks lit where it falls past the lamps
    rain(sc, 760, -20, 360, 16, .16, .7)
    rain(sc, 260, -20, 400, 30, .2, 1)
    for lx, ly, rr in [(455, 275, 42), (ax, ib - ah + 8, 26), (dx + 22, ib - 30, 34), (dx, ib - 12, 30)]:
        rain(sc, 18, ly - rr, ly + rr, 12, .55, .8, col=P["lamp_core"], x0=lx - rr * .8, x1=lx + rr * .8)
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build().save(f"{out}/bree.svg", "Bree in the rain")
