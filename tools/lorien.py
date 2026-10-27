"""Lothlórien: the Golden Wood.

Enormous silver-grey mallorn trunks rising out of frame under a golden canopy,
talans high in the trees with soft lanterns and a hanging walkway between
them, a white stair winding round the greatest trunk, a clear stream through
the glade, mist and drifting light. Cool silver-blue air, gold in the leaves.
"""
import math
import re
import sys
from scene_kit import Scene, W, H, f

P = dict(
    sky=[(0, "#eef1ef"), (.35, "#e3e9ed"), (.7, "#d9e1e8"), (1, "#d6dde4")], glow="#fbf0c8",
    air="#dfe6ec", mist="#f1f4f6",
    bark_far="#cbd4dc", bark_mid="#b6c2cc", bark_lit="#e7edf2", bark="#a8b5c1", bark_shade="#8b99a7",
    gold="#e2bd55", gold_light="#f7e294", gold_shade="#cba547", gold_pale="#ede0b2",
    wood="#e2e5e2", wood_shade="#b9c1c7", wood_dark="#949ea8", white="#f8f9fa", stair_shade="#c3ccd4",
    lamp="#fff6d8", lamp_glow="#ffe9a8",
    water="#c3d3df", water_light="#f5f8fa", water_dark="#a9bccb",
    grass="#c4cdc4", grass_dark="#aab6ad", ground="#cfd6d6",
    elanor="#e8c13c", niphredil="#ffffff", leaf_fall=["#d8b24a", "#e6c463", "#c99c35"],
)


def mix(a, b, t):
    """Blend hex colour a toward b by t (0..1): used for aerial perspective."""
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def trunk(sc, x, w, yb, fade=0.0, lean=0.0, gid=None, flare=1.0):
    """A mallorn bole rising out of the top of the frame: smooth, silver, flaring into roots at its foot.
    Returns the half-width function so platforms and stairs can be fitted to it."""
    lit, mid, shade = (mix(c, P["air"], fade) for c in (P["bark_lit"], P["bark"], P["bark_shade"]))
    hw = w / 2
    top = -20
    xt = x + lean
    fl = w * .3 * flare
    fy = min(w * .5, 46)  # height of the root flare
    d = (f"M{f(xt - hw * .9)},{top} C{f(xt - hw * .93)},{f(yb * .45)} {f(x - hw)},{f(yb * .7)} {f(x - hw)},{f(yb - fy)} "
         f"Q{f(x - hw - fl * .05)},{f(yb - 2)} {f(x - hw - fl)},{f(yb + 2)} L{f(x + hw + fl)},{f(yb + 2)} "
         f"Q{f(x + hw + fl * .05)},{f(yb - 2)} {f(x + hw)},{f(yb - fy)} C{f(x + hw)},{f(yb * .7)} {f(xt + hw * .93)},{f(yb * .45)} {f(xt + hw * .9)},{top}Z")
    fill = sc.lin(gid, [(0, lit), (.32, mix(lit, mid, .45)), (.7, mid), (1, shade)], x2=1, y2=0) if gid else mid
    sc.add(f'<path d="{d}" fill="{fill}"/>')
    if fade < .5:
        # smooth bark: long faint streaks, and the root buttresses
        streaks = ""
        for _ in range(int(w / 7)):
            sx = sc.r(-hw * .8, hw * .8)
            y0 = sc.r(-10, yb - 120)
            streaks += f"M{f(x + sx + lean * (1 - y0 / yb))},{f(y0)} q{f(sc.r(-2, 2))},{f(sc.r(40, 90))} {f(sc.r(-2, 2))},{f(sc.r(80, 160))}"
        sc.add(f'<path d="{streaks}" stroke="{shade}" stroke-width="1" fill="none" opacity=".35"/>')
        roots = ""
        for k in (-.55, -.15, .3, .7):
            rx = x + hw * k
            roots += f"M{f(rx)},{f(yb - fy * 1.3)} Q{f(rx + k * 4)},{f(yb - 6)} {f(rx + k * fl * 1.3)},{f(yb + 1)}"
        sc.add(f'<path d="{roots}" stroke="{shade}" stroke-width="1.6" fill="none" opacity=".45"/>')
        sc.add(f'<path d="M{f(xt - hw * .55)},{top} C{f(xt - hw * .6)},{f(yb * .5)} {f(x - hw * .62)},{f(yb * .7)} {f(x - hw * .66)},{f(yb - fy * .5)}" stroke="{P["white"]}" stroke-width="{f(w * .06)}" fill="none" opacity=".35"/>')


def bough(sc, x0, y0, x1, y1, w, fade=0.0, bend=-20):
    """A tapering branch from a trunk out to a leaf cluster."""
    col = mix(P["bark"], P["air"], fade)
    lit = mix(P["bark_lit"], P["air"], fade)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + bend
    sc.add(f'<path d="M{f(x0)},{f(y0 - w / 2)} Q{f(mx)},{f(my - w * .3)} {f(x1)},{f(y1)} Q{f(mx)},{f(my + w * .3)} {f(x0)},{f(y0 + w / 2)}Z" fill="{col}"/>'
           f'<path d="M{f(x0)},{f(y0 - w / 2)} Q{f(mx)},{f(my - w * .3)} {f(x1)},{f(y1)}" stroke="{lit}" stroke-width="1.2" fill="none" opacity=".7"/>')


def leafmark(x, y, L, ang, wid=.32):
    """One pointed mallorn leaf as a path fragment, from its stalk at (x, y), length L, pointing at ang."""
    vx, vy = L * math.cos(ang), L * math.sin(ang)
    nx, ny = -vy * wid, vx * wid
    return f"M{f(x)},{f(y)}q{f(vx / 2 + nx)},{f(vy / 2 + ny)} {f(vx)},{f(vy)}q{f(-vx / 2 - nx)},{f(-vy / 2 - ny)} {f(-vx)},{f(-vy)}Z"


def leaves(sc, x, y, s, fade=0.0, n=8, marks=1.0):
    """A cluster of golden mallorn leaves: rounded masses, then sprays of single leaves -
    bright ones catching the light above, hanging ones fringing the lower edge."""
    leaf, light, shade = (mix(c, P["air"], fade) for c in (P["gold"], P["gold_light"], P["gold_shade"]))
    pts = []
    for i in range(n):
        a = sc.r(0, math.pi * 2)
        d = sc.r(0, s * .5)
        pts.append((x + math.cos(a) * d * 1.5, y + math.sin(a) * d * .55, s * sc.r(.26, .42)))
    g = ["".join(f'<ellipse cx="{f(a + r * .08)}" cy="{f(b + r * .16)}" rx="{f(r * .96)}" ry="{f(r * .7)}" fill="{shade}"/>' for a, b, r in pts),
         "".join(f'<ellipse cx="{f(a)}" cy="{f(b)}" rx="{f(r * .9)}" ry="{f(r * .62)}" fill="{leaf}"/>' for a, b, r in pts)]
    L = max(3.6, s * .11)
    hi = lo = fr = ""
    for _ in range(int(s * .45 * marks)):  # sunlit leaves on the upper side
        a = sc.r(0, math.pi * 2)
        d = sc.r(.2, 1) * s * .55
        lx, ly = x + math.cos(a) * d * 1.45, y + math.sin(a) * d * .5 - s * .08
        if ly < y + s * .05:
            hi += leafmark(lx, ly, L * sc.r(.8, 1.2), sc.r(-2.6, -.5))
        else:
            lo += leafmark(lx, ly, L * sc.r(.8, 1.2), sc.r(.3, 2.8))
    for _ in range(int(s * .3 * marks)):  # the hanging fringe
        lx = x + sc.r(-s * .85, s * .85)
        ly = y + s * .2 * (1 - (abs(lx - x) / s) ** 2) + sc.r(-2, 5)
        fr += leafmark(lx, ly, L * sc.r(.9, 1.4), math.pi / 2 + sc.r(-.5, .5))
    g.append(f'<path d="{lo}{fr}" fill="{shade}"/><path d="{fr}" fill="{leaf}" transform="translate(-1 -1)"/><path d="{hi}" fill="{light}"/>')
    sc.add("".join(g))


def spray(sc, x, y0, L, fade=0.0):
    """A drooping strand of mallorn leaves hanging from the canopy."""
    leaf, light, shade = (mix(c, P["air"], fade) for c in (P["gold"], P["gold_light"], P["gold_shade"]))
    sway = sc.r(-14, 14)
    stem = f"M{f(x)},{f(y0)} q{f(sway)},{f(L * .5)} {f(sway * .4)},{f(L)}"
    a = b = ""
    n = int(L / 3.4)
    for i in range(n):
        t = i / n
        px = x + sway * 2 * t * (1 - t) + sway * .4 * t * t
        py = y0 + L * t
        Lf = 7.5 * (1 - t * .4)
        side = 1 if i % 2 else -1
        frag = leafmark(px, py, Lf, math.pi / 2 + side * sc.r(.5, 1.0))
        if sc.r(0, 1) < .5:
            a += frag
        else:
            b += frag
    sc.add(f'<path d="{stem}" stroke="{mix(P["bark"], P["air"], fade)}" stroke-width=".8" fill="none"/><path d="{b}" fill="{shade}"/><path d="{a}" fill="{leaf}"/>'
           f'<path d="{leafmark(x + sway * .4, y0 + L, 6, math.pi / 2)}" fill="{light}"/>')


def canopy_band(sc, y, rmin, rmax, fill, light=None, dapple=.3, x0=-30, x1=W + 30, jitter=6):
    """Foliage hanging from above the frame: a scalloped lower edge, closed to the top."""
    bumps = []
    x = x0
    while x < x1:
        r = sc.r(rmin, rmax)
        bumps.append((x, r, y + sc.r(-jitter, jitter)))
        x += r * 1.5
    d = f"M{f(x0)},-20 L{f(x0)},{f(bumps[0][2])}"
    for bx, r, by in bumps:
        d += f" A{f(r)},{f(r * .8)} 0 0 0 {f(bx + r * 1.5)},{f(by)}"
    d += f" L{f(x)},-20Z"
    sc.add(f'<path d="{d}" fill="{fill}"/>')
    if light:
        sc.add("".join(f'<ellipse cx="{f(bx + r * .7)}" cy="{f(by + r * .25)}" rx="{f(r * .4)}" ry="{f(r * .25)}" fill="{light}" opacity=".8"/>'
                       for bx, r, by in bumps if sc.r(0, 1) < dapple))


def lantern(sc, x, y, hang=8, s=1.0):
    """A small hanging lamp with a soft halo."""
    sc.add(f'<circle cx="{f(x)}" cy="{f(y + hang + 3 * s)}" r="{f(16 * s)}" fill="url(#lampglow)"/>'
           f'<path d="M{f(x)},{f(y)} v{f(hang)}" stroke="{P["wood_dark"]}" stroke-width=".7"/>'
           f'<path d="M{f(x - 2.4 * s)},{f(y + hang + 1)} Q{f(x)},{f(y + hang - 1.5 * s)} {f(x + 2.4 * s)},{f(y + hang + 1)} '
           f'Q{f(x + 2.8 * s)},{f(y + hang + 5 * s)} {f(x)},{f(y + hang + 6.5 * s)} Q{f(x - 2.8 * s)},{f(y + hang + 5 * s)} {f(x - 2.4 * s)},{f(y + hang + 1)}Z" fill="{P["lamp"]}"/>')


def talan(sc, cx, y, rx, fade=0.0, lamps=(), rail=True, under=True):
    """A flet round a trunk, seen from below: a shallow elliptical platform with joists, a rim and a railing of arches."""
    wood, shade, dark = (mix(c, P["air"], fade) for c in (P["wood"], P["wood_shade"], P["wood_dark"]))
    ry = rx * .1
    g = []
    if under:  # curved brackets from the trunk out under the platform
        for k in (-.75, -.4, .4, .75):
            g.append(f'<path d="M{f(cx + rx * k * .35)},{f(y + ry + 18)} Q{f(cx + rx * k * .55)},{f(y + ry + 4)} {f(cx + rx * k)},{f(y + ry * .4)}" stroke="{shade}" stroke-width="2" fill="none"/>')
    g.append(f'<ellipse cx="{f(cx)}" cy="{f(y + 1.5)}" rx="{f(rx)}" ry="{f(ry)}" fill="{shade}"/>')
    joists = "".join(f"M{f(cx)},{f(y + 1.5)} L{f(cx + rx * .97 * math.cos(a))},{f(y + 1.5 + ry * .97 * math.sin(a))}" for a in [i * math.pi / 9 for i in range(1, 9)])
    g.append(f'<path d="{joists}" stroke="{dark}" stroke-width=".8" opacity=".55"/>')
    g.append(f'<path d="M{f(cx - rx)},{f(y + 1.5)} A{f(rx)},{f(ry)} 0 0 0 {f(cx + rx)},{f(y + 1.5)} L{f(cx + rx)},{f(y - 1.5)} A{f(rx)},{f(ry)} 0 0 1 {f(cx - rx)},{f(y - 1.5)}Z" fill="{wood}"/>')
    if rail:
        rh = 7
        d = ""
        n = int(rx / 7)
        for i in range(n + 1):
            a = math.pi * i / n
            px, py = cx - rx * math.cos(a), y - 1.5 + ry * math.sin(a) * .9
            d += f"M{f(px)},{f(py)} v{-rh}"
        g.append(f'<path d="{d}" stroke="{wood}" stroke-width=".9"/>')
        arc = ""
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            p0 = (cx - rx * math.cos(a0), y - 1.5 + ry * math.sin(a0) * .9 - rh)
            p1 = (cx - rx * math.cos(a1), y - 1.5 + ry * math.sin(a1) * .9 - rh)
            arc += f"M{f(p0[0])},{f(p0[1])} Q{f((p0[0] + p1[0]) / 2)},{f((p0[1] + p1[1]) / 2 + 4)} {f(p1[0])},{f(p1[1])}"
        g.append(f'<path d="M{f(cx - rx)},{f(y - 1.5 - rh)} A{f(rx)},{f(ry * .9)} 0 0 0 {f(cx + rx)},{f(y - 1.5 - rh)}" stroke="{wood}" stroke-width="1.3" fill="none"/>')
        g.append(f'<path d="{arc}" stroke="{wood}" stroke-width=".8" fill="none"/>')
    sc.add("".join(g))
    for lx, hang in lamps:
        lantern(sc, cx + lx, y + ry * math.sqrt(max(0, 1 - (lx / rx) ** 2)) + 1, hang)


def pavilion(sc, x, y, w, h, fade=0.0):
    """A pale open pavilion on a talan: slim posts under a leaf-shaped, upswept canopy."""
    wood, shade, white = (mix(c, P["air"], fade) for c in (P["wood"], P["wood_shade"], P["white"]))
    g = []
    posts = "".join(f"M{f(x - w / 2 + i * w / 4)},{f(y)} V{f(y - h)}" for i in range(5))
    g.append(f'<path d="{posts}" stroke="{shade}" stroke-width="1.4"/>')
    g.append(f'<path d="M{f(x - w / 2)},{f(y - h + 5)} Q{f(x - w / 4)},{f(y - h + 12)} {f(x)},{f(y - h + 5)} Q{f(x + w / 4)},{f(y - h + 12)} {f(x + w / 2)},{f(y - h + 5)}" stroke="{wood}" stroke-width="1" fill="none"/>')
    g.append(f'<path d="M{f(x - w * .72)},{f(y - h - 2)} Q{f(x - w * .4)},{f(y - h + 1)} {f(x - w * .1)},{f(y - h - h * .6)} Q{f(x)},{f(y - h - h * .85)} {f(x + w * .1)},{f(y - h - h * .6)} '
             f'Q{f(x + w * .4)},{f(y - h + 1)} {f(x + w * .72)},{f(y - h - 2)} Q{f(x)},{f(y - h + 4)} {f(x - w * .72)},{f(y - h - 2)}Z" fill="{white}"/>')
    g.append(f'<path d="M{f(x + w * .1)},{f(y - h - h * .6)} Q{f(x + w * .4)},{f(y - h + 1)} {f(x + w * .72)},{f(y - h - 2)} Q{f(x + w * .3)},{f(y - h + 1)} {f(x)},{f(y - h)}Z" fill="{shade}" opacity=".5"/>')
    g.append(f'<path d="M{f(x)},{f(y - h - h * .8)} v-6" stroke="{mix(P["gold"], P["air"], fade)}" stroke-width="1"/>')
    sc.add("".join(g))


def stair(sc, cx, hw, y0, y1, turns, phase=0.0):
    """A white stair winding round a trunk of half-width hw from y0 up to y1.
    Draws the part behind the trunk now and returns a function that draws the front part (call it after the trunk)."""
    R = hw * 1.22
    T = turns * math.pi * 2
    n = int(turns * 60)
    pts = []
    for i in range(n + 1):
        t = i / n * T + phase
        pts.append((cx + R * math.sin(t), y0 - (y0 - y1) * i / n, math.cos(t)))

    def ribbon(seg, fill, rail_col):
        if len(seg) < 2:
            return ""
        top = " L".join(f"{f(x)},{f(y)}" for x, y, _ in seg)
        bot = " L".join(f"{f(x)},{f(y + 4.5)}" for x, y, _ in reversed(seg))
        out = f'<path d="M{top} L{bot}Z" fill="{fill}"/>'
        rail = " L".join(f"{f(x)},{f(y - 7)}" for x, y, _ in seg)
        posts = "".join(f"M{f(x)},{f(y)} v-7" for x, y, _ in seg[::4])
        out += f'<path d="M{rail}" stroke="{rail_col}" stroke-width="1" fill="none"/><path d="{posts}" stroke="{rail_col}" stroke-width=".7"/>'
        return out

    def runs(front):
        cur, out = [], []
        for p in pts:
            if (p[2] > 0) == front:
                cur.append(p)
            elif cur:
                out.append(cur)
                cur = []
        if cur:
            out.append(cur)
        return out

    sc.add("".join(ribbon(s, P["stair_shade"], mix(P["stair_shade"], P["wood_dark"], .3)) for s in runs(False)))

    def front():
        g = []
        for s in runs(True):
            g.append(ribbon(s, P["white"], P["white"]))
            # tread lines and the shadow the stair casts on the bark
            g.append(f'<path d="M{" L".join(f"{f(x)},{f(y + 7)}" for x, y, _ in s)}" stroke="{P["bark_shade"]}" stroke-width="2" fill="none" opacity=".3"/>')
            g.append(f'<path d="{"".join(f"M{f(x)},{f(y + .5)} v4" for x, y, _ in s[::2])}" stroke="{P["stair_shade"]}" stroke-width=".7"/>')
        sc.add("".join(g))
    return front


def walkway(sc, x0, y0, x1, y1, sag, fade=0.0):
    """A slender hanging walkway between two talans."""
    wood, shade = mix(P["wood"], P["air"], fade), mix(P["wood_shade"], P["air"], fade)
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    g = [f'<path d="M{f(x0)},{f(y0)} Q{f(xm)},{f(ym)} {f(x1)},{f(y1)}" stroke="{shade}" stroke-width="3.2" fill="none"/>',
         f'<path d="M{f(x0)},{f(y0 - 1)} Q{f(xm)},{f(ym - 1)} {f(x1)},{f(y1 - 1)}" stroke="{wood}" stroke-width="1.6" fill="none"/>',
         f'<path d="M{f(x0)},{f(y0 - 9)} Q{f(xm)},{f(ym - 12)} {f(x1)},{f(y1 - 9)}" stroke="{wood}" stroke-width="1" fill="none"/>']

    def q(t, a, c, b):
        return (1 - t) ** 2 * a + 2 * (1 - t) * t * c + t * t * b
    d = ""
    for i in range(1, 16):
        t = i / 16
        bx, by = q(t, x0, xm, x1), q(t, y0, ym, y1)
        ty = q(t, y0 - 9, ym - 12, y1 - 9)
        d += f"M{f(bx)},{f(by - 1)} L{f(bx)},{f(ty)}"
    g.append(f'<path d="{d}" stroke="{wood}" stroke-width=".7"/>')
    sc.add("".join(g))
    return q


def build(seed=23):
    sc = Scene(seed)
    sc.defs.append(f'<radialGradient id="lampglow"><stop offset="0" stop-color="{P["lamp_glow"]}" stop-opacity=".75"/>'
                   f'<stop offset=".35" stop-color="{P["lamp_glow"]}" stop-opacity=".3"/><stop offset="1" stop-color="{P["lamp_glow"]}" stop-opacity="0"/></radialGradient>')
    sc.sky(sc.lin("sky", P["sky"]))
    # light pouring in from high on the left
    sc.add(f'<ellipse cx="380" cy="30" rx="520" ry="260" fill="{sc.rad("sun", [(0, P["glow"], .7), (.4, P["glow"], .3), (1, P["glow"], 0)])}"/>')

    # ---- the far wood: pale boles and a hazy gold roof ----
    canopy_band(sc, 118, 26, 46, mix(P["gold_pale"], P["air"], .55))
    for i in range(46):
        x = sc.r(-20, W + 20)
        w = sc.r(7, 15)
        sc.add(f'<path d="M{f(x - w * .45)},-10 L{f(x - w / 2)},300 L{f(x + w / 2)},300 L{f(x + w * .45)},-10Z" fill="{mix(P["bark_far"], P["air"], sc.r(.2, .6))}"/>')
    canopy_band(sc, 82, 22, 40, mix(P["gold_pale"], P["air"], .3), mix(P["gold_light"], P["air"], .45), .4)
    sc.add(f'<rect y="120" width="{W}" height="200" fill="{sc.lin("hz1", [(0, P["air"], 0), (.6, P["air"], .7), (1, P["air"], .9)])}"/>')

    # ---- the middle wood ----
    mids = [(40, 34), (300, 30), (548, 26), (880, 36), (1118, 30), (1420, 38), (1590, 28)]
    for i, (x, w) in enumerate(mids):
        trunk(sc, x, w, 286, .45, sc.r(-6, 6), None, .7)
    for x, y, s in [(70, 96, 40), (250, 70, 46), (520, 110, 38), (900, 92, 44), (1090, 120, 36), (1180, 74, 42), (1400, 104, 44), (1560, 84, 38)]:
        leaves(sc, x, y, s, .45, 8, .7)
    talan(sc, 1118, 160, 34, .45, lamps=[(-20, 6), (14, 9)])
    talan(sc, 300, 190, 30, .45, lamps=[(16, 7)])
    talan(sc, 880, 206, 38, .45, lamps=[(-24, 6), (22, 8)])
    pavilion(sc, 892, 204, 26, 14, .45)

    # light shafts slanting down from the canopy
    for x0, w, op in [(240, 60, .28), (420, 34, .22), (760, 80, .26), (1010, 40, .2), (1260, 70, .22), (60, 40, .18)]:
        sc.add(f'<path d="M{x0},-10 L{x0 + w},-10 L{x0 + w + 260},330 L{x0 + 190},330Z" fill="{sc.lin(f"shaft{x0}", [(0, P["glow"], op * 2.2), (.6, P["glow"], op), (1, P["glow"], 0)])}"/>')

    # mist through the glade
    sc.add(f'<rect y="200" width="{W}" height="130" fill="{sc.lin("hz2", [(0, P["mist"], 0), (.5, P["mist"], .6), (1, P["mist"], .85)])}"/>')

    # ---- the stream ----
    sc.ridge(244, 4, [(1.4, 1), (3.7, .4)], mix(P["grass"], P["mist"], .4), seed=1.9)
    sy = 256
    sc.add(f'<path d="M-20,{sy + 6} C200,{sy - 6} 380,{sy + 12} 640,{sy + 2} S1000,{sy - 8} 1240,{sy} S1500,{sy + 6} 1620,{sy - 2} '
           f'L1620,{sy + 10} C1400,{sy + 16} 1260,{sy + 10} 1000,{sy + 14} S640,{sy + 22} 420,{sy + 24} S120,{sy + 18} -20,{sy + 28}Z" fill="{P["water"]}"/>')
    sc.add(f'<path d="M-20,{sy + 6} C200,{sy - 6} 380,{sy + 12} 640,{sy + 2} S1000,{sy - 8} 1240,{sy} S1500,{sy + 6} 1620,{sy - 2}" stroke="{P["water_dark"]}" stroke-width="1.5" fill="none" opacity=".6"/>')
    glints = "".join(f"M{f(x)},{f(sy + 5 + sc.r(0, 12) * (1 if x < 900 else .6))}h{f(sc.r(8, 26))}" for x in [sc.r(0, W) for _ in range(50)])
    sc.add(f'<path d="{glints}" stroke="{P["water_light"]}" stroke-width="1.3" stroke-linecap="round" opacity=".9"/>')
    sc.add("".join(f'<ellipse cx="{f(x)}" cy="{f(sy + 2 + sc.r(4, 18) * (1 - x / 2400))}" rx="{f(sc.r(3, 6))}" ry="{f(sc.r(1.3, 2.4))}" fill="{P["water_dark"]}"/>' for x in [sc.r(0, W) for _ in range(16)]))
    sc.ridge(286, 4, [(1.6, 1), (4.2, .4)], P["grass"], seed=3.1)
    bx0, bx1, by = 520, 600, 268  # a little white footbridge over the stream
    sc.add(f'<path d="M{bx0 - 8},{by + 12} Q{(bx0 + bx1) / 2},{by - 16} {bx1 + 8},{by + 8} L{bx1 + 8},{by + 12} Q{(bx0 + bx1) / 2},{by - 10} {bx0 - 8},{by + 16}Z" fill="{P["white"]}"/>'
           f'<path d="M{bx0 - 2},{by + 14} Q{(bx0 + bx1) / 2},{by - 2} {bx1 + 2},{by + 11}" stroke="{P["stair_shade"]}" stroke-width="1.2" fill="none"/>'
           f'<path d="M{bx0 - 8},{by + 4} Q{(bx0 + bx1) / 2},{by - 24} {bx1 + 8},{by}" stroke="{P["white"]}" stroke-width="1" fill="none"/>'
           + "".join(f'<path d="M{f(x)},{f(by + 10 - 13 * (1 - ((x - (bx0 + bx1) / 2) / 48) ** 2))} v-7" stroke="{P["white"]}" stroke-width=".8"/>' for x in range(bx0, bx1 + 1, 8)))
    for _ in range(18):
        sc.add(f'<ellipse cx="{f(sc.r(-40, W + 40))}" cy="{f(sc.r(240, 290))}" rx="{f(sc.r(60, 150))}" ry="{f(sc.r(5, 10))}" fill="{P["mist"]}" opacity="{f(sc.r(.35, .6))}"/>')

    # ---- the great mallorns ----
    # left: a broad bole with a flet and its ladder of light
    trunk(sc, 150, 78, 300, 0.12, -10, "t0")
    bough(sc, 175, 70, 330, 40, 12, .1, -10)
    bough(sc, 120, 110, 10, 70, 11, .1, -6)
    talan(sc, 146, 150, 92, .08, lamps=[(-70, 8), (-30, 12), (40, 10), (74, 7)])
    pavilion(sc, 110, 148, 30, 16, .08)

    # the second great tree, linked to the first by a walkway
    trunk(sc, 434, 70, 300, .05, 6, "t2")
    bough(sc, 455, 60, 560, 26, 11, .05, -8)
    talan(sc, 434, 176, 82, .03, lamps=[(-60, 9), (-18, 13), (34, 10), (64, 6)])

    # the greatest tree, with the white stair winding up it to the high talan
    cx, w = 712, 104
    front = stair(sc, cx, w / 2, 304, 132, 2.6, -.6)
    trunk(sc, cx, w, 304, 0, -6, "t1", 1.1)
    front()
    bough(sc, 740, 52, 900, 10, 15, 0, -14)
    bough(sc, 680, 70, 560, 36, 13, 0, -10)
    talan(sc, 707, 126, 132, 0, lamps=[(-104, 9), (-60, 14), (-20, 10), (40, 15), (86, 11), (116, 7)])
    pavilion(sc, 650, 124, 48, 22)
    pavilion(sc, 772, 124, 34, 18)
    talan(sc, 704, 40, 80, 0, lamps=[(-50, 7), (52, 9)], rail=True)
    walkway(sc, 516, 176, 575, 124, 26, .03)
    walkway(sc, 220, 150, 400, 176, 22, .06)

    # right: two more boles above the cards, with a high talan and lanterns
    trunk(sc, 1300, 90, 300, .08, 8, "t3")
    bough(sc, 1270, 60, 1130, 20, 13, .06, -12)
    bough(sc, 1330, 90, 1470, 56, 12, .06, -10)
    talan(sc, 1304, 100, 104, .05, lamps=[(-80, 10), (-36, 14), (30, 12), (78, 8)])
    pavilion(sc, 1350, 98, 36, 18, .05)
    talan(sc, 1300, 210, 70, .08, lamps=[(-40, 8), (44, 10)])
    trunk(sc, 1556, 64, 300, .12, -4, "t4")
    walkway(sc, 1408, 100, 1530, 150, 20, .08)
    talan(sc, 1552, 150, 60, .1, lamps=[(-34, 7), (30, 9)])

    # ---- the golden roof: near foliage hanging into the frame ----
    # a thinner roof of leaves just above the frame, with light breaking through
    canopy_band(sc, 2, 18, 34, mix(P["gold"], P["air"], .25), mix(P["gold_light"], P["air"], .2), .6, jitter=10)
    # long sprays of leaves hanging down from the roof
    for x, y0, L in [(90, 30, 70), (262, 20, 84), (395, 40, 60), (586, 24, 76), (868, 26, 90), (1000, 30, 64), (1150, 26, 80),
                     (1420, 30, 72), (1540, 34, 60)]:
        spray(sc, x, y0, L)
    for x, y, s_ in [(30, 44, 60), (190, 22, 52), (340, 46, 62), (520, 20, 54), (640, 46, 48), (800, 18, 58), (930, 40, 64),
                     (1080, 16, 52), (1200, 44, 58), (1360, 20, 56), (1490, 48, 60), (1600, 22, 50), (450, 4, 44), (1290, 0, 46)]:
        leaves(sc, x + sc.r(-10, 10), y, s_, 0, 9)

    # drifting gold leaves and motes of light
    g = []
    for _ in range(70):
        x, y = sc.r(0, W), sc.r(60, 300)
        a = sc.r(-60, 60)
        g.append(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(sc.r(1.6, 2.8))}" ry="{f(sc.r(.8, 1.3))}" transform="rotate({f(a)} {f(x)} {f(y)})" fill="{sc.rnd.choice(P["leaf_fall"])}"/>')
    for _ in range(50):
        g.append(f'<circle cx="{f(sc.r(0, W))}" cy="{f(sc.r(50, 280))}" r="{f(sc.r(.8, 2))}" fill="{P["white"]}" opacity="{f(sc.r(.4, .8))}"/>')
    sc.add("".join(g))

    # ---- the near bank: grass with elanor and niphredil, close to the page colour ----
    sc.ridge(312, 5, [(1.7, 1), (4.4, .5)], P["grass"], seed=4.4)
    for x, w in [(150, 78), (434, 70), (712, 104), (1300, 90), (1556, 64)]:  # drifts of fallen gold round the roots
        sc.add(f'<ellipse cx="{x}" cy="305" rx="{f(w * 1.1)}" ry="4.5" fill="{P["gold_pale"]}" opacity=".45"/>')
        sc.flowers(300, 312, 14, P["leaf_fall"], 1.1, 2.0, x - w, x + w)
    sc.tufts(306, 360, 120, [P["grass_dark"], "#b8c2b8", "#c9cfc2", "#b2bdb6"], 5, 13)
    stars = ""
    for _ in range(46):  # elanor: little golden stars
        x, y, r = sc.r(0, W), sc.r(312, 372), sc.r(1.6, 2.6)
        stars += "M" + " L".join(f"{f(x + (r if k % 2 == 0 else r * .45) * math.cos(k * math.pi / 5 - math.pi / 2))},{f(y + (r if k % 2 == 0 else r * .45) * math.sin(k * math.pi / 5 - math.pi / 2))}" for k in range(10)) + "Z"
    sc.add(f'<path d="{stars}" fill="{P["elanor"]}"/>')
    sc.flowers(314, 372, 50, [P["niphredil"]], 1.2, 2.0)
    sc.flowers(316, 380, 50, P["leaf_fall"], 1.2, 2.2)
    sc.add(f'<rect y="290" width="{W}" height="110" fill="{sc.lin("hz3", [(0, "#d6dce2", 0), (1, "#d6dce2", .7)])}"/>')
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
    save(build(), f"{out}/lorien.svg", "Lothlórien, the Golden Wood")
