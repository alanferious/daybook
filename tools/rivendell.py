"""Rivendell: the Last Homely House on a golden autumn afternoon.

A deep, steep-sided valley: hazy blue mountains seen through its mouth, tall
cliffs on either hand with waterfalls dropping into mist, and in the middle a
rock spur stepped into terraces, carrying slender Elvish halls, towers, an
open round pavilion and a footbridge over the gorge. Amber, gold and rust
trees among dark pines; the Bruinen and its mist on the valley floor.
"""
import math
import re
import sys
from scene_kit import Scene, W, H, f

P = dict(
    sky=[(0, "#abb8d1"), (.42, "#d6d3d6"), (.75, "#efdfc2"), (1, "#f4e4c4")], sun="#fff0c6",
    cloud="#fbf5ea", cloud_shade="#e4d6c8",
    mtn="#bcc1d6", mtn_shade="#a8aec8", snow="#eef0f6", haze="#ece3d6",
    rock1="#c4b9bd", rock1_lit="#d6cccb", rock1_shade="#b1a6ae",
    rock2="#bcaca6", rock2_lit="#dccbb8", rock2_shade="#a09090",
    rock3="#c4b09e", rock3_lit="#dcc7ae", rock3_shade="#a69588",
    fall="#f6f7f8", mist="#f3f1ee",
    wall="#f3ede3", wall_shade="#dcd0c1", inner="#b9a698", glow="#f2dcaa",
    roof="#8d6a5a", roof_light="#a98572", roof_dark="#6e5148", trim="#c49a48",
    pine="#55645a", pine_shade="#425047", trunk="#6a4a36",
    leaves=[("#d99a3a", "#b0742a", "#f0c264"), ("#e6b84c", "#c08f33", "#f6d87e"),
            ("#bd5e2e", "#954422", "#da8649"), ("#cf7d32", "#a65d26", "#eaa553"),
            ("#b8a24c", "#92803a", "#d6c272")],
    water="#c9d6e2", water_light="#f2f5f8",
    ground="#cfc6c4", ground_far="#d9d3d4", bird="#5f5866",
)


def mix(a, b, t):
    """Blend hex colour a toward b by t (0..1): used for aerial perspective."""
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def profile(sc, keys, step=6, rough=1.5, wob=0.0):
    """A hand-placed skyline: straight runs between key points, roughened."""
    pts = []
    for (ax, ay), (bx, by) in zip(keys, keys[1:]):
        n = max(1, int(abs(bx - ax) / step))
        for i in range(n):
            t = i / n
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t + sc.r(-rough, rough) + wob * math.sin(x / 23)
            pts.append((x, y))
    pts.append(keys[-1])
    return pts


def mass(sc, pts, fill, bottom=H + 10, cid=None):
    """Close a skyline down to the bottom of the frame; optionally register it as a clip path."""
    d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + f" L{f(pts[-1][0])},{bottom} L{f(pts[0][0])},{bottom}Z"
    if cid:
        sc.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    sc.add(f'<path d="{d}" fill="{fill}"/>')
    return d


def strata(sc, cid, x0, x1, y0, y1, n, col, op, lit=None, lit_n=0, cols=0):
    """Rock texture inside a cliff: tall lit rock columns, lit planes and vertical cracks, clipped to the cliff."""
    g = [f'<g clip-path="url(#{cid})">']
    if lit:
        d = ""
        for _ in range(cols):  # tall jointed columns, the cliff's grain
            x = sc.r(x0, x1)
            w = sc.r(5, 14)
            d += f"M{f(x)},{f(y0 - 40)} l{f(w)},0 l{f(sc.r(-3, 3))},{f(y1 - y0 + 80)} l{f(-w)},0Z"
        for _ in range(lit_n):
            x, y, w, h = sc.r(x0, x1), sc.r(y0, y1), sc.r(8, 26), sc.r(30, 90)
            d += f"M{f(x)},{f(y)} l{f(w)},{f(sc.r(4, 12))} l{f(sc.r(-4, 4))},{f(h)} l{f(-w)},{f(sc.r(-6, 6))}Z"
        g.append(f'<path d="{d}" fill="{lit}" opacity=".5"/>')
    d = ""
    for _ in range(n):
        x, y, h = sc.r(x0, x1), sc.r(y0, y1), sc.r(14, 60)
        d += f"M{f(x)},{f(y)} q{f(sc.r(-3, 3))},{f(h / 2)} {f(sc.r(-4, 4))},{f(h)}"
    g.append(f'<path d="{d}" stroke="{col}" stroke-width="1.2" fill="none" opacity="{op}"/>')
    g.append("</g>")
    sc.add("".join(g))


def blob(sc, x, y, s, fade=0.0, fam=None):
    """A small, cheap tree crown for distant woods: a few overlapping discs."""
    leaf, shade, light = (mix(c, P["haze"], fade) for c in (fam or sc.rnd.choice(P["leaves"])))
    pts = [(x - s * .35, y - s * .7, s * .5), (x + s * .35, y - s * .72, s * .48), (x, y - s * 1.05, s * .55)]
    g = "".join(f'<circle cx="{f(a + r * .15)}" cy="{f(b + r * .15)}" r="{f(r)}" fill="{shade}"/>' for a, b, r in pts)
    g += "".join(f'<circle cx="{f(a)}" cy="{f(b)}" r="{f(r * .88)}" fill="{leaf}"/>' for a, b, r in pts)
    g += f'<circle cx="{f(x - s * .2)}" cy="{f(y - s * 1.2)}" r="{f(s * .22)}" fill="{light}" opacity=".7"/>'
    sc.add(g)


def autumn(sc, x, y, s, fade=0.0, fam=None):
    if s < 12:
        return blob(sc, x, y - s * .15, s * 1.05, fade, fam)
    leaf, shade, light = fam or sc.rnd.choice(P["leaves"])
    hz = P["haze"]
    sc.tree(x, y, s, mix(leaf, hz, fade), mix(shade, hz, fade), mix(light, hz, fade), mix(P["trunk"], hz, fade))


def poplar(sc, x, y, h, fade=0.0, fam=None):
    """A slender golden poplar/birch: a tall narrow crown."""
    leaf, shade, light = fam or sc.rnd.choice(P["leaves"][:2] + P["leaves"][4:])
    leaf, shade, light = (mix(c, P["haze"], fade) for c in (leaf, shade, light))
    w = h * .2
    g = [f'<path d="M{f(x - 1)},{f(y)} L{f(x)},{f(y - h * .7)} L{f(x + 1)},{f(y)}Z" fill="{mix("#e9e3dc", P["haze"], fade)}"/>',
         f'<path d="M{f(x)},{f(y - h)} C{f(x + w * 1.1)},{f(y - h * .7)} {f(x + w)},{f(y - h * .25)} {f(x)},{f(y - h * .18)} C{f(x - w)},{f(y - h * .25)} {f(x - w * 1.1)},{f(y - h * .7)} {f(x)},{f(y - h)}Z" fill="{shade}"/>',
         f'<path d="M{f(x - w * .15)},{f(y - h * .98)} C{f(x + w * .6)},{f(y - h * .72)} {f(x + w * .5)},{f(y - h * .3)} {f(x - w * .1)},{f(y - h * .22)} C{f(x - w * .9)},{f(y - h * .3)} {f(x - w * .95)},{f(y - h * .7)} {f(x - w * .15)},{f(y - h * .98)}Z" fill="{leaf}"/>',
         f'<ellipse cx="{f(x - w * .35)}" cy="{f(y - h * .66)}" rx="{f(w * .28)}" ry="{f(h * .16)}" fill="{light}" opacity=".7"/>']
    sc.add("".join(g))


def canopy(sc, x0, x1, y, rmin, rmax, fam, fade, jitter=4, bottom=H + 10, dapple=.35, to=None):
    """A continuous woodland edge: a run of rounded crowns closed to the bottom, with sunlit dapples."""
    leaf, shade, light = (mix(c, to or P["haze"], fade) for c in fam)
    bumps = []
    x = x0
    while x < x1:
        r = sc.r(rmin, rmax)
        bumps.append((x, r, y + sc.r(-jitter, jitter)))
        x += r * 1.5
    def path(dx, dy):
        d = f"M{f(x0 + dx)},{f(bottom)} L{f(x0 + dx)},{f(bumps[0][2] + dy)}"
        for bx, r, by in bumps:
            d += f" A{f(r)},{f(r * .85)} 0 0 1 {f(bx + r * 1.5 + dx)},{f(by + dy)}"
        return d + f" L{f(x + dx)},{f(bottom)}Z"
    sc.add(f'<path d="{path(2, 2)}" fill="{shade}"/><path d="{path(0, 0)}" fill="{leaf}"/>')
    g = []
    for bx, r, by in bumps:
        if sc.r(0, 1) < dapple:
            g.append(f'<circle cx="{f(bx + r * .6)}" cy="{f(by - r * .45)}" r="{f(r * .3)}" fill="{light}" opacity=".7"/>')
    sc.add("".join(g))


def woodband(sc, x0, y0, x1, y1, fam, fade, rmin=4, rmax=7, depth=10, dapple=.5):
    """Trees clinging to a sloping ledge: a run of small crowns along (x0,y0)-(x1,y1)."""
    leaf, shade, light = (mix(c, P["haze"], fade) for c in fam)
    bumps = []
    x = x0
    while x < x1:
        r = sc.r(rmin, rmax)
        bumps.append((x, r, y0 + (y1 - y0) * (x - x0) / (x1 - x0) + sc.r(-1.5, 1.5)))
        x += r * 1.4
    def path(dx, dy):
        d = f"M{f(x0 + dx)},{f(y0 + depth + dy)} L{f(x0 + dx)},{f(bumps[0][2] + dy)}"
        for bx, r, by in bumps:
            d += f" A{f(r)},{f(r)} 0 0 1 {f(bx + r * 1.4 + dx)},{f(by + dy)}"
        return d + f" L{f(x + dx)},{f(y1 + depth * .6 + dy)} Q{f((x0 + x) / 2)},{f((y0 + y1) / 2 + depth * 1.4)} {f(x0 + dx)},{f(y0 + depth + dy)}Z"
    sc.add(f'<path d="{path(1.5, 1.5)}" fill="{shade}"/><path d="{path(0, 0)}" fill="{leaf}"/>')
    sc.add("".join(f'<circle cx="{f(bx + r * .5)}" cy="{f(by - r * .5)}" r="{f(r * .35)}" fill="{light}" opacity=".75"/>' for bx, r, by in bumps if sc.r(0, 1) < dapple))


def stand(sc, x0, y0, x1, y1, fade, rmin=3.5, rmax=7):
    """A stand of small trees on a sloping ledge: a rock shelf, then crowns of mixed autumn colours."""
    shelf = mix(P["rock2_shade"], P["haze"], fade * .5)
    sc.add(f'<path d="M{f(x0 - 6)},{f(y0 + 3)} Q{f((x0 + x1) / 2)},{f((y0 + y1) / 2 - 3)} {f(x1 + 6)},{f(y1 + 3)} L{f(x1)},{f(y1 + 7)} Q{f((x0 + x1) / 2)},{f((y0 + y1) / 2 + 8)} {f(x0)},{f(y0 + 7)}Z" fill="{shelf}"/>')
    crowns = []
    x = x0
    while x < x1:
        t = (x - x0) / (x1 - x0)
        mid = 1 - abs(t - .5) * 1.4
        r = sc.r(rmin, rmax) * (.7 + .5 * mid)
        y = y0 + (y1 - y0) * t + 3 - r * sc.r(.6, 1.6)
        crowns.append((x, y, r, sc.rnd.choice(P["leaves"])))
        if sc.r(0, 1) < .22:  # a taller tree behind
            crowns.insert(0, (x + sc.r(-2, 2), y - r * sc.r(.9, 1.4), r * .8, sc.rnd.choice(P["leaves"])))
        x += r * sc.r(1.4, 1.9)
    g = []
    for cx, cy, r, fam in crowns:
        leaf, shade, light = (mix(c, P["haze"], fade) for c in fam)
        g.append(f'<circle cx="{f(cx + r * .2)}" cy="{f(cy + r * .2)}" r="{f(r)}" fill="{shade}"/><circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r * .88)}" fill="{leaf}"/>')
        if sc.r(0, 1) < .3:
            g.append(f'<circle cx="{f(cx - r * .3)}" cy="{f(cy - r * .35)}" r="{f(r * .35)}" fill="{light}" opacity=".75"/>')
    sc.add("".join(g))


def rimwood(sc, pts, x0, x1, fade, rmin, rmax, pine_p, pine_h, sink=3):
    """Woods along a clifftop: crowns of mixed colour hugging the skyline, dark pines standing up out of them."""
    x = x0
    pines = []
    g = []
    while x < x1:
        y = sc.y_at(pts, x) + sink
        r = sc.r(rmin, rmax)
        if sc.r(0, 1) < pine_p:
            pines.append((x, y + r * .4))
        leaf, shade, light = (mix(c, P["haze"], fade) for c in sc.rnd.choice(P["leaves"]))
        cy = y - r * sc.r(.3, 1.0)
        g.append(f'<circle cx="{f(x + r * .2)}" cy="{f(cy + r * .2)}" r="{f(r)}" fill="{shade}"/><circle cx="{f(x)}" cy="{f(cy)}" r="{f(r * .88)}" fill="{leaf}"/>')
        if sc.r(0, 1) < .3:
            g.append(f'<circle cx="{f(x - r * .3)}" cy="{f(cy - r * .35)}" r="{f(r * .35)}" fill="{light}" opacity=".75"/>')
        x += r * sc.r(1.1, 1.6)
    for px, py in pines:
        pine(sc, px, py, sc.r(*pine_h), fade + .05)
    sc.add("".join(g))


def rimcanopy(sc, pts, x0, x1, fade, rmin, rmax, sink=3, depth=10, dots=.3):
    """Distant woods along a skyline as two scalloped bands of colour (cheap), with a few bright crowns."""
    for k, fam in enumerate([P["leaves"][2], P["leaves"][4]]):
        leaf, shade, light = (mix(c, P["haze"], fade) for c in fam)
        x = x0 + k * rmax
        d = f"M{f(x)},{f(sc.y_at(pts, x) + sink + depth)} L{f(x)},{f(sc.y_at(pts, x) + sink)}"
        while x < x1:
            r = sc.r(rmin, rmax)
            nx = x + r * 1.6
            d += f" A{f(r)},{f(r)} 0 0 1 {f(nx)},{f(sc.y_at(pts, nx) + sink + k * 2 + sc.r(-1, 1.5))}"
            x = nx
        for bx in range(int(x), int(x0) - 20, -20):
            d += f" L{bx},{f(sc.y_at(pts, bx) + sink + depth)}"
        sc.add(f'<path d="{d}" fill="{leaf if k else shade}"/>')
    g = []
    x = x0
    while x < x1:
        if sc.r(0, 1) < dots:
            leaf, shade, light = (mix(c, P["haze"], fade) for c in sc.rnd.choice(P["leaves"]))
            r = sc.r(rmin, rmax) * .8
            g.append(f'<circle cx="{f(x)}" cy="{f(sc.y_at(pts, x) + sink - r * .6)}" r="{f(r)}" fill="{sc.rnd.choice([leaf, light])}"/>')
        x += rmax * 1.3
    sc.add("".join(g))


def pine(sc, x, y, h, fade=0.0):
    """A dark, slightly drooping pine in stacked tiers."""
    col, shade = mix(P["pine"], P["haze"], fade), mix(P["pine_shade"], P["haze"], fade)
    w = h * .32
    g = [f'<rect x="{f(x - h * .025)}" y="{f(y - h * .2)}" width="{f(h * .05)}" height="{f(h * .2)}" fill="{shade}"/>']
    d1 = d2 = ""
    for i in range(3):
        top = y - h + i * h * .27
        bot = top + h * .44
        ww = w * (.5 + i * .25)
        if h < 31:  # small and far: straight-sided tiers are enough
            d1 += f"M{f(x)},{f(top)}L{f(x + ww)},{f(bot)} {f(x - ww)},{f(bot)}Z"
            d2 += f"M{f(x)},{f(top)}L{f(x + ww)},{f(bot)} {f(x)},{f(bot)}Z"
            continue
        d1 += f"M{f(x)},{f(top)} Q{f(x + ww * .4)},{f(bot - h * .1)} {f(x + ww)},{f(bot)} Q{f(x)},{f(bot - h * .05)} {f(x - ww)},{f(bot)} Q{f(x - ww * .4)},{f(bot - h * .1)} {f(x)},{f(top)}Z"
        d2 += f"M{f(x)},{f(top)} Q{f(x + ww * .4)},{f(bot - h * .1)} {f(x + ww)},{f(bot)} Q{f(x + ww * .4)},{f(bot - h * .04)} {f(x)},{f(bot - h * .03)}Z"
    g.append(f'<path d="{d1}" fill="{col}"/><path d="{d2}" fill="{shade}" opacity=".6"/>')
    sc.add("".join(g))


def fall(sc, x, y0, y1, w, op=1.0, mist_s=1.0, lean=0.0):
    """A ribbon waterfall from a notch at (x, y0) down to y1, widening, with spray and mist."""
    w1 = w * 2.2
    xm = x + lean
    d = (f"M{f(x - w / 2)},{f(y0)} C{f(x - w / 2)},{f(y0 + 10)} {f(xm - w1 / 2)},{f(y1 - (y1 - y0) * .5)} {f(xm - w1 / 2)},{f(y1)} "
         f"L{f(xm + w1 / 2)},{f(y1)} C{f(xm + w1 / 2)},{f(y1 - (y1 - y0) * .5)} {f(x + w / 2)},{f(y0 + 10)} {f(x + w / 2)},{f(y0)}Z")
    g = [f'<g opacity="{op}">',
         f'<ellipse cx="{f(x)}" cy="{f(y0 + 1)}" rx="{f(w * .9)}" ry="{f(w * .5)}" fill="{P["rock2_shade"]}" opacity=".5"/>',
         f'<path d="{d}" fill="{P["fall"]}" opacity=".9"/>']
    for i in range(int(3 + w / 2)):  # streaks in the falling water
        t = sc.r(.1, .9)
        sx = x - w / 2 + w * t
        ex = xm - w1 / 2 + w1 * t
        sy = sc.r(y0, y0 + (y1 - y0) * .4)
        g.append(f'<path d="M{f(sx)},{f(sy)} L{f(ex)},{f(y1)}" stroke="#c9d3dc" stroke-width="{f(sc.r(.5, 1.1))}" opacity=".55"/>')
    # spray drifting at the foot
    for i in range(5):
        g.append(f'<ellipse cx="{f(xm + sc.r(-14, 14) * mist_s)}" cy="{f(y1 - sc.r(0, 12) * mist_s)}" rx="{f(sc.r(12, 24) * mist_s)}" ry="{f(sc.r(5, 9) * mist_s)}" fill="{P["mist"]}" opacity="{f(sc.r(.3, .55))}"/>')
    g.append("</g>")
    sc.add("".join(g))


# ---------- Elvish architecture ----------

def arcade(sc, x0, yb, w, h, n, wall, shade, inner, glow_every=0):
    """A wall pierced by n tall pointed arches on slim columns."""
    g = [f'<rect x="{f(x0)}" y="{f(yb - h)}" width="{f(w)}" height="{f(h)}" fill="{wall}"/>',
         f'<rect x="{f(x0 + w * .82)}" y="{f(yb - h)}" width="{f(w * .18)}" height="{f(h)}" fill="{shade}" opacity=".6"/>']
    col = max(1.2, w / n * .18)
    aw = w / n - col
    for i in range(n):
        a = x0 + col / 2 + i * (aw + col)
        yt = yb - h + h * .14
        lit = glow_every and i % glow_every == 1
        g.append(f'<path d="M{f(a)},{f(yb)} V{f(yt + aw * .6)} Q{f(a)},{f(yt)} {f(a + aw / 2)},{f(yt - aw * .2)} Q{f(a + aw)},{f(yt)} {f(a + aw)},{f(yt + aw * .6)} V{f(yb)}Z" fill="{P["glow"] if lit else inner}"/>')
    g.append(f'<rect x="{f(x0 - 1.5)}" y="{f(yb - h - 2)}" width="{f(w + 3)}" height="2.2" fill="{shade}"/>')
    g.append(f'<rect x="{f(x0 - 1)}" y="{f(yb - 1.5)}" width="{f(w + 2)}" height="1.5" fill="{shade}"/>')
    sc.add("".join(g))


def roof(sc, x0, x1, y, h, ov, col, light, dark, lines=True):
    """A sweeping roof with concave flanks and up-curled eaves."""
    xc = (x0 + x1) / 2
    w = x1 - x0
    top = f"M{f(x0 - ov)},{f(y - 3)} Q{f(x0 + w * .18)},{f(y - h * .12)} {f(xc - w * .06)},{f(y - h)} L{f(xc + w * .06)},{f(y - h)} Q{f(x1 - w * .18)},{f(y - h * .12)} {f(x1 + ov)},{f(y - 3)}"
    d = top + f" Q{f(x1)},{f(y + 1.5)} {f(x1 - w * .1)},{f(y + 1)} L{f(x0 + w * .1)},{f(y + 1)} Q{f(x0)},{f(y + 1.5)} {f(x0 - ov)},{f(y - 3)}Z"
    g = [f'<path d="{f"M{f(x0 - ov * .6)},{f(y - 1)} L{f(x1 + ov * .6)},{f(y - 1)} L{f(x1)},{f(y + 4)} L{f(x0)},{f(y + 4)}Z"}" fill="{dark}" opacity=".5"/>',
         f'<path d="{d}" fill="{col}"/>']
    # the sunlit left flank
    g.append(f'<path d="M{f(x0 - ov)},{f(y - 3)} Q{f(x0 + w * .18)},{f(y - h * .12)} {f(xc - w * .06)},{f(y - h)} L{f(xc - w * .02)},{f(y - h)} Q{f(x0 + w * .3)},{f(y - h * .05)} {f(x0 + w * .1)},{f(y + 1)}Z" fill="{light}" opacity=".75"/>')
    if lines:
        k = max(3, int(w / 9))
        for i in range(1, k):
            t = i / k
            ex = x0 - ov + (x1 + ov - x0 + ov) * t
            g.append(f'<path d="M{f(xc + (t - .5) * w * .12)},{f(y - h + 1)} Q{f(xc + (t - .5) * w * .5)},{f(y - h * .35)} {f(ex)},{f(y - 1)}" stroke="{dark}" stroke-width=".6" fill="none" opacity=".45"/>')
    g.append(f'<path d="M{f(xc - w * .06)},{f(y - h)} L{f(xc + w * .06)},{f(y - h)}" stroke="{P["trim"]}" stroke-width="1.2"/>')
    g.append(f'<path d="M{f(xc)},{f(y - h)} V{f(y - h - 5)}" stroke="{P["trim"]}" stroke-width="1"/><circle cx="{f(xc)}" cy="{f(y - h - 5.5)}" r="1.2" fill="{P["trim"]}"/>')
    sc.add("".join(g))


def tower(sc, x, yb, w, h, fade=0.0, windows=3, balcony=True):
    """A slender round-ish tower with lancet windows, a balcony ring and an ogee cupola."""
    wall, shade, inner = (mix(c, P["haze"], fade) for c in (P["wall"], P["wall_shade"], P["inner"]))
    rf, rl, rd, trim = (mix(c, P["haze"], fade) for c in (P["roof"], P["roof_light"], P["roof_dark"], P["trim"]))
    yt = yb - h
    g = [f'<rect x="{f(x - w / 2)}" y="{f(yt)}" width="{f(w)}" height="{f(h)}" fill="{wall}"/>',
         f'<rect x="{f(x + w * .1)}" y="{f(yt)}" width="{f(w * .4)}" height="{f(h)}" fill="{shade}"/>',
         f'<rect x="{f(x - w / 2 - 1)}" y="{f(yb - 3)}" width="{f(w + 2)}" height="3" fill="{shade}"/>']
    for i in range(windows):
        wy = yt + 12 + i * (h - 20) / max(1, windows)
        ww = w * .28
        g.append(f'<path d="M{f(x - ww / 2)},{f(wy + ww * 2.4)} V{f(wy + ww * .6)} Q{f(x - ww / 2)},{f(wy)} {f(x)},{f(wy - ww * .3)} Q{f(x + ww / 2)},{f(wy)} {f(x + ww / 2)},{f(wy + ww * .6)} V{f(wy + ww * 2.4)}Z" fill="{P["glow"] if i == 1 and fade < .3 else inner}"/>')
    if balcony:
        by = yt + 7
        g.append(f'<rect x="{f(x - w * .85)}" y="{f(by)}" width="{f(w * 1.7)}" height="2" fill="{shade}"/>')
        g.append(f'<path d="M{f(x - w * .85)},{f(by + 2)} Q{f(x)},{f(by + 9)} {f(x + w * .85)},{f(by + 2)}" fill="{shade}" opacity=".7"/>')
        g.append(f'<path d="M{f(x - w * .85)},{f(by - 4)} H{f(x + w * .85)}" stroke="{shade}" stroke-width=".8"/>')
        for k in range(5):
            px = x - w * .85 + k * w * 1.7 / 4
            g.append(f'<path d="M{f(px)},{f(by - 4)} V{f(by)}" stroke="{shade}" stroke-width=".7"/>')
    ch = w * 3.0  # a tall spire with concave flanks and flared eaves
    cw = w * .82
    g.append(f'<path d="M{f(x - cw)},{f(yt + 1)} Q{f(x - w * .12)},{f(yt - ch * .22)} {f(x)},{f(yt - ch)} Q{f(x + w * .12)},{f(yt - ch * .22)} {f(x + cw)},{f(yt + 1)}Z" fill="{rf}"/>')
    g.append(f'<path d="M{f(x - cw)},{f(yt + 1)} Q{f(x - w * .12)},{f(yt - ch * .22)} {f(x)},{f(yt - ch)} Q{f(x - w * .14)},{f(yt - ch * .3)} {f(x - cw * .25)},{f(yt + 1)}Z" fill="{rl}"/>')
    g.append(f'<path d="M{f(x - cw - 1)},{f(yt + 1)} H{f(x + cw + 1)}" stroke="{rd}" stroke-width="1.4"/>')
    g.append(f'<path d="M{f(x)},{f(yt - ch)} V{f(yt - ch - 7)}" stroke="{trim}" stroke-width="1"/><circle cx="{f(x)}" cy="{f(yt - ch * .55)}" r="1.1" fill="{trim}"/>')
    sc.add("".join(g))


def hall(sc, x0, yb, w, h, n, roof_h, fade=0.0, glow_every=3, upper=0):
    wall, shade, inner = (mix(c, P["haze"], fade) for c in (P["wall"], P["wall_shade"], P["inner"]))
    rf, rl, rd = (mix(c, P["haze"], fade) for c in (P["roof"], P["roof_light"], P["roof_dark"]))
    top = yb - h
    if upper:  # a set-back upper storey
        uw = w * .7
        ux = x0 + (w - uw) / 2
        arcade(sc, ux, top, uw, upper, max(3, n - 2), wall, shade, inner, glow_every)
        top -= upper
        roof(sc, ux, ux + uw, top, roof_h, uw * .12, rf, rl, rd)
        # skirt roof over the lower arcade
        sc.add(f'<path d="M{f(x0 - w * .06)},{f(yb - h + 2)} Q{f(x0 + w * .2)},{f(yb - h - 3)} {f(ux)},{f(yb - h - 6)} L{f(ux + uw)},{f(yb - h - 6)} Q{f(x0 + w * .8)},{f(yb - h - 3)} {f(x0 + w * 1.06)},{f(yb - h + 2)}Z" fill="{rf}"/>'
               f'<path d="M{f(x0 - w * .06)},{f(yb - h + 2)} Q{f(x0 + w * .2)},{f(yb - h - 3)} {f(ux)},{f(yb - h - 6)} L{f(ux + uw * .2)},{f(yb - h - 6)} Q{f(x0 + w * .25)},{f(yb - h - 1)} {f(x0 + w * .05)},{f(yb - h + 2)}Z" fill="{rl}" opacity=".7"/>')
        arcade(sc, x0, yb, w, h, n, wall, shade, inner, glow_every)
    else:
        arcade(sc, x0, yb, w, h, n, wall, shade, inner, glow_every)
        roof(sc, x0, x0 + w, top, roof_h, w * .1, rf, rl, rd)


def gazebo(sc, x, yb, r, h, fade=0.0):
    """An open round pavilion on slim columns under a flared dome."""
    wall, shade = mix(P["wall"], P["haze"], fade), mix(P["wall_shade"], P["haze"], fade)
    rf, rl = mix(P["roof"], P["haze"], fade), mix(P["roof_light"], P["haze"], fade)
    g = [f'<ellipse cx="{f(x)}" cy="{f(yb)}" rx="{f(r * 1.15)}" ry="{f(r * .28)}" fill="{shade}"/>',
         f'<ellipse cx="{f(x)}" cy="{f(yb - 1.5)}" rx="{f(r * 1.1)}" ry="{f(r * .24)}" fill="{wall}"/>']
    for k in range(5):
        cx = x - r + k * r / 2
        g.append(f'<rect x="{f(cx - .9)}" y="{f(yb - h)}" width="1.8" height="{f(h - 1)}" fill="{wall if k < 3 else shade}"/>')
        if k < 4:
            g.append(f'<path d="M{f(cx + .9)},{f(yb - h + 6)} Q{f(cx + r / 4)},{f(yb - h + 1)} {f(cx + r / 2 - .9)},{f(yb - h + 6)}" stroke="{wall}" stroke-width="1" fill="none"/>')
    g.append(f'<path d="M{f(x - r * 1.25)},{f(yb - h + 1)} Q{f(x - r * .95)},{f(yb - h - 2)} {f(x - r * .8)},{f(yb - h - r * .5)} Q{f(x - r * .5)},{f(yb - h - r * 1.25)} {f(x)},{f(yb - h - r * 1.4)} Q{f(x + r * .5)},{f(yb - h - r * 1.25)} {f(x + r * .8)},{f(yb - h - r * .5)} Q{f(x + r * .95)},{f(yb - h - 2)} {f(x + r * 1.25)},{f(yb - h + 1)} Q{f(x)},{f(yb - h + 4)} {f(x - r * 1.25)},{f(yb - h + 1)}Z" fill="{rf}"/>')
    g.append(f'<path d="M{f(x - r * 1.25)},{f(yb - h + 1)} Q{f(x - r * .95)},{f(yb - h - 2)} {f(x - r * .8)},{f(yb - h - r * .5)} Q{f(x - r * .5)},{f(yb - h - r * 1.25)} {f(x)},{f(yb - h - r * 1.4)} Q{f(x - r * .5)},{f(yb - h - r * .9)} {f(x - r * .45)},{f(yb - h + 2)}Z" fill="{rl}" opacity=".8"/>')
    g.append(f'<path d="M{f(x)},{f(yb - h - r * 1.4)} V{f(yb - h - r * 1.4 - 8)}" stroke="{P["trim"]}" stroke-width="1"/><circle cx="{f(x)}" cy="{f(yb - h - r * 1.4 - 4)}" r="1.2" fill="{P["trim"]}"/>')
    sc.add("".join(g))


def bridge(sc, x0, y0, x1, y1, rise, fade=0.0):
    """A slender arched footbridge with a curving underside and a light railing."""
    wall, shade = mix(P["wall"], P["haze"], fade), mix(P["wall_shade"], P["haze"], fade)
    xm = (x0 + x1) / 2
    ym = (y0 + y1) / 2 - rise
    deck = f"M{f(x0)},{f(y0)} Q{f(xm)},{f(ym - rise * .1)} {f(x1)},{f(y1)}"
    under = f"M{f(x0)},{f(y0 + 6)} Q{f(xm)},{f(ym + 3)} {f(x1)},{f(y1 + 6)}"
    g = [f'<path d="M{f(x0)},{f(y0)} Q{f(xm)},{f(ym - rise * .1)} {f(x1)},{f(y1)} L{f(x1)},{f(y1 + 3)} Q{f(xm)},{f(ym - rise * .1 + 3)} {f(x0)},{f(y0 + 3)}Z" fill="{wall}"/>',
         f'<path d="{under}" stroke="{shade}" stroke-width="1.8" fill="none"/>']

    def q(t, a, c, b):
        return (1 - t) ** 2 * a + 2 * (1 - t) * t * c + t * t * b
    for i in range(1, 12):  # hangers and rail posts
        t = i / 12
        dx, dy = q(t, x0, xm, x1), q(t, y0, ym - rise * .1, y1)
        uy = q(t, y0 + 6, ym + 3, y1 + 6)
        g.append(f'<path d="M{f(dx)},{f(dy + 3)} V{f(uy)}" stroke="{shade}" stroke-width=".7"/>')
        g.append(f'<path d="M{f(dx)},{f(dy)} V{f(dy - 5)}" stroke="{shade}" stroke-width=".8"/>')
    g.append(f'<path d="M{f(x0)},{f(y0 - 5)} Q{f(xm)},{f(ym - rise * .1 - 5)} {f(x1)},{f(y1 - 5)}" stroke="{shade}" stroke-width="1" fill="none"/>')
    sc.add("".join(g))


def terrace(sc, x0, x1, y, depth, fade=0.0, arches=0):
    """A stone platform with a battered retaining wall and a balustrade."""
    wall, shade = mix(P["wall"], P["haze"], fade), mix(P["wall_shade"], P["haze"], fade)
    inner = mix(P["inner"], P["haze"], fade)
    g = [f'<path d="M{f(x0)},{f(y)} L{f(x1)},{f(y)} L{f(x1 - 4)},{f(y + depth)} L{f(x0 + 4)},{f(y + depth)}Z" fill="{shade}"/>',
         f'<rect x="{f(x0 - 2)}" y="{f(y - 1)}" width="{f(x1 - x0 + 4)}" height="3.5" fill="{wall}"/>']
    if arches:
        aw = (x1 - x0 - 8) / arches
        for i in range(arches):
            a = x0 + 6 + i * aw
            g.append(f'<path d="M{f(a)},{f(y + depth)} V{f(y + depth * .5)} Q{f(a)},{f(y + 6)} {f(a + aw * .35)},{f(y + 6)} Q{f(a + aw * .7)},{f(y + 6)} {f(a + aw * .7)},{f(y + depth * .5)} V{f(y + depth)}Z" fill="{inner}" opacity=".7"/>')
    g.append(f'<path d="M{f(x0)},{f(y - 6)} H{f(x1)}" stroke="{wall}" stroke-width="1"/>')
    posts = "".join(f"M{f(x0 + k * 5)},{f(y - 6)}v5" for k in range(int((x1 - x0) / 5) + 1))
    g.append(f'<path d="{posts}" stroke="{wall}" stroke-width=".8"/>')
    sc.add("".join(g))


def build(seed=11):
    sc = Scene(seed)
    sc.sky(sc.lin("sky", P["sky"]))
    sc.add(f'<circle cx="300" cy="40" r="300" fill="{sc.rad("sun", [(0, P["sun"], .95), (.3, P["sun"], .45), (1, P["sun"], 0)])}"/>')
    for cx, cy, s, op in [(560, 40, 26, .75), (850, 70, 34, .85), (1300, 30, 30, .7), (1520, 96, 20, .55), (120, 104, 18, .5)]:
        sc.cloud(cx, cy, s, P["cloud"], P["cloud_shade"], op)
    sc.birds([(700, 62), (716, 55), (731, 66), (1010, 44)], P["bird"], .8)

    # ---- the Misty Mountains, far off through the valley mouth ----
    keys = [(-20, 150), (60, 120), (140, 142), (230, 108), (320, 138), (420, 116), (520, 140), (610, 104), (690, 132),
            (760, 96), (840, 128), (905, 88), (970, 124), (1040, 100), (1110, 136), (1190, 110), (1290, 140), (1400, 112),
            (1500, 138), (1620, 118)]
    mtn = profile(sc, keys, 5, .8)
    mass(sc, mtn, P["mtn"])
    for (ax, ay), (bx, by), (cx, cy) in zip(keys, keys[1:], keys[2:]):  # snow on the peaks, shade on their right flanks
        if by < ay and by < cy:
            sc.add(f'<path d="M{f(bx)},{f(by)} L{f(cx)},{f(cy)} L{f(bx + 6)},{f(cy + 30)}Z" fill="{P["mtn_shade"]}" opacity=".7"/>')
            sc.add(f'<path d="M{f(bx)},{f(by)} L{f(bx + (cx - bx) * .28)},{f(by + (cy - by) * .28)} L{f(bx + 3)},{f(by + 9)} L{f(bx - 4)},{f(by + 13)} L{f(bx + (ax - bx) * .3)},{f(by + (ay - by) * .3)}Z" fill="{P["snow"]}"/>')
    sc.add(f'<rect y="90" width="{W}" height="130" fill="{sc.lin("hz0", [(0, P["haze"], 0), (1, P["haze"], .75)])}"/>')
    # a lower blue foothill in the gap
    sc.ridge(178, 6, [(2.1, 1), (5.3, .4)], mix(P["mtn"], P["haze"], .35), seed=3.3)

    # ---- back cliffs (hazy), wrapping round behind the house, open in the middle-right ----
    k1 = [(-20, 66), (70, 56), (150, 64), (240, 44), (330, 58), (420, 50), (520, 68), (600, 60), (680, 88), (760, 96),
          (830, 118), (875, 146), (910, 176), (960, 196), (1010, 200), (1050, 186), (1090, 150), (1140, 112), (1200, 92),
          (1300, 72), (1400, 82), (1500, 58), (1620, 66)]
    back = profile(sc, k1, 6, 1.6)
    mass(sc, back, P["rock1"], cid="c1")
    strata(sc, "c1", -20, 1620, 50, 260, 60, P["rock1_shade"], .55, P["rock1_lit"], 30, 34)
    # woods along the back rim: scattered small crowns, thinning where the rim drops into the gap
    g = []
    x = -10
    while x < W + 10:
        y = sc.y_at(back, x)
        if sc.r(0, 1) < (.6 if y < 120 else .25):
            leaf, shade, light = (mix(c, P["haze"], .58) for c in sc.rnd.choice(P["leaves"]))
            r = sc.r(2.5, 5)
            g.append(f'<circle cx="{f(x + .8)}" cy="{f(y + 4 - r * .3)}" r="{f(r)}" fill="{shade}"/><circle cx="{f(x)}" cy="{f(y + 3 - r * .4)}" r="{f(r * .85)}" fill="{leaf}"/>')
        x += sc.r(6, 10)
    sc.add("".join(g))
    for x in range(0, W, 56):
        x += sc.r(-16, 16)
        if sc.r(0, 1) < .6:
            pine(sc, x, sc.y_at(back, x) + 6, sc.r(10, 15), .62)
    fall(sc, 742, 94, 230, 3, .75, .8, 3)
    fall(sc, 1255, 84, 220, 3.5, .7, .8, -2)
    sc.add(f'<rect y="60" width="{W}" height="260" fill="{sc.lin("hz1", [(0, P["haze"], 0), (.5, P["haze"], .35), (1, P["haze"], .9)])}"/>')

    # upper buildings on a ledge of the back cliff, softened by haze
    terrace(sc, 640, 760, 168, 14, .45)
    hall(sc, 652, 168, 52, 16, 5, 12, .45)
    tower(sc, 722, 168, 9, 44, .45, 2)
    gazebo(sc, 748, 168, 7, 13, .45)
    for x in (630, 770, 790):
        autumn(sc, x, 176, 9, .45)

    # ---- the near cliffs, left and right ----
    kl = [(-20, 40), (60, 30), (140, 46), (220, 34), (300, 54), (360, 66), (405, 80), (432, 96), (446, 134), (456, 190),
          (466, 246), (476, 300), (484, 410)]
    left = profile(sc, kl, 5, 1.3)
    mass(sc, left, P["rock2"], cid="cl")
    kr = [(1066, 410), (1072, 300), (1084, 240), (1098, 172), (1112, 124), (1136, 100), (1200, 86), (1262, 94),
          (1330, 70), (1400, 62), (1470, 76), (1540, 46), (1620, 40)]
    right = profile(sc, kr, 5, 1.3)
    mass(sc, right, P["rock2"], cid="cr")
    # left cliff: sunlit top face, shaded face toward the house; right cliff: its west face catches the sun
    sc.add(f'<g clip-path="url(#cl)"><path d="M-20,30 L430,90 L455,400 L-20,400Z" fill="{P["rock2_lit"]}" opacity=".35"/>'
           f'<path d="M400,60 L470,60 L490,400 L440,400Z" fill="{P["rock2_shade"]}" opacity=".7"/></g>')
    sc.add(f'<g clip-path="url(#cr)"><path d="M1060,400 L1110,110 L1160,96 L1150,400Z" fill="{P["rock2_lit"]}" opacity=".85"/></g>')
    strata(sc, "cl", -20, 480, 30, 320, 60, P["rock2_shade"], .6, P["rock2_lit"], 20, 22)
    strata(sc, "cr", 1060, 1620, 40, 320, 70, P["rock2_shade"], .6, P["rock2_lit"], 24, 28)
    # wooded ledges on the cliff faces: crowns of mixed colour, a few dark pines standing out
    L = P["leaves"]
    ledges = [(-20, 100, 84, 112), (126, 150, 226, 138), (256, 108, 318, 118), (40, 190, 150, 204), (280, 192, 372, 204),
              (-20, 252, 96, 262), (150, 222, 236, 234), (330, 150, 392, 158), (1150, 162, 1250, 148), (1290, 110, 1356, 118),
              (1428, 126, 1516, 136), (1270, 206, 1360, 222), (1476, 192, 1600, 180),
              (1560, 118, 1620, 112)]  # (the cards cover the cliff foot on the right, so no ledges there)
    for i, (x0, y0, x1, y1) in enumerate(ledges):
        stand(sc, x0, y0, x1, y1, .2)
        for k in range(sc.rnd.choice([0, 1, 1, 2])):
            xx = sc.r(x0 + 10, x1 - 10)
            pine(sc, xx, y0 + (y1 - y0) * (xx - x0) / (x1 - x0) + 4, sc.r(18, 26), .25)
    # a little pavilion on a ledge beside the falls
    sc.add(f'<path d="M280,262 L384,262 Q376,278 352,288 Q330,300 300,286 Q286,276 280,262Z" fill="{mix(P["rock2_shade"], P["haze"], .1)}"/>'
           f'<path d="M280,262 L330,262 Q320,280 300,286 Q286,276 280,262Z" fill="{P["rock2_lit"]}" opacity=".6"/>')
    stand(sc, 284, 288, 384, 286, .2, 4, 7)
    terrace(sc, 292, 372, 254, 12, .15)
    hall(sc, 300, 254, 64, 18, 5, 13, .15, 3)
    # waterfalls on the near cliffs
    fall(sc, 214, 37, 300, 5, .95, 1.3, 8)
    fall(sc, 410, 84, 306, 4, .9, 1.1, 10)
    fall(sc, 1118, 120, 300, 4.5, .95, 1.2, -6)
    fall(sc, 1392, 63, 290, 6, .95, 1.3, -4)
    fall(sc, 1545, 48, 270, 3.5, .85, 1.0, 2)
    # woods along the near rims, with a few slender golden poplars
    rimwood(sc, left, -14, 424, .15, 5, 9, .18, (20, 30))
    rimwood(sc, right, 1134, W + 14, .15, 5, 9, .18, (20, 30))
    for x in (1162, 1240, 1300, 1455, 1590):
        poplar(sc, x, sc.y_at(right, x) + 5, sc.r(26, 34), .15)
    for x in (24, 168, 330):
        poplar(sc, x, sc.y_at(left, x) + 5, sc.r(26, 34), .15)

    # ---- the spur of the Last Homely House ----
    ks = [(470, 410), (478, 300), (498, 266), (530, 252), (560, 236), (590, 220), (640, 212), (720, 210), (790, 216),
          (840, 226), (880, 238), (950, 242), (1000, 236), (1016, 244), (1034, 270), (1050, 310), (1060, 410)]
    spur = profile(sc, ks, 5, 1.0)
    mass(sc, spur, P["rock3"], cid="cs")
    sc.add(f'<g clip-path="url(#cs)"><path d="M470,410 L520,250 L640,212 L700,240 L620,410Z" fill="{P["rock3_lit"]}" opacity=".6"/>'
           f'<path d="M980,236 L1060,240 L1070,410 L1000,410Z" fill="{P["rock3_shade"]}" opacity=".6"/></g>')
    strata(sc, "cs", 470, 1060, 220, 330, 40, P["rock3_shade"], .5)
    # trees behind the buildings
    for x, y, s in [(612, 214, 12), (800, 220, 13), (836, 228, 11), (690, 212, 10), (540, 252, 11), (960, 240, 10)]:
        autumn(sc, x, y, s, .1)
    poplar(sc, 580, 226, 40, .05)
    poplar(sc, 846, 232, 36, .05)
    pine(sc, 822, 226, 38, .1)
    pine(sc, 524, 258, 32, .1)

    # the main house: a tall tower, the great hall with its upper storey, a second tower
    tower(sc, 598, 214, 15, 96, 0, 4)
    terrace(sc, 600, 790, 214, 22, 0, 6)
    hall(sc, 620, 214, 150, 34, 9, 22, 0, 3, upper=22)
    tower(sc, 790, 216, 12, 62, 0, 3)
    # left wing on a lower terrace
    terrace(sc, 494, 590, 252, 18, 0, 4)
    hall(sc, 505, 252, 76, 26, 5, 18, 0, 2)
    # an open colonnade on the right, then the round pavilion on its outcrop
    terrace(sc, 842, 970, 240, 16, 0, 5)
    tower(sc, 948, 240, 11, 64, 0, 3)
    hall(sc, 852, 240, 104, 24, 8, 16, 0, 4)
    gazebo(sc, 996, 236, 12, 22)
    bridge(sc, 1006, 238, 1108, 234, 16)
    # stair from the lower wing up to the hall terrace
    for i in range(7):
        sc.add(f'<rect x="{f(588 + i * 2.2)}" y="{f(250 - i * 5)}" width="9" height="2" fill="{P["wall_shade"]}"/>')

    # front trees on the spur, in front of the terrace walls
    for x, y, s in [(505, 286, 18), (560, 280, 16), (612, 262, 15), (668, 258, 17), (726, 262, 14), (780, 258, 16),
                    (840, 268, 15), (896, 270, 17), (950, 274, 15), (1004, 280, 16), (1040, 300, 14)]:
        autumn(sc, x + sc.r(-4, 4), y, s, .05)
    for x in (640, 862, 980):
        pine(sc, x, 272, sc.r(36, 44), .08)
    for x in (700, 925):
        poplar(sc, x, 268, sc.r(44, 52), .05)

    # ---- the valley floor: the Bruinen in mist, autumn treetops, fading toward the page ----
    sc.add(f'<rect y="250" width="{W}" height="150" fill="{sc.lin("hz2", [(0, P["haze"], 0), (.4, P["haze"], .45), (1, P["haze"], .7)])}"/>')
    L = P["leaves"]
    canopy(sc, -20, W + 20, 300, 9, 15, L[2], .42, 5, 334, .15)
    canopy(sc, -20, W + 20, 308, 8, 14, L[1], .4, 5, 334, .2)
    for x in range(10, W, 120):
        pine(sc, x + sc.r(-30, 30), 316, sc.r(28, 38), .42)
    canopy(sc, -20, W + 20, 316, 8, 13, L[0], .38, 4, 334, .35)
    wy = 322
    sc.add(f'<path d="M-20,{wy} Q260,{wy - 8} 560,{wy + 2} T1140,{wy - 2} T1620,{wy + 3} L1620,{wy + 14} Q1200,{wy + 9} 880,{wy + 15} T-20,{wy + 13}Z" fill="{P["water"]}"/>')
    glints = "".join(f"M{f(sc.r(0, W))},{f(wy + 4 + sc.r(0, 7))}h{f(sc.r(8, 22))}" for i in range(36))
    sc.add(f'<path d="{glints}" stroke="{P["water_light"]}" stroke-width="1.2" stroke-linecap="round" opacity=".85"/>')
    # drifting mist over the water
    for i in range(18):
        sc.add(f'<ellipse cx="{f(sc.r(-40, W + 40))}" cy="{f(sc.r(300, 336))}" rx="{f(sc.r(60, 140))}" ry="{f(sc.r(6, 12))}" fill="{P["mist"]}" opacity="{f(sc.r(.3, .55))}"/>')
    # near ground, close to the page colour
    canopy(sc, -20, W + 20, 348, 10, 18, L[3], .78, 6, H + 10, .15, "#d6d2da")
    sc.ridge(368, 4, [(2.3, 1), (5.1, .4)], P["ground"], seed=7.7)
    sc.tufts(364, 400, 50, ["#c4b8b0", "#cbbca6", "#bdb0ae", "#d1c4b4"], 5, 12)
    sc.flowers(368, 398, 40, ["#d99a3a", "#bd5e2e", "#e6b84c", "#cf7d32"], 1.5, 2.8)  # fallen leaves
    sc.add(f'<rect y="330" width="{W}" height="70" fill="{sc.lin("hz3", [(0, "#dcdae0", 0), (1, "#dcdae0", .55)])}"/>')
    return sc


def save(sc, path, title):
    """Like Scene.save, but rounds larger coordinates to whole pixels to keep the file small."""
    svg = sc.svg(title)
    svg = re.sub(r"(?<![\d.])(-?\d{2,})\.\d\b", lambda m: str(round(float(m.group(0)))), svg)
    svg = re.sub(r"(?<![\d.])0\.(\d)", r".\1", svg)  # 0.4 -> .4
    with open(path, "w") as fh:
        fh.write(svg)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    save(build(), f"{out}/rivendell.svg", "Rivendell in autumn")
