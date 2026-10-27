"""Shared drawing kit for Daybook's region scenes.

Every scene is a 1600x400 panorama drawn as flat, layered vector shapes:
sky, far hills fading into haze, a detailed middle distance, and a foreground
that the page fades out. Scenes are generated (seeded, so stable) and written
to scenes/<region>.svg.
"""
import math
import random
from contextlib import contextmanager
from html import escape

W, H = 1600, 400
# extra lights a viewer can switch on stay dark wherever the file is shown as a plain image (the Daybook banner);
# the scene viewer's own rules are more specific, so it can still light them
LIT_STYLE = "<style>.hot .on-lit{opacity:0}</style>"


def f(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


class Scene:
    def __init__(self, seed):
        self.rnd = random.Random(seed)
        self.defs = []
        self.parts = []

    # ---------- output ----------
    def add(self, s):
        self.parts.append(s)

    def svg(self, title):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMax slice">'
                f'<title>{title}</title><defs>{"".join(self.defs)}{LIT_STYLE}</defs>{"".join(self.parts)}</svg>')

    def save(self, path, title):
        with open(path, "w") as fh:
            fh.write(self.svg(title))

    # ---------- structure the scene viewer (scenes.html) reads ----------
    # Daybook shows the files as plain images, where these groups change nothing.
    @contextmanager
    def layer(self, name, depth):
        """A depth plane: 0 = sky, 1 = nearest foreground. The viewer shifts each plane by depth for parallax."""
        self.add(f'<g class="layer" data-layer="{name}" data-depth="{depth}">')
        yield
        self.add("</g>")

    @contextmanager
    def hot(self, hid, name, note, fx="pulse"):
        """A feature you can click: name is its label, note one short line, fx what happens
        (pulse, light, swing, smoke, sparks, leaves, splash, flash, erupt)."""
        self.add(f'<g class="hot" id="{hid}" data-name="{escape(name)}" data-note="{escape(note)}" data-fx="{fx}">')
        yield
        self.add("</g>")

    @contextmanager
    def fx(self, kind, period=0):
        """Ambient motion the viewer can switch on (smoke, cloud, water, flicker, rain, embers, sway, glow, beam, birds).
        rain needs period: the streaks repeat every `period` px vertically so the loop is seamless."""
        st = f' style="--p:{period}px"' if period else ""
        self.add(f'<g class="fx fx-{kind}"{st}>')
        yield
        self.add("</g>")

    # ---------- helpers ----------
    def r(self, a, b):
        return self.rnd.uniform(a, b)

    def lin(self, gid, stops, x2=0, y2=1):
        st = ""
        for s in stops:
            o, c = s[0], s[1]
            op = f' stop-opacity="{s[2]}"' if len(s) > 2 else ""
            st += f'<stop offset="{o}" stop-color="{c}"{op}/>'
        self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">{st}</linearGradient>')
        return f"url(#{gid})"

    def rad(self, gid, stops, cx=.5, cy=.5, rr=.5):
        st = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{op}"/>' for o, c, op in stops)
        self.defs.append(f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{rr}">{st}</radialGradient>')
        return f"url(#{gid})"

    def sky(self, fill):
        self.add(f'<rect width="{W}" height="{H}" fill="{fill}"/>')

    def ridge(self, y, amp, waves, fill, seed=0.0, rough=0.0, step=8, x0=-20, x1=W + 20, bottom=H + 10, extra="", taper=0):
        """A hill line: sum of sines plus a little noise, closed to the bottom.
        taper (px) slopes the ends down by ~90px so a partial ridge settles into the ground instead of ending in a wall."""
        pts = []
        x = x0
        while x <= x1:
            t = x / W
            yy = y + sum(amp * a * math.sin(t * math.pi * 2 * k + seed * (i + 1)) for i, (k, a) in enumerate(waves))
            if taper:
                e = min(x - x0, x1 - x) / taper
                if e < 1:
                    yy += 90 * (1 - e) ** 2
            if rough:
                yy += self.r(-rough, rough)
            pts.append((x, yy))
            x += step
        d = "M" + " L".join(f"{f(a)},{f(b)}" for a, b in pts) + f" L{f(x1)},{bottom} L{f(x0)},{bottom}Z"
        self.add(f'<path d="{d}" fill="{fill}"{extra}/>')
        return pts

    @staticmethod
    def y_at(pts, x):
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if ax <= x <= bx:
                return ay + (by - ay) * (x - ax) / ((bx - ax) or 1)
        return pts[-1][1]

    def cloud(self, cx, cy, s, light, shade, op=1.0):
        g = [f'<g opacity="{op}">']
        puffs = [(-1.1, .25, .55), (-.55, -.05, .75), (0, -.25, .9), (.6, 0, .7), (1.1, .25, .5)]
        for dx, dy, rr in puffs:
            g.append(f'<ellipse cx="{f(cx + dx * s)}" cy="{f(cy + dy * s + s * .12)}" rx="{f(rr * s)}" ry="{f(rr * s * .62)}" fill="{shade}"/>')
        for dx, dy, rr in puffs:
            g.append(f'<ellipse cx="{f(cx + dx * s - s * .05)}" cy="{f(cy + dy * s)}" rx="{f(rr * s * .92)}" ry="{f(rr * s * .55)}" fill="{light}"/>')
        g.append(f'<rect x="{f(cx - 1.5 * s)}" y="{f(cy + s * .28)}" width="{f(3 * s)}" height="{f(s * .3)}" fill="{shade}" opacity="0"/>')
        g.append("</g>")
        self.add("".join(g))

    def tree(self, x, y, s, leaf, shade, light, trunk="#5a3d22", kind="round"):
        """A broadleaf tree standing at (x, y) with canopy size s."""
        g = [f'<path d="M{f(x - s * .07)},{f(y)} L{f(x - s * .04)},{f(y - s * .7)} L{f(x + s * .04)},{f(y - s * .7)} L{f(x + s * .08)},{f(y)}Z" fill="{trunk}"/>']
        n = 7 if kind == "round" else 9
        blobs = []
        for i in range(n):
            a = i / n * math.pi * 2
            rr = s * self.r(.32, .45)
            bx = x + math.cos(a) * s * .38
            by = y - s * 1.05 + math.sin(a) * s * .3
            blobs.append((bx, by, rr))
        blobs.append((x, y - s * 1.1, s * .5))
        for bx, by, rr in blobs:
            g.append(f'<circle cx="{f(bx + rr * .12)}" cy="{f(by + rr * .14)}" r="{f(rr)}" fill="{shade}"/>')
        for bx, by, rr in blobs:
            g.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(rr * .9)}" fill="{leaf}"/>')
        for bx, by, rr in blobs[:4] + blobs[-1:]:
            g.append(f'<circle cx="{f(bx - rr * .3)}" cy="{f(by - rr * .35)}" r="{f(rr * .38)}" fill="{light}" opacity=".7"/>')
        self.add("".join(g))

    def conifer(self, x, y, s, fill, shade):
        h = s * 2.4
        d = f"M{f(x)},{f(y - h)} L{f(x + s * .55)},{f(y)} L{f(x - s * .55)},{f(y)}Z"
        self.add(f'<path d="{d}" fill="{fill}"/><path d="M{f(x)},{f(y - h)} L{f(x + s * .55)},{f(y)} L{f(x)},{f(y)}Z" fill="{shade}" opacity=".55"/>')

    def hedge(self, pts, s, fill, shade):
        g = []
        for x, y in pts:
            rr = s * self.r(.7, 1.15)
            g.append(f'<circle cx="{f(x + rr * .2)}" cy="{f(y + rr * .2)}" r="{f(rr)}" fill="{shade}"/>')
        for x, y in pts:
            rr = s * self.r(.6, 1.0)
            g.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" fill="{fill}"/>')
        self.add("".join(g))

    def tufts(self, y0, y1, n, cols, hmin=6, hmax=16):
        g = []
        for _ in range(n):
            x = self.r(-10, W + 10)
            y = self.r(y0, y1)
            c = self.rnd.choice(cols)
            h = self.r(hmin, hmax)
            lean = self.r(-3, 3)
            g.append(f'<path d="M{f(x - 2)},{f(y)} Q{f(x + lean)},{f(y - h)} {f(x + lean * 1.4)},{f(y - h - 1)} Q{f(x + 1)},{f(y - h * .5)} {f(x + 2)},{f(y)}Z" fill="{c}"/>')
        self.add("".join(g))

    def flowers(self, y0, y1, n, cols, rmin=1.2, rmax=2.4, x0=0, x1=W):
        g = []
        for _ in range(n):
            g.append(f'<circle cx="{f(self.r(x0, x1))}" cy="{f(self.r(y0, y1))}" r="{f(self.r(rmin, rmax))}" fill="{self.rnd.choice(cols)}"/>')
        self.add("".join(g))

    def smoke(self, x, y, n, col, op=.35, drift=1.0):
        g = [f'<g fill="{col}" opacity="{op}">']
        for i in range(n):
            rr = 3 + i * 1.6
            g.append(f'<circle cx="{f(x + drift * (i * 4 + math.sin(i) * 5))}" cy="{f(y - i * 9)}" r="{f(rr)}" opacity="{f(1 - i / (n + 1))}"/>')
        g.append("</g>")
        self.add("".join(g))

    def birds(self, pts, col, s=1.0):
        g = [f'<g fill="none" stroke="{col}" stroke-width="1.4" stroke-linecap="round">']
        for x, y in pts:
            g.append(f'<path d="M{f(x - 6 * s)},{f(y)} q{f(3 * s)},{f(-4 * s)} {f(6 * s)},0 q{f(3 * s)},{f(-4 * s)} {f(6 * s)},0"/>')
        g.append("</g>")
        self.add("".join(g))
