#!/usr/bin/env python3
"""Generate the Aegis wallpaper / screensaver image.

A low-key field of glossy blue iso-blocks (Kali-blocks vibe) with the glowing
Aegis shield in the centre. Rendered 2x and downsampled for clean edges.

    python3 tools/gen-wallpaper.py OUT.png [WIDTH HEIGHT]

Default output is 1920x1080. The result ships as
packages/aegis-base/usr/share/backgrounds/aegis/aegis-wallpaper.png and is used
for both the desktop background and the xscreensaver image.
"""
import math
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

TEAL = (45, 212, 191)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(h):
        c = lerp(top, bottom, y / max(1, h - 1))
        for x in range(w):
            px[x, y] = c
    return img


def radial_glow(size, cx, cy, radius, color, strength):
    """An additive radial glow layer (RGBA) centred at cx,cy."""
    w, h = size
    layer = Image.new("L", size, 0)
    px = layer.load()
    r2 = radius * radius
    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if d2 < r2:
                t = 1.0 - math.sqrt(d2) / radius
                px[x, y] = int(255 * (t ** 2) * strength)
    out = Image.new("RGBA", size, color + (0,))
    out.putalpha(layer)
    return out


def qbezier(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def shield_outline(cx, cy, w, h):
    """Return the shield polygon points (rounded top shoulders, curved taper)."""
    hw, top = w / 2.0, cy - h / 2.0
    bot = cy + h / 2.0
    shoulder = top + h * 0.40
    r = w * 0.10  # shoulder corner radius
    pts = []
    # top edge, left shoulder -> right shoulder (with small rounded corners)
    pts += qbezier((cx - hw, top + r), (cx - hw, top), (cx - hw + r, top), 8)
    pts += [(cx + hw - r, top)]
    pts += qbezier((cx + hw - r, top), (cx + hw, top), (cx + hw, top + r), 8)
    # right side down then taper to the bottom tip
    pts += [(cx + hw, shoulder)]
    pts += qbezier((cx + hw, shoulder), (cx + hw, bot - h * 0.12), (cx, bot), 26)
    # left side back up (mirror)
    pts += qbezier((cx, bot), (cx - hw, bot - h * 0.12), (cx - hw, shoulder), 26)
    pts += [(cx - hw, top + r)]
    return pts


def draw_letter_a(d, cx, cy, w, h, color):
    """A bold stencil 'A' built from polygons, centred on cx,cy."""
    hw, hh = w / 2.0, h / 2.0
    stroke = w * 0.26
    apex = (cx, cy - hh)
    lb = (cx - hw, cy + hh)
    rb = (cx + hw, cy + hh)
    # outer triangle, then punch the inner triangle and add the crossbar
    outer = [apex, (lb[0] + stroke, lb[1]), (rb[0] - stroke, rb[1])]
    # left leg
    d.polygon([apex, (apex[0] - stroke * 0.5, apex[1]),
               (lb[0] + stroke, lb[1]), lb], fill=color)
    # right leg
    d.polygon([apex, (apex[0] + stroke * 0.5, apex[1]),
               (rb[0], rb[1]), (rb[0] - stroke, rb[1])], fill=color)
    # crossbar
    by = cy + hh * 0.18
    d.polygon([(cx - w * 0.30, by), (cx + w * 0.30, by),
               (cx + w * 0.30, by + stroke * 0.7),
               (cx - w * 0.30, by + stroke * 0.7)], fill=color)
    _ = outer  # (kept for clarity; legs+bar form the A)


def iso_blocks(img, cx, cy):
    """Paint the low-key glossy blue iso-block field onto img (in place)."""
    w, h = img.size
    d = ImageDraw.Draw(img, "RGBA")
    tw = int(w * 0.055)          # tile width
    hw, hh = tw // 2, tw // 4     # iso half width / half height
    ox, oy = w // 2, int(h * 0.26)

    cubes = []
    rng = range(-18, 19)
    for gx in rng:
        for gy in rng:
            sx = ox + (gx - gy) * hw
            sy = oy + (gx + gy) * hh
            if sx < -tw or sx > w + tw or sy < -tw or sy > h + tw:
                continue
            cubes.append((gx + gy, gx, gy, sx, sy))
    cubes.sort(key=lambda c: c[0])

    maxd = math.hypot(w, h) * 0.5
    for _s, gx, gy, sx, sy in cubes:
        dist = math.hypot(sx - cx, sy - cy)
        near = max(0.0, 1.0 - dist / maxd)          # 1 at centre -> 0 at edge
        r = random.random()
        glass = r > 0.86
        tall = r < 0.14
        fh = int(tw * (0.55 if tall else random.uniform(0.18, 0.34)))

        # base blue, brighter & slightly teal toward the centre
        topc = lerp((26, 52, 96), (54, 110, 176), near * 0.8 + random.uniform(-0.05, 0.05))
        if random.random() < 0.10:  # occasional teal-tinted block ties to the shield
            topc = lerp(topc, (40, 150, 150), 0.4)
        leftc = lerp(topc, (6, 14, 30), 0.45)
        rightc = lerp(topc, (4, 9, 20), 0.62)
        # low-key: fade blocks far from the centre into the background
        fade = 0.25 + 0.75 * near
        topc = lerp((11, 18, 34), topc, fade)
        leftc = lerp((9, 14, 28), leftc, fade)
        rightc = lerp((7, 11, 22), rightc, fade)

        A = (sx, sy - hh - fh)
        B = (sx + hw, sy - fh)
        C = (sx, sy + hh - fh)
        D = (sx - hw, sy - fh)
        Cl = (sx, sy + hh)
        Dl = (sx - hw, sy)
        Bl = (sx + hw, sy)

        alpha = 150 if glass else 255
        d.polygon([D, C, Cl, Dl], fill=leftc + (alpha,))
        d.polygon([C, B, Bl, Cl], fill=rightc + (alpha,))
        d.polygon([A, B, C, D], fill=topc + (alpha,))

        # glossy top edge highlight
        hi = lerp(topc, (210, 230, 255), 0.5)
        d.line([A, B], fill=hi + (200,), width=max(1, tw // 60))
        d.line([A, D], fill=hi + (120,), width=max(1, tw // 60))
        if glass:  # a diagonal reflection streak on glass blocks
            d.line([lerp(A, D, 0.3), lerp(C, Cl, 0.6)],
                   fill=(220, 235, 255, 90), width=max(1, tw // 30))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "aegis-wallpaper.png"
    W = int(sys.argv[2]) if len(sys.argv) > 3 else 1920
    H = int(sys.argv[3]) if len(sys.argv) > 3 else 1080
    ss = 2
    w, h = W * ss, H * ss
    random.seed(11)

    img = vgrad((w, h), (9, 13, 26), (13, 22, 42))
    cx, cy = w // 2, int(h * 0.47)

    iso_blocks(img, cx, cy)

    img = img.convert("RGBA")
    # soft glow pooling light behind the shield
    img = Image.alpha_composite(img, radial_glow((w, h), cx, cy, int(w * 0.28),
                                                  (30, 120, 150), 0.55))

    # shield on its own layer so we can bloom it
    sl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sl)
    sw, sh = int(w * 0.11), int(h * 0.26)
    pts = shield_outline(cx, cy, sw, sh)
    sd.polygon(pts, fill=(16, 26, 44, 235), outline=TEAL + (255,))
    # thick teal rim
    for width in (max(2, w // 320), max(1, w // 520)):
        sd.line(pts + [pts[0]], fill=TEAL + (255,), width=width, joint="curve")
    draw_letter_a(sd, cx, cy - sh * 0.02, sw * 0.42, sh * 0.44, TEAL + (255,))

    # bloom = blurred copy of the shield layer, composited under the crisp one
    bloom = sl.filter(ImageFilter.GaussianBlur(w // 180))
    img = Image.alpha_composite(img, bloom)
    img = Image.alpha_composite(img, bloom)
    img = Image.alpha_composite(img, sl)

    # gentle vignette to keep it low-key
    vig = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-w * 0.25, -h * 0.25, w * 1.25, h * 1.25], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(w // 12))
    dark = Image.new("RGBA", (w, h), (4, 7, 16, 255))
    dark.putalpha(Image.eval(vig, lambda v: 255 - v))
    img = Image.alpha_composite(img, dark)

    img = img.convert("RGB").resize((W, H), Image.LANCZOS)
    img.save(out, "PNG", optimize=True)
    print(f"wrote {out}  ({W}x{H})")


if __name__ == "__main__":
    main()
