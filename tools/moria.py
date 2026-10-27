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
SHAFTS = [(0.0, 29, 1.0), (13.0, 49, .75), (-13.5, 39, .6), (24.0, 57, .5), (57.0, 31, .6), (-30.0, 19, .8), (47.0, 20, .65)]
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
    sc.add(f'<path d="{poly([(tx - wt / 2, top), (tx + wt / 2, top), (fx + wf / 2, fy), (fx - wf / 2, fy)])}" fill="url(#{gid})"/>')
    sc.add(f'<path d="{poly([(tx - wt * .16, top), (tx + wt * .2, top), (fx + wf * .14, fy), (fx - wf * .1, fy)])}" fill="{C["shaft"]}" opacity="{f(.07 * s)}"/>')
    # the pool where it lands
    rx = 5.0 * FL / Z
    ry = 5.0 * FL * HC / (Z * Z) * 1.2
    sc.add(f'<ellipse cx="{f(fx)}" cy="{f(fy)}" rx="{f(rx)}" ry="{f(ry)}" fill="url(#pool)" opacity="{f(s)}"/>')
    # dust turning in the light
    g = [f'<g fill="{C["dust"]}">']
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


def build(seed=11):
    sc = Scene(seed)
    sc.defs.append(f'<linearGradient id="vault" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="0" y2="{H}">'
                   f'<stop offset="0" stop-color="{C["void"]}" stop-opacity=".96"/><stop offset=".14" stop-color="{C["void"]}" stop-opacity=".72"/>'
                   f'<stop offset=".34" stop-color="{C["void"]}" stop-opacity=".25"/><stop offset=".48" stop-color="{C["void"]}" stop-opacity="0"/>'
                   f'<stop offset=".62" stop-color="{C["void"]}" stop-opacity="0"/><stop offset="1" stop-color="{C["void"]}" stop-opacity=".7"/></linearGradient>')
    sc.defs.append(f'<radialGradient id="pool"><stop offset="0" stop-color="{C["shaft"]}" stop-opacity=".42"/>'
                   f'<stop offset=".5" stop-color="{C["shaft"]}" stop-opacity=".1"/><stop offset="1" stop-color="{C["shaft"]}" stop-opacity="0"/></radialGradient>')

    carving_defs(sc)

    # the dark of the hall, greyer far down the aisle where the deep opens
    sc.sky(C["void"])
    sc.add(f'<ellipse cx="{VX}" cy="{VY - 10}" rx="420" ry="190" fill="{sc.rad("glow", [(0, "#4a4b52", 1), (.45, C["haze"], .5), (1, C["haze"], 0)])}"/>')

    # beyond the chasm: the far cliff with its ledge and a doorway at the bridge's end
    fz = 96
    cliff = []
    for i in range(61):
        X = -110 + i * 220 / 60
        Y = BRIDGE_Y - .4 + .7 * math.sin(i * 1.7) + .5 * math.sin(i * .6 + 1)
        cliff.append((sx(X, fz), sy(Y, fz)))
    ced = " ".join(f"L{f(a)},{f(b)}" for a, b in reversed(cliff))
    sc.add(f'<path d="M{f(cliff[0][0])},-10 L{f(cliff[-1][0])},-10 L{f(cliff[-1][0])},{f(cliff[-1][1])} {ced}Z" '
           f'fill="{sc.lin("cliffg", [(0, "#141416"), (.6, "#33343a"), (1, "#45464c")])}"/>')
    for Y in (14, 19, 25):  # cut courses on the far wall
        y = sy(Y, fz)
        sc.add(f'<path d="M{f(sx(-110, fz))},{f(y)} H{f(sx(110, fz))}" stroke="#000" stroke-opacity=".3" stroke-width=".8"/>')
    dx0, dx1 = sx(-2.2, fz), sx(2.2, fz)
    dyt, dyb = sy(BRIDGE_Y + 7, fz), sy(BRIDGE_Y, fz)
    ch = (dx1 - dx0) * .3
    sc.add(f'<path d="{poly([(dx0, dyb), (dx0, dyt + ch), (dx0 + ch, dyt), (dx1 - ch, dyt), (dx1, dyt + ch), (dx1, dyb)])}" fill="#0c0c0e"/>')
    # the deep
    ye = sy(0, EDGE)
    sc.add(f'<path d="M{f(cliff[0][0])},{f(cliff[0][1])} ' + " ".join(f"L{f(a)},{f(b)}" for a, b in cliff) +
           f' L{f(cliff[-1][0])},{f(ye + 4)} L{f(cliff[0][0])},{f(ye + 4)}Z" fill="{sc.lin("abyss", [(0, "#2a2b30"), (.35, "#121214"), (1, C["void"])])}"/>')
    # a shaft falling into the deep behind the bridge, so the bridge stands dark against it
    bxs = sx(-2, 84)
    sc.add(f'<path d="{poly([(bxs + 52, -10), (bxs + 84, -10), (bxs + 12, ye), (bxs - 8, ye)])}" fill="{C["shaft"]}" opacity=".06"/>')
    sc.add(f'<ellipse cx="{f(bxs + 6)}" cy="{f(sy(BRIDGE_Y, BRIDGE_Z) + 6)}" rx="80" ry="16" fill="url(#pool)"/>')
    for i in range(4):  # mist in the deep
        sc.add(f'<ellipse cx="{f(VX + sc.r(-60, 60))}" cy="{f(sy(BRIDGE_Y, BRIDGE_Z) + 8 + i * 5)}" rx="{f(sc.r(120, 200))}" ry="{f(sc.r(2, 4))}" fill="#6a6b70" opacity="{f(.09 - i * .015)}"/>')
    # the bridge: one slender arch with no rail, springing from rock on either side
    L, R = sx(-17, BRIDGE_Z), sx(17, BRIDGE_Z)
    yd = sy(BRIDGE_Y, BRIDGE_Z)
    span = R - L
    top, under = [], []
    for i in range(41):
        t = i / 40
        x = L + span * t
        rise = 3.5 * math.sin(math.pi * t)
        top.append((x, yd - rise))
        under.append((x, yd - rise + 1.4 + 18 * (abs(t - .5) * 2) ** 3.5))
    sc.add(f'<path d="{poly(top + list(reversed(under)))}" fill="#121215"/>')
    sc.add(f'<path d="M' + " L".join(f"{f(a)},{f(b)}" for a, b in top) + '" fill="none" stroke="#9a9894" stroke-opacity=".5" stroke-width=".7"/>')
    for side in (-1, 1):  # rock the bridge springs from
        x0 = L if side < 0 else R
        pts = [(x0 + side * 2, yd - 1), (x0 + side * 12, yd - 3.5), (x0 + side * 34, yd - 2.5), (x0 + side * 80, yd + 1),
               (x0 + side * 80, ye + 2), (x0 + side * 10, ye + 2), (x0 - side * 3, yd + 18)]
        sc.add(f'<path d="{poly(pts)}" fill="#18181b"/>')

    # the hall floor, flagstones running away to the lip of the deep
    sc.add(f'<rect x="-10" y="{f(ye)}" width="{W + 20}" height="{f(H - ye + 10)}" fill="{sc.lin("floor", [(0, C["floor_far"]), (.3, "#19191d"), (1, C["floor_near"])])}"/>')
    g = ['<g stroke="#000" stroke-opacity=".45" stroke-width=".8" fill="none">']
    for k in range(-90, 91):
        X = k * 3.0
        g.append(f'<path d="M{f(sx(X, EDGE))},{f(ye)} L{f(sx(X, 3))},{f(sy(0, 3))}"/>')
    Z = EDGE
    while Z > 3:
        g.append(f'<path d="M-10,{f(sy(0, Z))} H{W + 10}"/>')
        Z -= 3.0
    g.append("</g>")
    sc.add("".join(g))
    sc.add(f'<rect x="-10" y="{f(ye - .6)}" width="{W + 20}" height="1.4" fill="#5c5d62" opacity=".5"/>')

    # pillars, vaults and shafts, far to near (within a row: pillars, then the vault they carry)
    items = []
    for Z in ROWS:
        for X in COLS:
            if -200 < sx(X, Z) < W + 200 and not hidden(X, Z):
                items.append((-Z, -abs(X) / 100, "p", X, Z))
        items.append((-Z, 1, "v", None, Z))
    for X, Z, s in SHAFTS:
        items.append((-(Z + .5), 0, "s", (X, Z, s), Z))
    items.append((-36.8, 0, "r", None, 36.8))
    items.sort(key=lambda it: (it[0], it[1]))
    for _, _, kind, v, Z in items:
        if kind == "p":
            pillar(sc, v, Z, broken=9.5 if (v, Z) == BROKEN else None)
        elif kind == "v":
            vault(sc, Z)
        elif kind == "s":
            shaft(sc, *v)
        else:
            rubble(sc)

    # glints of gold where the light touches the floor
    for X, Z, s in SHAFTS:
        for _ in range(int(6 * s) + 2):
            gx, gz = X + sc.r(-3, 3), Z + sc.r(-2.5, 2.5)
            sparkle(sc, sx(gx, gz), sy(0, gz) - sc.r(0, 1), sc.r(1.4, 2.6) * (34 / gz) ** .5, C["gold_hi"], sc.r(.5, .9))

    # the near floor sinks into the page's dark
    sc.add(f'<rect y="262" width="{W}" height="138" fill="{sc.lin("near", [(0, C["bg"], 0), (1, C["bg"], .85)])}"/>')
    return sc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "../scenes"
    build().save(f"{out}/moria.svg", "The halls of Moria")
