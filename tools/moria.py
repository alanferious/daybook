"""Moria: the Dwarrowdelf, the great pillared hall under the mountain.

We stand in the middle aisle of the hall. Rows of square-cut pillars carved with
angular dwarf work march away from us in perspective and climb into the dark,
where they flare into stepped vaults; pale shafts of light fall from high
windows, dust turning in them, glints of gold in the carving and on the floor.
The hall ends at a chasm, and beyond it a thin stone bridge without a rail
crosses the deep in the grey light.
"""
import math
import sys
from scene_kit import Scene, W, H, f

# the camera: vanishing point, focal length (px), eye height (world units, about a dwarf's height each)
VX, VY, FL, HC = 712, 215, 220, 3.2
PW = 3.2                       # pillar width
TOP = 30.0                     # where the pillars meet the vault
COLS = [-107, -96, -85, -74, -63, -52, -41, -30, -19, -8, 8, 19, 30, 41, 52, 63, 74, 85, 96, 107]
ROWS = [24, 34, 44, 54]
EDGE = 60                      # the hall floor ends at the chasm
BRIDGE_Z, BRIDGE_Y = 74, 9.5
BROKEN = (-8, 34)            # the pillar that has fallen   # the bridge crosses the deep here, this high above our floor

C = dict(
    bg="#0f0f11", void="#070708",
    haze="#3a3b42", fog="#3a3b41",
    stone="#181716", stone_side="#0e0e0f", stone_lit="#a29d90", vault="#1d1c1f",
    floor_far="#28282d", floor_near="#0f0f11",
    shaft="#e4e6e3", dust="#f1efe6", gold="#d6b05a", gold_hi="#f3d98f",
)

# where the light falls: (X, Z, strength); shafts lean left as they fall
SHAFTS = [(0.0, 29, 1.0), (13.0, 49, .75), (-13.5, 39, .6), (24.0, 57, .5), (57.0, 31, .6), (-30.0, 19, .8), (47.0, 20, .65), (11.0, 16, .5)]
LEAN = .42


def sx(X, Z):
    return VX + X * FL / Z


def sy(Y, Z):
    return VY + (HC - Y) * FL / Z


def hexrgb(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    A, B = hexrgb(a), hexrgb(b)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(A, B))


def poly(pts):
    return "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + "Z"


def light_at(X, Z):
    v = 0.0
    for lx, lz, s in SHAFTS:
        d2 = (X - lx) ** 2 + ((Z - lz) * .8) ** 2
        v += s * math.exp(-d2 / 200)
    return min(1.0, v)


def fog_at(Z):
    return 1 - math.exp(-(Z - 12) / 30)


def carving_defs(sc):
    """The carved face of a pillar, drawn once in world units (x across, y up as negative) and reused at every pillar."""
    hw = PW / 2
    sw = .045
    g = ['<g id="cv">']
    bands = [(4.6, 5.6), (12.4, 13.4), (19.4, 20.2), (25.6, 26.4)]
    for y0, y1 in bands:
        g.append(f'<rect x="{f(-hw)}" y="{f(-y1)}" width="{f(PW)}" height="{f(y1 - y0)}" fill="#000" opacity=".25"/>')
    dd = ""
    k = 5
    seg = PW / k
    for y0, y1 in bands:
        a, b = -y1, -y0
        m = (a + b) / 2
        for i in range(k):
            x0 = -hw + i * seg
            dd += f"M{f(x0)},{b:.2f}H{x0 + seg * .25:.2f}V{m:.2f}L{x0 + seg * .5:.2f},{a:.2f}L{x0 + seg * .75:.2f},{m:.2f}V{b:.2f}H{x0 + seg:.2f}"
    # the long recessed panel with its chain of stepped diamonds
    pa, pb = -11.6, -6.4
    pm = PW * .18
    g.append(f'<rect x="{f(-hw + pm)}" y="{pa}" width="{f(PW - 2 * pm)}" height="{f(pb - pa)}" fill="#000" opacity=".2"/>')
    hwid = (PW - 2 * pm) * .4
    nd = 3
    hh = (pb - pa) / nd
    for i in range(nd):
        cy = pa + hh * (i + .5)
        for q in (.47, .27):
            dd += f"M0,{cy - hh * q:.2f}L{hwid * q * 2.1:.2f},{cy:.2f}L0,{cy + hh * q:.2f}L{-hwid * q * 2.1:.2f},{cy:.2f}Z"
    # fluting between the upper bands
    for t in (-.25, 0, .25):
        dd += f"M{PW * t:.2f},-19.2V-13.6"
    g.append(f'<path d="{dd}" fill="none" stroke="#000" stroke-width="{sw}"/>')
    g.append('</g>')
    # gold set into the bands and the panel, where the light reaches it
    gd = ['<g id="gd">']
    gl = ""
    for y0, y1 in bands:
        gl += f"M{f(-hw)},{-y1 + .1:.2f}H{f(hw)}M{f(-hw)},{-y0 - .1:.2f}H{f(hw)}"
    gd.append(f'<path d="{gl}" stroke="{C["gold"]}" stroke-width=".06"/>')
    for i in range(nd):
        gd.append(f'<circle cy="{pa + hh * (i + .5):.2f}" r=".09" fill="{C["gold_hi"]}"/>')
    gd.append('</g>')
    sc.defs.append("".join(g) + "".join(gd))


def pillar(sc, X, Z, broken=None):
    """A square pillar centred at (X, Z). broken: the world height it snapped off at."""
    hw = PW / 2
    zn, zf = Z - hw, Z + hw
    lit = light_at(X, Z)
    fog = fog_at(Z)
    front = mix(mix(C["stone"], C["stone_lit"], lit * .62), C["fog"], fog * .85)
    side = mix(mix(C["stone_side"], C["stone"], lit * .6), C["fog"], fog * .7)
    dark = mix(front, "#000000", .3)
    top_y = sy(broken, zn) if broken else -40
    xl, xr = sx(X - hw, zn), sx(X + hw, zn)
    pw = xr - xl
    yb = sy(0, zn)
    g = []
    # the side we can see is the one facing the aisle
    ex = X + hw if X < 0 else X - hw
    sxn, sxf = sx(ex, zn), sx(ex, zf)
    tyn = sy(broken, zn) if broken else -40
    tyf = sy(broken, zf) if broken else -40
    g.append(f'<path d="{poly([(sxn, tyn), (sxf, tyf), (sxf, sy(0, zf)), (sxn, yb)])}" fill="{side}"/>')
    if pw > 6:
        sw = max(.4, min(2.0, 30 / Z))
        lines = ""
        for Y in [1.6, 4.6, 5.6, 12.4, 13.4, 19.4, 20.2, 25.6, 26.4]:
            if broken and Y > broken:
                continue
            lines += f"M{f(sxn)},{f(sy(Y, zn))}L{f(sxf)},{f(sy(Y, zf))}"
        g.append(f'<path d="{lines}" stroke="#000" stroke-opacity=".4" stroke-width="{f(sw)}"/>')
    # the face toward us
    k = FL / zn
    cx = (xl + xr) / 2
    tr = f'transform="translate({f(cx)},{f(yb)}) scale({k:.3f})"'
    so = .6 * (1 - fog * .8)
    if broken:
        n = 7
        jag = [(xl + pw * i / n, top_y + (sc.r(-1, 1) * .1 + (i % 2) * .09 - .08 * (i / n)) * pw) for i in range(n + 1)]
        shape = poly(jag + [(xr, yb), (xl, yb)])
        sc.defs.append(f'<clipPath id="brk"><path d="{shape}"/></clipPath>')
        g.append(f'<path d="{shape}" fill="{front}"/>')
        g.append(f'<g clip-path="url(#brk)"><use href="#cv" {tr} opacity="{f(so)}"/></g>')
        g.append(f'<path d="{poly(jag + [(xr, jag[-1][1] + pw * .05), (xl, jag[0][1] + pw * .05)])}" fill="{C["stone_lit"]}" opacity="{f(.15 + lit * .3)}"/>')
    else:
        g.append(f'<rect x="{f(xl)}" y="-40" width="{f(pw)}" height="{f(yb + 40)}" fill="{front}"/>')
        if pw > 5:
            g.append(f'<use href="#cv" {tr} opacity="{f(so)}"/>')
            if lit > .25:
                g.append(f'<use href="#gd" {tr} opacity="{f(min(1, lit * 1.1))}"/>')
    # light raking the edge that faces the aisle
    if lit > .12:
        ew = pw * .07
        ex_x = xr - ew if X < 0 else xl
        g.append(f'<rect x="{f(ex_x)}" y="{f(top_y)}" width="{f(ew)}" height="{f(yb - top_y)}" fill="{C["stone_lit"]}" opacity="{f(lit * .4)}"/>')
    # plinth: a wider block at the foot
    pz = zn - .4
    px0, px1 = sx(X - hw - .4, pz), sx(X + hw + .4, pz)
    pyb, pyt = sy(0, pz), sy(1.6, pz)
    g.append(f'<rect x="{f(px0)}" y="{f(pyt)}" width="{f(px1 - px0)}" height="{f(pyb - pyt)}" fill="{dark}"/>')
    g.append(f'<rect x="{f(px0)}" y="{f(pyt)}" width="{f(px1 - px0)}" height="{f(max(.6, (pyb - pyt) * .12))}" fill="{mix(front, C["stone_lit"], .25)}"/>')
    # the dark coming down from the vault, in canvas space
    x0, x1 = min(xl, sxn, sxf), max(xr, sxn, sxf)
    g.append(f'<rect x="{f(x0)}" y="{f(top_y - 6)}" width="{f(x1 - x0)}" height="{f(yb - top_y + 6)}" fill="url(#vault)"/>')
    sc.add("".join(g))


def extent(X, Z):
    hw = PW / 2
    zn, zf = Z - hw, Z + hw
    ex = X + hw if X < 0 else X - hw
    xs = [sx(X - hw - .4, zn - .4), sx(X + hw + .4, zn - .4), sx(ex, zf)]
    return min(xs), max(xs)


def hidden(X, Z):
    """True when a nearer, whole pillar stands squarely in front of this one."""
    a0, a1 = extent(X, Z)
    for Zq in ROWS:
        if Zq >= Z:
            continue
        for Xq in COLS:
            if (Xq, Zq) == BROKEN:
                continue
            b0, b1 = sx(Xq - PW / 2, Zq - PW / 2), sx(Xq + PW / 2, Zq - PW / 2)
            if b0 <= a0 and a1 <= b1:
                return True
    return False


def vault(sc, Z):
    """The stepped vault the row of pillars at Z holds up: a band across the hall with angular arches."""
    zn = Z - PW / 2
    fog = fog_at(Z)
    col = mix(C["vault"], C["fog"], fog * .7)
    hw = PW / 2
    # bottom edge of the band, walking across each opening between pillars
    pts = []
    xs = [-120] + COLS + [120]
    for a, b in zip(xs, xs[1:]):
        l, r = a + hw, b - hw
        d = r - l
        for X, Y in [(l, TOP - 4.5), (l + .12 * d, TOP - 3.2), (l + .12 * d, TOP - 2.2), (l + .28 * d, TOP - .8), (l + .42 * d, TOP),
                     (r - .42 * d, TOP), (r - .28 * d, TOP - .8), (r - .12 * d, TOP - 2.2), (r - .12 * d, TOP - 3.2), (r, TOP - 4.5)]:
            pts.append((sx(X, zn), sy(Y, zn)))
    ytop = sy(TOP + 9, zn)
    sc.add(f'<path d="{poly([(pts[0][0], ytop)] + pts + [(pts[-1][0], ytop)])}" fill="{col}"/>')
    # a lit lip along the arches and a carved course above them
    sc.add(f'<path d="M' + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + f'" fill="none" stroke="{C["stone_lit"]}" stroke-opacity="{f(.12 + .1 * (1 - fog))}" stroke-width="{f(max(.5, 20 / Z))}"/>')
    yc = sy(TOP + 1.6, zn)
    sc.add(f'<path d="M{f(pts[0][0])},{f(yc)} H{f(pts[-1][0])}" stroke="#000" stroke-opacity=".35" stroke-width="{f(max(.5, 30 / Z))}"/>')
    sc.add(f'<rect x="{f(pts[0][0])}" y="{f(ytop)}" width="{f(pts[-1][0] - pts[0][0])}" height="{f(sy(TOP - 4.5, zn) - ytop + 2)}" fill="url(#vault)"/>')


def shaft(sc, X, Z, s):
    """A pale shaft from a high window, landing on the floor at (X, Z)."""
    fx, fy = sx(X, Z), sy(0, Z)
    wf = (4.6 if s >= 1 else 3.4) * FL / Z
    top = -10
    tx = fx + (fy - top) * LEAN
    wt = wf * 1.5
    gid = f"sh{abs(int(X * 10))}{Z}"
    sc.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                   f'<stop offset="0" stop-color="{C["shaft"]}" stop-opacity="{f(.4 * s)}"/>'
                   f'<stop offset=".55" stop-color="{C["shaft"]}" stop-opacity="{f(.19 * s)}"/>'
                   f'<stop offset="1" stop-color="{C["shaft"]}" stop-opacity="{f(.13 * s)}"/></linearGradient>')
    beam = sc.fx("beam")
    beam.__enter__()
    sc.add(f'<path d="{poly([(tx - wt / 2, top), (tx + wt / 2, top), (fx + wf / 2, fy), (fx - wf / 2, fy)])}" fill="url(#{gid})"/>')
    sc.add(f'<path d="{poly([(tx - wt * .16, top), (tx + wt * .2, top), (fx + wf * .14, fy), (fx - wf * .1, fy)])}" fill="{C["shaft"]}" opacity="{f(.07 * s)}"/>')
    # the pool where it lands
    rx = 5.0 * FL / Z
    ry = 5.0 * FL * HC / (Z * Z) * 1.2
    sc.add(f'<ellipse cx="{f(fx)}" cy="{f(fy)}" rx="{f(rx)}" ry="{f(ry)}" fill="url(#pool)" opacity="{f(s)}"/>')
    beam.__exit__(None, None, None)
    # dust turning in the light
    g = [f'<g class="fx fx-embers" fill="{C["dust"]}">']
    for _ in range(int(80 * s)):
        t = sc.r(.04, 1) ** .7
        y = top + (fy - top) * t
        cx = tx + (fx - tx) * t
        ww = wt + (wf - wt) * t
        g.append(f'<circle cx="{f(cx + sc.r(-.55, .55) * ww)}" cy="{f(y)}" r="{f(sc.r(.35, 1.05))}" opacity="{f(sc.r(.15, .65) * s)}"/>')
    g.append("</g>")
    sc.add("".join(g))


def sparkle(sc, x, y, s, col, op=1.0):
    k = .2
    sc.add(f'<path d="M{f(x)},{f(y - s)} L{f(x + s * k)},{f(y - s * k)} L{f(x + s)},{f(y)} L{f(x + s * k)},{f(y + s * k)} L{f(x)},{f(y + s)} '
           f'L{f(x - s * k)},{f(y + s * k)} L{f(x - s)},{f(y)} L{f(x - s * k)},{f(y - s * k)}Z" fill="{col}" opacity="{f(op)}"/>')


def rubble(sc):
    """Drums of the broken pillar fallen across the floor, and loose blocks."""
    lit = light_at(-8, 35)
    fill = mix(mix(C["stone"], C["stone_lit"], lit * .45), C["fog"], fog_at(35) * .85)
    shade = mix(fill, "#000000", .4)
    g = []
    blocks = [(-8.5 + sc.r(-5, 4.5), sc.r(31, 38), sc.r(.3, .9)) for _ in range(16)]
    blocks.sort(key=lambda b: -b[1])
    for X, Z, s0 in blocks[:8]:
        s = s0 * FL / Z
        x, y = sx(X, Z), sy(0, Z)
        g.append(f'<path d="{poly([(x - s, y), (x - s * .8, y - s * .9), (x + s * .4, y - s), (x + s, y - s * .3), (x + s, y)])}" fill="{mix(fill, "#000000", sc.r(.05, .35))}"/>')
    for X, Z, r, ln in [(-9.0, 37.5, 1.5, 3.2), (-4.6, 32.5, 1.5, 3.8)]:
        x0, x1 = sx(X - ln / 2, Z), sx(X + ln / 2, Z)
        yb = sy(0, Z)
        h = 2 * r * FL / Z
        g.append(f'<rect x="{f(x0)}" y="{f(yb - h)}" width="{f(x1 - x0)}" height="{f(h)}" fill="{fill}"/>')
        g.append(f'<rect x="{f(x0)}" y="{f(yb - h * .38)}" width="{f(x1 - x0)}" height="{f(h * .38)}" fill="{shade}"/>')
        g.append(f'<rect x="{f(x0)}" y="{f(yb - h)}" width="{f(x1 - x0)}" height="{f(h * .1)}" fill="{C["stone_lit"]}" opacity="{f(.15 + lit * .25)}"/>')
        # the snapped end, and a carved band running round the drum
        g.append(f'<ellipse cx="{f(x1)}" cy="{f(yb - h / 2)}" rx="{f(h * .16)}" ry="{f(h / 2)}" fill="{shade}"/>')
        bx = x0 + (x1 - x0) * .32
        g.append(f'<path d="M{f(bx)},{f(yb - h)} v{f(h)} M{f(bx + 4)},{f(yb - h)} v{f(h)}" stroke="#000" stroke-opacity=".4" stroke-width="1"/>')
    for X, Z, s0 in blocks[8:]:
        s = s0 * FL / Z
        x, y = sx(X, Z), sy(0, Z)
        g.append(f'<path d="{poly([(x - s, y), (x - s * .7, y - s * .8), (x + s * .5, y - s * .9), (x + s, y)])}" fill="{mix(fill, "#000000", sc.r(.05, .4))}"/>')
    sc.add("".join(g))


def bucket(Z):
    """Which depth plane a thing at distance Z belongs to."""
    return "far" if Z >= 42 else "mid" if Z >= 30 else "near" if Z >= 15 else "front"


DEPTH = dict(far=.15, mid=.35, near=.6, front=1)


def stone_fill(X, Z, dark=0.0):
    lit = light_at(X, Z)
    return mix(mix(mix(C["stone"], C["stone_lit"], lit * .5), C["fog"], fog_at(max(Z, 12)) * .8), "#000000", dark)


def pebble(sc, X, Z, s0):
    """A loose stone on the floor, lit on top where the light reaches."""
    s = s0 * FL / Z
    x, y = sx(X, Z), sy(0, Z)
    rnd = sc.r
    pts = [(x - s, y), (x - s * rnd(.6, .9), y - s * rnd(.5, .8)), (x + s * rnd(-.2, .3), y - s * rnd(.7, 1)), (x + s * rnd(.6, .9), y - s * rnd(.3, .6)), (x + s, y)]
    top = pts[1:4] + [(pts[3][0] - s * .2, pts[3][1] + s * .2), (pts[1][0] + s * .2, pts[1][1] + s * .25)]
    lit = light_at(X, Z)
    sc.add(f'<path d="{poly(pts)}" fill="{stone_fill(X, Z, rnd(.15, .4))}"/>'
           + (f'<path d="{poly(top)}" fill="{C["stone_lit"]}" opacity="{f(.12 + lit * .45)}"/>' if s > 2 else ""))


def drum(sc, cx, cz, ang, ln, hw=1.3, ht=2.6, cut_near=True):
    """One square drum of a fallen pillar lying on the floor: centre (cx, cz), axis angle ang (radians from +X), length ln."""
    dx, dz = math.cos(ang), math.sin(ang)
    nx, nz = dz, -dx
    if cx * nx + cz * nz > 0:          # the long side turned toward us
        nx, nz = -nx, -nz

    def P(t, side, Y):                 # t in [-.5, .5] along the axis
        X = cx + dx * ln * t + nx * hw * side
        Z = cz + dz * ln * t + nz * hw * side
        return sx(X, Z), sy(Y, Z)
    lit = light_at(cx, cz)
    face = stone_fill(cx, cz, .12)
    g = [f'<path d="{poly([P(-.5, 1, 0), P(.5, 1, 0), P(.5, 1, ht), P(-.5, 1, ht)])}" fill="{face}"/>',
         f'<path d="{poly([P(-.5, 1, ht), P(.5, 1, ht), P(.5, -1, ht), P(-.5, -1, ht)])}" fill="{mix(face, C["stone_lit"], .3 + lit * .4)}"/>']
    # the carved face: bands at both ends and a sunk panel with diamonds between
    bands = ""
    for t in (-.4, -.33, .33, .4):
        (x0, y0), (x1, y1), (x2, y2) = P(t, 1, 0), P(t, 1, ht), P(t, -1, ht)
        bands += f"M{f(x0)},{f(y0)}L{f(x1)},{f(y1)}L{f(x2)},{f(y2)}"
    g.append(f'<path d="{bands}" fill="none" stroke="#000" stroke-opacity=".45" stroke-width="1.1"/>')
    g.append(f'<path d="{poly([P(-.24, 1, ht * .2), P(.24, 1, ht * .2), P(.24, 1, ht * .8), P(-.24, 1, ht * .8)])}" fill="#000" opacity=".22"/>')
    dia = ""
    for t in (-.12, .12):
        (ax_, ay_), (bx_, by_), (cx_, cy_), (ex_, ey_) = P(t - .08, 1, ht * .5), P(t, 1, ht * .72), P(t + .08, 1, ht * .5), P(t, 1, ht * .28)
        dia += f"M{f(ax_)},{f(ay_)}L{f(bx_)},{f(by_)}L{f(cx_)},{f(cy_)}L{f(ex_)},{f(ey_)}Z"
    g.append(f'<path d="{dia}" fill="none" stroke="#000" stroke-opacity=".5" stroke-width=".9"/>')
    for t in (-.365, .365):
        (x0, y0), (x1, y1) = P(t, 1, 0), P(t, 1, ht)
        g.append(f'<path d="M{f(x0)},{f(y0)}L{f(x1)},{f(y1)}" stroke="{C["gold"]}" stroke-width="1" opacity="{f(.25 + lit * .6)}"/>')
    # the snapped ends: whichever faces us shows its broken section
    for end in (-.5, .5):
        ex, ez = cx + dx * ln * end, cz + dz * ln * end
        if (dx * end) * ex + (dz * end) * ez < 0:
            cap = [P(end, 1, 0), P(end, 1, ht * .5), P(end, 1, ht), P(end, -1, ht), P(end, -1, ht * .55), P(end, -1, 0)]
            cap = [(x + sc.r(-1.2, 1.2), y + sc.r(-1.2, 1.2)) for x, y in cap]
            g.append(f'<path d="{poly(cap)}" fill="{mix(face, "#000000", .3)}"/>')
            g.append(f'<path d="{poly(cap[1:4] + [(cap[3][0] + 2, cap[3][1] + 4), (cap[1][0] - 1, cap[1][1] + 3)])}" fill="{C["stone_lit"]}" opacity="{f(.12 + lit * .3)}"/>')
    sc.add("".join(g))


def fallen_pillar(sc):
    """A pillar that came down across the floor and broke into drums, which rolled a little apart."""
    # far end first: the pillar's plinth, still square, then the shaft broken in two, then a loose drum
    drum(sc, -25.2, 21.0, 2.8, 1.8, hw=1.9, ht=3.0)
    for cx, cz, ang, ln in [(-19.0, 18.4, 2.76, 9.6), (-10.6, 14.6, 2.9, 6.4)]:
        drum(sc, cx, cz, ang, ln)
    for _ in range(14):
        t = sc.r(0, 1)
        pebble(sc, -6 - 18 * t + sc.r(-2, 2), 12.5 + 8 * t + sc.r(-2, 2), sc.r(.2, .55))


def well(sc, Xw, Zw, R=2.6, hw=.8):
    """A round stone well-head: the low parapet, its lit rim, and the black shaft inside."""
    def ring(r, Y, a0=0, a1=360, n=48):
        out = []
        for i in range(n + 1):
            t = math.radians(a0 + (a1 - a0) * i / n)
            X, Z = Xw + r * math.cos(t), Zw + r * math.sin(t)
            out.append((sx(X, Z), sy(Y, Z)))
        return out
    lit = light_at(Xw, Zw)
    face = stone_fill(Xw, Zw, .05)
    g = []
    # the rim seen from above, the black shaft inside it, and the far inner wall going down into the dark
    g.append(f'<path d="{poly(ring(R, hw))}" fill="{mix(face, C["stone_lit"], .2 + lit * .3)}"/>')
    hole = poly(ring(R - .45, hw))
    sc.defs.append(f'<clipPath id="wellhole"><path d="{hole}"/></clipPath>')
    g.append(f'<path d="{hole}" fill="#050506"/>')
    inner_back = ring(R - .45, hw, 0, 180, 24) + list(reversed(ring(R - .45, hw - 1.4, 0, 180, 24)))
    g.append(f'<path d="{poly(inner_back)}" fill="{mix(face, "#000000", .45)}" clip-path="url(#wellhole)"/>')
    # the front of the parapet: the near half of the outer wall, in blocks
    front = ring(R, hw, 180, 360, 24) + list(reversed(ring(R, 0, 180, 360, 24)))
    g.append(f'<path d="{poly(front)}" fill="{face}"/>')
    joints = ""
    for i in range(1, 9):
        t = math.radians(180 + i * 180 / 9)
        X, Z = Xw + R * math.cos(t), Zw + R * math.sin(t)
        joints += f"M{f(sx(X, Z))},{f(sy(0, Z))}V{f(sy(hw, Z))}"
    mid = ring(R, hw * .5, 180, 360, 24)
    joints += "M" + "L".join(f"{f(x)},{f(y)}" for x, y in mid)
    g.append(f'<path d="{joints}" fill="none" stroke="#000" stroke-opacity=".45" stroke-width="1"/>')
    # rim catching the light, a band of gold set into it
    g.append(f'<path d="M' + "L".join(f"{f(x)},{f(y)}" for x, y in ring(R, hw, 180, 360, 24)) + f'" fill="none" stroke="{C["stone_lit"]}" stroke-width="1.6" opacity="{f(.35 + lit * .5)}"/>')
    g.append(f'<path d="M' + "L".join(f"{f(x)},{f(y)}" for x, y in ring(R, hw * .7, 195, 345, 20)) + f'" fill="none" stroke="{C["gold"]}" stroke-width=".9" opacity="{f(.25 + lit * .6)}"/>')
    sc.add("".join(g))
    # a hit area over the well-head
    sc.add(f'<ellipse cx="{f(sx(Xw, Zw))}" cy="{f(sy(1.2, Zw))}" rx="{f(R * FL / Zw * 1.15)}" ry="{f(R * FL / Zw * .6)}" fill="#000" fill-opacity="0"/>')


def runes(sc, X, Z):
    """Rune-work cut into the pillar's upper face, hidden until lit: angular staves between the fluting."""
    hw = PW / 2
    zn = Z - hw
    k = FL / zn
    cx = (sx(X - hw, zn) + sx(X + hw, zn)) / 2
    d = ""
    for lane in range(4):
        lx = -1.2 + lane * .8
        for row in range(3):
            y0 = -18.8 + row * 1.8
            d += f"M{lx:.2f},{y0:.2f}v1.25"
            kind = sc.rnd.randrange(5)
            if kind == 0:
                d += f"M{lx:.2f},{y0 + .1:.2f}l.25,.35M{lx:.2f},{y0 + .1:.2f}l-.25,.35"
            elif kind == 1:
                d += f"M{lx:.2f},{y0 + .3:.2f}l.25,-.25M{lx:.2f},{y0 + .7:.2f}l.25,-.25"
            elif kind == 2:
                d += f"M{lx - .25:.2f},{y0 + .45:.2f}l.25,.3l.25,-.3"
            elif kind == 3:
                d += f"M{lx:.2f},{y0 + .2:.2f}l-.25,.3l.25,.3"
            else:
                d += f"M{lx - .25:.2f},{y0 + .2:.2f}l.5,.6M{lx + .25:.2f},{y0 + .2:.2f}l-.5,.6"
    for y0 in (-13.15, -5.35):  # runes along a band too
        for i in range(5):
            lx = -1.3 + i * .65
            d += f"M{lx:.2f},{y0:.2f}l.2,.6l.2,-.6"
    tr = f'transform="translate({f(cx)},{f(sy(0, zn))}) scale({k:.3f})"'
    sc.add(f'<g class="on-lit" {tr} fill="none" stroke-linecap="round" stroke-linejoin="round">'
           f'<path d="{d}" stroke="#bfe0ff" stroke-width=".32" opacity=".28"/><path d="{d}" stroke="#eef7ff" stroke-width=".09"/></g>')
    # a faint glow on the stone round the runes
    sc.add(f'<ellipse class="on-lit" cx="{f(cx)}" cy="{f(sy(16.4, zn))}" rx="{f(PW * k * .55)}" ry="{f(4.2 * k)}" fill="#bfe0ff" opacity=".12"/>')


def build(seed=11):
    sc = Scene(seed)
    sc.defs.append(f'<linearGradient id="vault" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{H}">'
                   f'<stop offset="0" stop-color="{C["void"]}" stop-opacity=".96"/><stop offset=".14" stop-color="{C["void"]}" stop-opacity=".72"/>'
                   f'<stop offset=".34" stop-color="{C["void"]}" stop-opacity=".25"/><stop offset=".48" stop-color="{C["void"]}" stop-opacity="0"/>'
                   f'<stop offset=".62" stop-color="{C["void"]}" stop-opacity="0"/><stop offset="1" stop-color="{C["void"]}" stop-opacity=".7"/></linearGradient>')
    sc.defs.append(f'<radialGradient id="pool"><stop offset="0" stop-color="{C["shaft"]}" stop-opacity=".42"/>'
                   f'<stop offset=".5" stop-color="{C["shaft"]}" stop-opacity=".1"/><stop offset="1" stop-color="{C["shaft"]}" stop-opacity="0"/></radialGradient>')
    carving_defs(sc)
    ye = sy(0, EDGE)

    # ================= the deep: the far wall beyond the chasm, and the bridge =================
    with sc.layer("deep", 0):
        sc.add(f'<rect x="-30" y="-30" width="{W + 60}" height="{H + 60}" fill="{C["void"]}"/>')
        sc.add(f'<ellipse cx="{VX}" cy="{VY - 10}" rx="420" ry="190" fill="{sc.rad("glow", [(0, "#4a4b52", 1), (.45, C["haze"], .5), (1, C["haze"], 0)])}"/>')
        fz = 96
        cliff = []
        for i in range(61):
            X = -110 + i * 220 / 60
            Y = BRIDGE_Y - .4 + .7 * math.sin(i * 1.7) + .5 * math.sin(i * .6 + 1)
            cliff.append((sx(X, fz), sy(Y, fz)))
        ced = " ".join(f"L{f(a)},{f(b)}" for a, b in reversed(cliff))
        sc.add(f'<path d="M{f(cliff[0][0])},-10 L{f(cliff[-1][0])},-10 L{f(cliff[-1][0])},{f(cliff[-1][1])} {ced}Z" '
               f'fill="{sc.lin("cliffg", [(0, "#141416"), (.6, "#33343a"), (1, "#45464c")])}"/>')
        for Y in (14, 19, 25):
            y = sy(Y, fz)
            sc.add(f'<path d="M{f(sx(-110, fz))},{f(y)} H{f(sx(110, fz))}" stroke="#000" stroke-opacity=".3" stroke-width=".8"/>')
        dx0, dx1 = sx(-2.2, fz), sx(2.2, fz)
        dyt, dyb = sy(BRIDGE_Y + 7, fz), sy(BRIDGE_Y, fz)
        ch = (dx1 - dx0) * .3
        sc.add(f'<path d="{poly([(dx0, dyb), (dx0, dyt + ch), (dx0 + ch, dyt), (dx1 - ch, dyt), (dx1, dyt + ch), (dx1, dyb)])}" fill="#0c0c0e"/>')
        sc.add(f'<path d="M' + " ".join(f"L{f(a)},{f(b)}" for a, b in cliff)[1:] +
               f' L{f(cliff[-1][0])},{f(ye + 4)} L{f(cliff[0][0])},{f(ye + 4)}Z" fill="{sc.lin("abyss", [(0, "#2a2b30"), (.35, "#121214"), (1, C["void"])])}"/>')
        # pale light rising out of the deep behind the bridge, so the span stands out dark against it
        bxs = sx(-2, 84)
        yd = sy(BRIDGE_Y, BRIDGE_Z)
        sc.add(f'<path d="{poly([(bxs + 52, -10), (bxs + 84, -10), (bxs + 12, ye), (bxs - 8, ye)])}" fill="{C["shaft"]}" opacity=".07"/>')
        sc.add(f'<ellipse cx="{f(VX)}" cy="{f(yd + 12)}" rx="170" ry="22" fill="{sc.rad("deepglow", [(0, "#a3a4aa", .7), (.5, "#76777c", .3), (1, "#6a6b70", 0)])}"/>')
        for i in range(4):
            sc.add(f'<ellipse cx="{f(VX + sc.r(-60, 60))}" cy="{f(yd + 10 + i * 5)}" rx="{f(sc.r(120, 200))}" ry="{f(sc.r(2, 4))}" fill="#6a6b70" opacity="{f(.09 - i * .015)}"/>')
        with sc.hot("moria-bridge", "The narrow bridge", "One slender arch with no rail, flung across the chasm.", "flash"):
            L_, R_ = sx(-17, BRIDGE_Z), sx(17, BRIDGE_Z)
            span = R_ - L_
            top, under = [], []
            for i in range(41):
                t = i / 40
                x = L_ + span * t
                rise = 4.5 * math.sin(math.pi * t)
                top.append((x, yd - rise))
                under.append((x, yd - rise + 2.6 + 20 * (abs(t - .5) * 2) ** 3.5))
            sc.add(f'<path d="{poly(top + list(reversed(under)))}" fill="#0b0b0d"/>')
            sc.add(f'<path d="M' + " L".join(f"{f(a)},{f(b)}" for a, b in top) + '" fill="none" stroke="#c9c7c0" stroke-opacity=".75" stroke-width="1.1"/>')
            for side in (-1, 1):
                x0 = L_ if side < 0 else R_
                pts = [(x0 + side * 2, yd - 1), (x0 + side * 12, yd - 3.5), (x0 + side * 34, yd - 2.5), (x0 + side * 80, yd + 1),
                       (x0 + side * 80, ye + 2), (x0 + side * 10, ye + 2), (x0 - side * 3, yd + 18)]
                sc.add(f'<path d="{poly(pts)}" fill="#18181b"/>')
                sc.add(f'<path d="M{f(x0 + side * 2)},{f(yd - 1)} L{f(x0 + side * 12)},{f(yd - 3.5)} L{f(x0 + side * 34)},{f(yd - 2.5)}" fill="none" stroke="#9a9894" stroke-opacity=".45" stroke-width=".8"/>')
            sc.add(f'<rect x="{f(L_ - 10)}" y="{f(yd - 14)}" width="{f(span + 20)}" height="30" fill="#000" fill-opacity="0"/>')

    # ================= the hall: floor, then pillars, vaults and shafts far to near =================
    items = []
    for Z in ROWS:
        for X in COLS:
            if -200 < sx(X, Z) < W + 200 and not hidden(X, Z):
                items.append((-Z, -abs(X) / 100, "p", X, Z))
        items.append((-Z, 1, "v", None, Z))
    for X, Z, s in SHAFTS:
        items.append((-(Z + .5), 0, "s", (X, Z, s), Z))
        items.append((-(Z - .6), 0, "g", (X, Z, s), Z - .6))
    items.append((-36.8, 0, "r", None, 36.8))
    items.append((-20.0, 0, "fp", None, 20.0))
    items.append((-15.0, 0, "w", None, 15.0))  # (drawn at Z 13, kept in the near plane)
    # loose stones all over the floor, thicker near the fallen work and along the rows
    stones = []
    for _ in range(70):
        X, Z = sc.r(-45, 45), sc.r(6, 46)
        if abs(X) < 5 and Z < 30 and sc.r(0, 1) < .7:
            continue
        stones.append((X, Z, sc.r(.12, .4)))
    for _ in range(24):
        stones.append((sc.r(-14, -2), sc.r(28, 40), sc.r(.15, .5)))
    for _ in range(30):
        stones.append((sc.r(-30, 30), sc.r(6, 20), sc.r(.2, .5)))
    # big broken blocks close to us, framing the aisle
    for X, Z, s0 in [(-14, 6.5, 1.1), (-11.5, 7.6, .7), (-17, 8.4, .8), (-8.5, 5.2, .5), (12.5, 6.2, 1.2), (15.5, 7.8, .8), (9.5, 5.4, .55), (20, 9, .9)]:
        stones.append((X, Z, s0))
    for X, Z, s0 in stones:
        items.append((-Z, .5, "st", (X, Z, s0), Z))
    items.sort(key=lambda it: (it[0], it[1]))

    current = None
    cur_b = ["far"]

    def enter(b):
        nonlocal current
        if current is not None:
            current.__exit__(None, None, None)
        current = sc.layer(b, DEPTH[b])
        current.__enter__()

    enter("far")
    # the floor, flagstones running away to the lip of the deep, some cracked, some stained
    sc.add(f'<rect x="-30" y="{f(ye)}" width="{W + 60}" height="{f(H - ye + 10)}" fill="{sc.lin("floor", [(0, C["floor_far"]), (.3, "#19191d"), (1, C["floor_near"])])}"/>')
    tiles = []
    for _ in range(90):
        i, j = sc.rnd.randrange(-16, 16), sc.rnd.randrange(2, 19)
        X0, Z0 = i * 3.0, EDGE - j * 3.0
        q = [(sx(X0, Z0), sy(0, Z0)), (sx(X0 + 3, Z0), sy(0, Z0)), (sx(X0 + 3, Z0 - 3), sy(0, Z0 - 3)), (sx(X0, Z0 - 3), sy(0, Z0 - 3))]
        if sc.r(0, 1) < .7:
            tiles.append(f'<path d="{poly(q)}" fill="#000" opacity="{f(sc.r(.12, .3))}"/>')
        else:
            tiles.append(f'<path d="{poly(q)}" fill="#8a8a90" opacity="{f(sc.r(.03, .07))}"/>')
    sc.add("".join(tiles))
    g = ['<g stroke="#000" stroke-opacity=".45" stroke-width=".8" fill="none">']
    for k in range(-90, 91):
        X = k * 3.0
        g.append(f'<path d="M{f(sx(X, EDGE))},{f(ye)} L{f(sx(X, 3))},{f(sy(0, 3))}"/>')
    Z = EDGE
    while Z > 3:
        g.append(f'<path d="M-30,{f(sy(0, Z))} H{W + 30}"/>')
        Z -= 3.0
    g.append("</g>")
    sc.add("".join(g))
    cracks = ""
    for _ in range(16):
        X, Z = sc.r(-40, 40), sc.r(6, 40)
        x, y = sx(X, Z), sy(0, Z)
        cracks += f"M{f(x)},{f(y)}" + "".join(f"l{f(sc.r(-14, 14) * 20 / Z)},{f(sc.r(-3, 3) * 20 / Z)}" for _ in range(4))
    sc.add(f'<path d="{cracks}" fill="none" stroke="#000" stroke-opacity=".55" stroke-width="1"/>')
    sc.add(f'<rect x="-30" y="{f(ye - .6)}" width="{W + 60}" height="1.4" fill="#5c5d62" opacity=".5"/>')

    for _, _, kind, v, Z in items:
        b = bucket(Z)
        # layers only ever step nearer as we paint far to near
        if b != cur_b[0] and DEPTH[b] > DEPTH[cur_b[0]]:
            enter(b)
            cur_b[0] = b
        if kind == "p":
            if (v, Z) == (8, 24):
                with sc.hot("moria-runes", "Carved pillar", "Dwarf-runes cut deep in the stone; light them and they shine.", "light"):
                    pillar(sc, v, Z)
                    runes(sc, v, Z)
            else:
                pillar(sc, v, Z, broken=9.5 if (v, Z) == BROKEN else None)
        elif kind == "v":
            vault(sc, Z)
        elif kind == "s":
            X, Zs, s = v
            if (X, Zs) == (0.0, 29):
                with sc.hot("moria-shaft", "Light from above", "A pale shaft slants down from some window far overhead.", "pulse"):
                    shaft(sc, *v)
            else:
                shaft(sc, *v)
        elif kind == "g":
            X, Zs, s = v
            for _ in range(int(6 * s) + 2):
                gx, gz = X + sc.r(-3, 3), Zs + sc.r(-2.5, 2.5)
                sparkle(sc, sx(gx, gz), sy(0, gz) - sc.r(0, 1), sc.r(1.4, 2.6) * (34 / gz) ** .5, C["gold_hi"], sc.r(.5, .9))
        elif kind == "r":
            rubble(sc)
        elif kind == "fp":
            fallen_pillar(sc)
        elif kind == "w":
            with sc.hot("moria-well", "The well", "A deep, black shaft in the floor; a dropped stone falls a long while.", "splash"):
                well(sc, 12.0, 13.0)
        elif kind == "st":
            pebble(sc, *v)
    if cur_b[0] != "front":
        enter("front")
    # the near floor sinks into the page's dark
    sc.add(f'<rect x="-30" y="262" width="{W + 60}" height="148" fill="{sc.lin("near", [(0, C["bg"], 0), (1, C["bg"], .85)])}"/>')
    current.__exit__(None, None, None)
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build().save(f"{out}/moria.svg", "The halls of Moria")
