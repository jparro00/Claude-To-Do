#!/usr/bin/env python3
"""Generate labeled menswear diagrams + fabric/color swatches for the wardrobe guide.
No network needed; everything is drawn procedurally. Output: PNGs in this folder."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, Rectangle, FancyArrowPatch, Ellipse
from matplotlib.path import Path
import matplotlib.patches as mpatches
from PIL import Image

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "DejaVu Sans"

INK = "#1b1b1b"
SUB = "#555555"

# ---------------------------------------------------------------- fabric weaves
def woven_base(h, w, base_rgb, contrast=10, seed=0):
    """A subtle warp/weft micro-texture so swatches read like cloth, not flat fill."""
    rng = np.random.default_rng(seed)
    base = np.array(base_rgb, dtype=float)
    img = np.tile(base, (h, w, 1))
    # vertical warp threads
    warp = (np.indices((h, w))[1] % 2) * contrast
    weft = (np.indices((h, w))[0] % 2) * (contrast * 0.6)
    noise = rng.normal(0, 4, (h, w))
    delta = (warp + weft + noise)[:, :, None]
    img = np.clip(img + delta - contrast, 0, 255)
    return img

def save_rgb(arr, name):
    Image.fromarray(arr.astype(np.uint8)).save(os.path.join(OUT, name))

def swatch(name, base_rgb, drawfn=None, contrast=10, seed=1):
    h, w = 360, 540
    img = woven_base(h, w, base_rgb, contrast=contrast, seed=seed)
    if drawfn:
        drawfn(img)
    save_rgb(img, name)

def _vlines(img, color, spacing, width=2, softness=0.0, offset=0):
    h, w, _ = img.shape
    col = np.array(color, float)
    for x in range(offset, w, spacing):
        for dx in range(width):
            xx = x + dx
            if xx < w:
                if softness:
                    img[:, xx] = img[:, xx] * (1 - softness) + col * softness
                else:
                    img[:, xx] = col

def _hlines(img, color, spacing, width=2, offset=0):
    h, w, _ = img.shape
    col = np.array(color, float)
    for y in range(offset, h, spacing):
        for dy in range(width):
            yy = y + dy
            if yy < h:
                img[yy, :] = col

def _dots(img, color, spacing, r=2):
    h, w, _ = img.shape
    col = np.array(color, float)
    for y in range(spacing // 2, h, spacing):
        for x in range(spacing // 2, w, spacing):
            img[max(0, y - r):y + r, max(0, x - r):x + r] = col

def make_fabric_swatches():
    navy = (38, 50, 78)
    charcoal = (60, 62, 68)
    midgrey = (130, 134, 140)
    # solids
    swatch("sw_navy.png", navy, contrast=8, seed=2)
    swatch("sw_charcoal.png", charcoal, contrast=8, seed=3)
    swatch("sw_midgrey.png", midgrey, contrast=10, seed=4)
    swatch("sw_black.png", (28, 28, 30), contrast=6, seed=5)
    # birdseye (tiny light dots on navy)
    swatch("sw_birdseye.png", navy, drawfn=lambda im: _dots(im, (170, 175, 190), 10, r=1), seed=6)
    # nailhead (slightly bigger dots, mid grey field)
    swatch("sw_nailhead.png", (74, 78, 90), drawfn=lambda im: _dots(im, (185, 190, 200), 14, r=2), seed=7)
    # sharkskin / pick-and-pick (fine diagonal)
    def sharkskin(im):
        h, w, _ = im.shape
        col = np.array((175, 178, 188), float)
        for d in range(-h, w, 6):
            for y in range(h):
                x = d + y
                if 0 <= x < w:
                    im[y, x] = col
    swatch("sw_sharkskin.png", (92, 96, 108), drawfn=sharkskin, seed=8)
    # pinstripe (thin crisp lines, navy)
    swatch("sw_pinstripe.png", navy, drawfn=lambda im: _vlines(im, (200, 205, 215), 26, width=2), seed=9)
    # chalk stripe (softer, wider, charcoal)
    swatch("sw_chalkstripe.png", charcoal, drawfn=lambda im: _vlines(im, (205, 207, 212), 46, width=5, softness=0.85), seed=10)
    # glen check / Prince of Wales (2-tone district check + rust overcheck)
    def glen(im):
        h, w, _ = im.shape
        block = 16
        light = np.array((200, 200, 204), float)
        mid = np.array((120, 124, 134), float)
        for by in range(0, h, block):
            for bx in range(0, w, block):
                checker = ((bx // block) + (by // block)) % 2 == 0
                im[by:by + block, bx:bx + block] = light if checker else mid
        # faint Prince-of-Wales rust overcheck
        _vlines(im, (150, 92, 70), 96, width=2, softness=0.55)
        _hlines(im, (150, 92, 70), 96, width=2)
    swatch("sw_glencheck.png", (188, 188, 190), drawfn=glen, contrast=6, seed=11)
    # windowpane (widely spaced thin grid)
    def windowpane(im):
        _vlines(im, (205, 150, 150), 90, width=1, softness=0.7)
        _hlines(im, (205, 150, 150), 90, width=1)
    swatch("sw_windowpane.png", charcoal, drawfn=windowpane, seed=12)
    # hopsack (basketweave - 2x2 blocks)
    def hopsack(im):
        h, w, _ = im.shape
        b = 8
        light = np.array((58, 72, 104), float)
        dark = np.array((30, 40, 64), float)
        for y in range(0, h, b):
            for x in range(0, w, b):
                blk = light if ((x // b + y // b) % 2 == 0) else dark
                im[y:y + b, x:x + b] = blk
    swatch("sw_hopsack.png", navy, drawfn=hopsack, contrast=4, seed=13)

# ---------------------------------------------------------------- leather shades
def make_leather_strip():
    fig, ax = plt.subplots(figsize=(9, 2.4), dpi=150)
    shades = [
        ("Tan",        "#b9824f", "most casual"),
        ("Mid-brown /\nChestnut", "#7d4a2a", "daily default"),
        ("Dark oak /\nEspresso",  "#3f2417", "most formal brown"),
        ("Oxblood /\nBurgundy",   "#5a2230", "knowing choice"),
        ("Black",      "#15110f", "most formal"),
    ]
    n = len(shades)
    for i, (name, hexc, note) in enumerate(shades):
        ax.add_patch(Rectangle((i, 0), 0.94, 1, color=hexc))
        ax.text(i + 0.47, -0.13, name, ha="center", va="top", fontsize=10, color=INK)
        ax.text(i + 0.47, -0.46, note, ha="center", va="top", fontsize=8, color=SUB, style="italic")
    ax.annotate("", xy=(n - 0.1, 1.28), xytext=(0.1, 1.28),
                arrowprops=dict(arrowstyle="->", color=SUB))
    ax.text(0.1, 1.36, "more casual", fontsize=8, color=SUB)
    ax.text(n - 0.1, 1.36, "more formal", fontsize=8, color=SUB, ha="right")
    ax.set_xlim(-0.1, n); ax.set_ylim(-0.7, 1.5); ax.axis("off")
    fig.savefig(os.path.join(OUT, "leather_shades.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- oxford vs derby
def make_oxford_derby():
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), dpi=150)
    for ax, kind in zip(axes, ["oxford", "derby"]):
        ax.set_xlim(0, 10); ax.set_ylim(-1.4, 8); ax.axis("off")
        # sole
        ax.add_patch(FancyBboxPatch((0.6, 0.6), 8.8, 1.0, boxstyle="round,pad=0.1,rounding_size=0.4",
                                    fc="#6b4a32", ec=INK, lw=1.2))
        # upper body
        body = Polygon([(1.2, 1.6), (8.8, 1.6), (8.6, 3.2), (6.6, 4.6),
                        (3.0, 4.8), (1.4, 3.6)], closed=True, fc="#8a5a36", ec=INK, lw=1.4)
        ax.add_patch(body)
        # toe cap line
        ax.plot([6.9, 7.2], [1.7, 4.0], color=INK, lw=1)
        if kind == "oxford":
            # closed lacing: quarters tucked UNDER vamp, V meets at bottom
            q1 = Polygon([(3.0, 4.7), (4.6, 4.4), (4.4, 2.6), (3.2, 2.6)], closed=True,
                         fc="#7a4d2e", ec=INK, lw=1.2)
            q2 = Polygon([(6.0, 4.55), (4.7, 4.4), (4.9, 2.6), (6.1, 2.7)], closed=True,
                         fc="#7a4d2e", ec=INK, lw=1.2)
            ax.add_patch(q1); ax.add_patch(q2)
            for y in [4.2, 3.6, 3.0]:
                ax.plot([4.45, 4.85], [y, y], color="#2b2b2b", lw=2)
            ax.text(5.0, 6.2, "OXFORD", ha="center", fontsize=14, weight="bold", color=INK)
            ax.text(5.0, 5.5, "CLOSED lacing", ha="center", fontsize=10, color="#9c2b2b", weight="bold")
            ax.text(5.0, -0.8, "Lace flaps stitched UNDER the front —\nsleek, V comes together. Most formal.",
                    ha="center", fontsize=8.5, color=SUB)
        else:
            # open lacing: quarters sit ON TOP of vamp, flaps open outward
            q1 = Polygon([(2.7, 4.9), (4.7, 4.5), (4.5, 2.4), (2.9, 2.6)], closed=True,
                         fc="#7a4d2e", ec=INK, lw=1.2)
            q2 = Polygon([(6.4, 4.75), (4.8, 4.5), (5.0, 2.5), (6.4, 2.7)], closed=True,
                         fc="#7a4d2e", ec=INK, lw=1.2)
            ax.add_patch(q1); ax.add_patch(q2)
            for y in [4.3, 3.7, 3.1]:
                ax.plot([4.5, 4.95], [y + 0.05, y - 0.05], color="#2b2b2b", lw=2)
            ax.text(5.0, 6.2, "DERBY", ha="center", fontsize=14, weight="bold", color=INK)
            ax.text(5.0, 5.5, "OPEN lacing", ha="center", fontsize=10, color="#2b6b2b", weight="bold")
            ax.text(5.0, -0.8, "Lace flaps sewn ON TOP, open at the bottom —\nrelaxed & adjustable. Business-casual.",
                    ha="center", fontsize=8.5, color=SUB)
    fig.savefig(os.path.join(OUT, "oxford_vs_derby.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- toe shapes
def make_toe_shapes():
    fig, axes = plt.subplots(1, 4, figsize=(11, 2.8), dpi=150)
    shapes = [
        ("Round", "ok", [(0.1,0.2),(2.4,0.2),(2.9,0.55),(2.4,0.95),(0.1,0.95)], 0.45),
        ("Almond", "ok", [(0.1,0.2),(2.3,0.2),(3.0,0.5),(2.85,0.62),(2.3,0.95),(0.1,0.95)], 0.05),
        ("Chiseled", "care", [(0.1,0.2),(2.6,0.25),(3.2,0.42),(3.2,0.6),(2.6,0.92),(0.1,0.95)], 0.0),
        ("Square", "avoid", [(0.1,0.2),(3.0,0.2),(3.0,0.95),(0.1,0.95)], 0.0),
    ]
    verdict = {"ok": ("#2b6b2b", "safe"), "care": ("#9c7a1f", "moderate only"), "avoid": ("#9c2b2b", "AVOID")}
    for ax, (name, v, pts, _r) in zip(axes, shapes):
        ax.set_xlim(-0.2, 3.6); ax.set_ylim(-0.6, 1.4); ax.axis("off")
        ax.add_patch(Polygon(pts, closed=True, fc="#8a5a36", ec=INK, lw=1.6))
        ax.text(1.6, 1.2, name, ha="center", fontsize=12, weight="bold", color=INK)
        c, label = verdict[v]
        ax.text(1.6, -0.4, label, ha="center", fontsize=10, weight="bold", color=c)
    fig.suptitle("Toe shapes  —  what reads refined vs. cheap", fontsize=12, color=INK, y=1.02)
    fig.savefig(os.path.join(OUT, "toe_shapes.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- shoe styles
def shoe_outline(ax, color="#8a5a36"):
    ax.add_patch(FancyBboxPatch((0.5, 0.5), 8.6, 0.85, boxstyle="round,pad=0.08,rounding_size=0.35",
                                fc="#5e4029", ec=INK, lw=1.1))
    body = Polygon([(1.1, 1.35), (8.8, 1.35), (8.5, 3.0), (6.3, 4.4),
                    (3.0, 4.6), (1.3, 3.4)], closed=True, fc=color, ec=INK, lw=1.4)
    ax.add_patch(body)

def make_shoe_styles():
    fig, axes = plt.subplots(2, 3, figsize=(11, 7), dpi=150)
    titles = ["Cap-toe Oxford", "Wholecut", "Single Monk",
              "Double Monk", "Penny Loafer", "Tassel Loafer"]
    notes = ["The formal standard.\nBlack = boardroom/black-tie.",
             "One piece of leather,\nno seams. Very sleek/formal.",
             "One buckle instead of laces.\nBetween oxford & derby.",
             "Two buckles. Sharper,\nslightly more fashion-forward.",
             "Slip-on, strap with a slot.\nWarm-climate workhorse.",
             "Slip-on with tassels.\nClassic lawyer/finance shoe."]
    for ax, t, note in zip(axes.ravel(), titles, notes):
        ax.set_xlim(0, 10); ax.set_ylim(-1.2, 6); ax.axis("off")
        shoe_outline(ax)
        if t == "Cap-toe Oxford":
            ax.plot([6.7, 7.0], [1.45, 3.7], color=INK, lw=1.4)
            for y in [4.0, 3.4, 2.8]:
                ax.plot([4.4, 4.9], [y, y], color="#2b2b2b", lw=2)
        elif t == "Wholecut":
            pass
        elif t == "Single Monk":
            ax.add_patch(Rectangle((3.6, 2.4), 2.8, 0.5, fc="#6b4524", ec=INK, lw=1))
            ax.add_patch(Rectangle((6.1, 2.3), 0.45, 0.7, fc="#c9a24a", ec=INK, lw=1))
        elif t == "Double Monk":
            ax.add_patch(Rectangle((3.4, 2.9), 3.0, 0.45, fc="#6b4524", ec=INK, lw=1))
            ax.add_patch(Rectangle((3.4, 2.1), 3.0, 0.45, fc="#6b4524", ec=INK, lw=1))
            ax.add_patch(Rectangle((6.1, 2.85), 0.4, 0.55, fc="#c9a24a", ec=INK, lw=1))
            ax.add_patch(Rectangle((6.1, 2.05), 0.4, 0.55, fc="#c9a24a", ec=INK, lw=1))
        elif t == "Penny Loafer":
            ax.add_patch(Polygon([(3.4, 3.7), (6.4, 3.7), (6.2, 2.9), (3.6, 2.9)],
                                 closed=True, fc="#6b4524", ec=INK, lw=1))
            ax.add_patch(Rectangle((4.5, 3.15), 0.9, 0.18, fc=color if False else "#3a2613", ec=INK, lw=0.8))
        elif t == "Tassel Loafer":
            ax.add_patch(Polygon([(3.4, 3.7), (6.4, 3.7), (6.2, 2.9), (3.6, 2.9)],
                                 closed=True, fc="#6b4524", ec=INK, lw=1))
            for tx in [4.3, 4.7, 5.6, 6.0]:
                ax.plot([tx, tx], [2.9, 2.2], color="#3a2613", lw=2)
                ax.add_patch(Circle((tx, 2.15), 0.12, fc="#3a2613", ec=INK, lw=0.5))
        ax.text(5, 5.4, t, ha="center", fontsize=12.5, weight="bold", color=INK)
        ax.text(5, -1.0, note, ha="center", fontsize=8.5, color=SUB)
    fig.suptitle("Dress shoe styles, most formal → most casual", fontsize=13, color=INK, y=1.0)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "shoe_styles.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- collars
def make_collars():
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.6), dpi=150)
    # spread angle: point=narrow, semi=medium, spread=wide
    configs = [
        ("Point", 18, False, "Narrow gap. Traditional,\nslims the face. Good w/ tie."),
        ("Semi-spread", 55, False, "The all-rounder.\nWorks tie OR open."),
        ("Spread", 95, False, "Wide gap. Modern, formal,\nauthority. Best w/ tie."),
        ("Button-down (OCBD)", 50, True, "Collar buttons down.\nCasual; ideal tie-less."),
    ]
    for ax, (name, angle, bd, note) in zip(axes, configs):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
        # neck/shirt body
        ax.add_patch(Polygon([(2, 0), (8, 0), (8, 4.5), (2, 4.5)], closed=True, fc="#eef1f6", ec="#c8ccd4"))
        # collar band
        ax.add_patch(Rectangle((3.4, 4.3), 3.2, 0.5, fc="#ffffff", ec="#b9bec8"))
        # collar leaves spread by angle
        import math
        a = math.radians(angle / 2)
        tipx = 1.9 * math.sin(a)
        tipy = 1.9 * math.cos(a)
        # left leaf
        ax.add_patch(Polygon([(5, 4.8), (5 - 0.2, 7.6), (5 - tipx - 0.6, 7.6 - tipy + 1.0), (4.2, 4.8)],
                             closed=True, fc="#ffffff", ec=INK, lw=1.3))
        ax.add_patch(Polygon([(5, 4.8), (5 + 0.2, 7.6), (5 + tipx + 0.6, 7.6 - tipy + 1.0), (5.8, 4.8)],
                             closed=True, fc="#ffffff", ec=INK, lw=1.3))
        # tie knot triangle for the gap
        ax.add_patch(Polygon([(5, 4.9), (4.6, 6.4), (5.4, 6.4)], closed=True, fc="#3a4a6b", ec=INK, lw=0.8))
        if bd:
            ax.add_patch(Circle((4.25, 5.0), 0.12, fc="#2b2b2b"))
            ax.add_patch(Circle((5.75, 5.0), 0.12, fc="#2b2b2b"))
        ax.text(5, 9.2, name, ha="center", fontsize=11.5, weight="bold", color=INK)
        ax.text(5, -0.2, note, ha="center", va="top", fontsize=8.3, color=SUB)
    fig.suptitle("Dress-shirt collar styles", fontsize=13, color=INK, y=1.04)
    fig.savefig(os.path.join(OUT, "collars.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- cuffs
def make_cuffs():
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.4), dpi=150)
    # barrel
    ax = axes[0]; ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.add_patch(Rectangle((2.5, 1), 5, 6, fc="#eef1f6", ec="#c8ccd4"))
    ax.add_patch(Rectangle((2.3, 1), 5.4, 1.8, fc="#ffffff", ec=INK, lw=1.4))
    ax.add_patch(Circle((6.9, 1.9), 0.18, fc="#2b2b2b"))
    ax.text(5, 8.4, "Barrel (button) cuff", ha="center", fontsize=11, weight="bold", color=INK)
    ax.text(5, 0.2, "Standard. Closes with a button.\nCorrect for the no-tie office.", ha="center", va="top", fontsize=8.5, color=SUB)
    # french
    ax = axes[1]; ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.add_patch(Rectangle((2.5, 1), 5, 6, fc="#eef1f6", ec="#c8ccd4"))
    ax.add_patch(Rectangle((2.1, 1), 5.8, 2.4, fc="#ffffff", ec=INK, lw=1.4))
    ax.add_patch(Rectangle((2.1, 1), 5.8, 0.5, fc="#dfe3ea", ec=INK, lw=1))  # fold
    ax.add_patch(Circle((5.0, 1.6), 0.28, fc="#c9a24a", ec=INK, lw=1))       # cufflink
    ax.text(5, 8.4, "French (double) cuff", ha="center", fontsize=11, weight="bold", color=INK)
    ax.text(5, 0.2, "Folds back, closes with a cufflink.\nFormal/black-tie — too dressy for daily.", ha="center", va="top", fontsize=8.5, color=SUB)
    fig.savefig(os.path.join(OUT, "cuffs.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- trouser break
def make_break():
    fig, axes = plt.subplots(1, 3, figsize=(10, 4.6), dpi=150)
    configs = [
        ("No break", 4.6, 0, "Hem just touches shoe.\nClean, modern."),
        ("Quarter break", 4.2, 1, "One soft dimple.\nThe safe default."),
        ("Full break", 3.5, 3, "Fabric pools/folds.\nDated, looks sloppy."),
    ]
    for ax, (name, hem, folds, note) in zip(axes, configs):
        ax.set_xlim(0, 6); ax.set_ylim(0, 13.6); ax.axis("off")
        # leg
        ax.add_patch(Polygon([(2, 11.6), (4, 11.6), (3.9, hem), (2.1, hem)], closed=True,
                             fc="#5b6478", ec=INK, lw=1.3))
        # folds (breaks)
        for i in range(folds):
            yy = hem + 0.1 + i * 0.34
            ax.plot([2.1, 3.9], [yy, yy - 0.15], color="#2b3140", lw=1.4)
        # shoe
        ax.add_patch(FancyBboxPatch((1.6, 1.6), 3.2, 0.8, boxstyle="round,pad=0.05,rounding_size=0.3",
                                    fc="#5e4029", ec=INK, lw=1))
        ax.add_patch(Polygon([(2.0, 2.4), (4.7, 2.4), (4.4, hem - 0.1), (2.1, hem - 0.1)],
                             closed=True, fc="#8a5a36", ec=INK, lw=1.2))
        ax.text(3, 12.9, name, ha="center", fontsize=11.5, weight="bold", color=INK)
        ax.text(3, 0.6, note, ha="center", va="top", fontsize=8.5, color=SUB)
    fig.suptitle("Trouser “break” — how the hem meets the shoe", fontsize=12.5, color=INK, y=1.0)
    fig.savefig(os.path.join(OUT, "trouser_break.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- canvas construction
def make_canvas():
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.4), dpi=150)
    def jacket(ax, title, fill_full, fill_half, glued, verdict, vcolor):
        ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
        # jacket front silhouette
        outline = [(2, 0.5), (7.5, 0.5), (8, 9), (6.5, 11), (5.2, 7.5), (3.0, 11), (2.0, 9)]
        ax.add_patch(Polygon(outline, closed=True, fc="#3a4a6b", ec=INK, lw=1.6))
        # canvas overlay region (hatched)
        if fill_full:
            region = [(2.7, 1.0), (6.9, 1.0), (7.2, 9), (6.0, 10.6), (5.2, 7.8), (3.4, 10.6), (2.6, 9)]
            ax.add_patch(Polygon(region, closed=True, fill=False, hatch="////", ec="#ffd27f", lw=0.8))
        if fill_half:
            region = [(2.9, 5.2), (6.7, 5.2), (7.0, 9), (6.0, 10.6), (5.2, 7.8), (3.4, 10.6), (2.7, 9)]
            ax.add_patch(Polygon(region, closed=True, fill=False, hatch="////", ec="#ffd27f", lw=0.8))
        if glued:
            ax.text(5, 4.5, "glued\nfusible", ha="center", fontsize=9, color="#ffd0d0", style="italic")
        ax.text(5, 11.7, title, ha="center", fontsize=11.5, weight="bold", color=INK)
        ax.text(5, -0.4, verdict, ha="center", va="top", fontsize=8.8, weight="bold", color=vcolor)
    jacket(axes[0], "Full canvas", True, False, False, "Best drape & longevity.\nPriciest.", "#2b6b2b")
    jacket(axes[1], "Half canvas", False, True, False, "Canvas in chest/lapel,\nfused below. VALUE PICK.", "#2b6b2b")
    jacket(axes[2], "Fused", False, False, True, "Glued throughout. Stiff,\ncan bubble. AVOID.", "#9c2b2b")
    # legend
    axes[1].add_patch(Polygon([(0.2, 11.4), (0.9, 11.4), (0.9, 11.9), (0.2, 11.9)], closed=True,
                              fill=False, hatch="////", ec="#caa24a", lw=0.8))
    axes[1].text(1.0, 11.65, "= floating canvas layer", fontsize=7.5, va="center", color=SUB)
    fig.suptitle("Jacket construction — the #1 quality tell (pinch below the bottom button)", fontsize=11.5, color=INK, y=1.02)
    fig.savefig(os.path.join(OUT, "canvas.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- watch types
def make_watches():
    fig, axes = plt.subplots(1, 3, figsize=(11, 4), dpi=150)
    def watch(ax, shape, title, note, sporty=False):
        ax.set_xlim(0, 10); ax.set_ylim(-1.5, 10); ax.axis("off")
        # strap
        ax.add_patch(Rectangle((4.2, 7.6), 1.6, 2.0, fc="#6b4a32", ec=INK, lw=1))
        ax.add_patch(Rectangle((4.2, -0.4), 1.6, 2.0, fc="#6b4a32", ec=INK, lw=1))
        if shape == "round":
            ax.add_patch(Circle((5, 4.5), 2.4, fc="#dfe4ec", ec=INK, lw=2))
            if sporty:
                ax.add_patch(Circle((5, 4.5), 2.4, fc="#1e2733", ec=INK, lw=2))
                for h in range(12):
                    import math
                    a = math.radians(h * 30)
                    ax.plot([5 + 1.9*math.sin(a), 5 + 2.15*math.sin(a)],
                            [4.5 + 1.9*math.cos(a), 4.5 + 2.15*math.cos(a)], color="#e8e8e8", lw=2)
            else:
                ax.add_patch(Circle((5, 4.5), 2.4, fc="#eef0f4", ec=INK, lw=2))
            ax.plot([5, 5], [4.5, 6.1], color=INK, lw=2)
            ax.plot([5, 6.0], [4.5, 4.5], color=INK, lw=2)
            ax.add_patch(Circle((5, 4.5), 0.12, fc=INK))
        else:  # rectangular (tank)
            ax.add_patch(FancyBboxPatch((3.1, 2.1), 3.8, 4.8, boxstyle="round,pad=0.05,rounding_size=0.25",
                                        fc="#eef0f4", ec=INK, lw=2))
            ax.plot([5, 5], [4.5, 6.0], color=INK, lw=1.6)
            ax.plot([5, 5.8], [4.5, 4.5], color=INK, lw=1.6)
        ax.text(5, 9.0, title, ha="center", fontsize=11, weight="bold", color=INK)
        ax.text(5, -1.4, note, ha="center", va="top", fontsize=8.3, color=SUB)
    watch(axes[0], "round", "Round dress watch", "e.g. Rolex Datejust/Explorer,\nNomos, Grand Seiko. Quietly correct.")
    watch(axes[1], "rect", "Rectangular dress", "e.g. Cartier Tank.\nThe “intellectual’s” watch — culture, not flex.")
    watch(axes[2], "round", "Steel sports watch", "e.g. Tudor/Omega diver.\nFine; the hyped ones can read try-hard.", sporty=True)
    fig.suptitle("Watch archetypes — quiet status lives in the dress/tool register", fontsize=11.5, color=INK, y=1.02)
    fig.savefig(os.path.join(OUT, "watches.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- tie knots
def make_knots():
    fig, axes = plt.subplots(1, 2, figsize=(8, 4.4), dpi=150)
    def knot(ax, title, width, note, good):
        ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")
        # collar
        ax.add_patch(Polygon([(3, 11), (5, 9), (7, 11)], closed=False, fill=False, ec="#aab0bc", lw=2))
        # knot
        ax.add_patch(Polygon([(5 - width, 9.5), (5 + width, 9.5), (5 + width*0.6, 8.0), (5 - width*0.6, 8.0)],
                             closed=True, fc="#5a2230", ec=INK, lw=1.4))
        # tie blade
        ax.add_patch(Polygon([(5 - width*0.55, 8.0), (5 + width*0.55, 8.0), (5 + 0.7, 1.0), (5, 0.2), (5 - 0.7, 1.0)],
                             closed=True, fc="#6a2838", ec=INK, lw=1.2))
        ax.text(5, 11.4, title, ha="center", fontsize=11.5, weight="bold", color=INK)
        c = "#2b6b2b" if good else "#9c2b2b"
        ax.text(5, -0.2, note, ha="center", va="top", fontsize=8.5, color=c, weight="bold")
    knot(axes[0], "Four-in-hand", 0.95, "Small, slightly asymmetric.\nThe old-money knot.", True)
    knot(axes[1], "Full Windsor", 1.7, "Big, symmetric triangle.\nReads salesman to insiders.", False)
    fig.suptitle("Tie knots — smaller is more refined", fontsize=12, color=INK, y=1.02)
    fig.savefig(os.path.join(OUT, "knots.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

# ---------------------------------------------------------------- the social uniform
def make_uniform():
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis("off")
    # blazer
    ax.add_patch(Polygon([(1, 9), (4.5, 9), (4.6, 3), (1.0, 3), (0.9, 7)], closed=True, fc="#26324e", ec=INK, lw=1.5))
    ax.add_patch(Polygon([(2.4, 9), (3.1, 9), (2.9, 6.2), (2.6, 6.2)], closed=True, fc="#eef1f6", ec="#c8ccd4"))  # shirt V
    ax.text(2.7, 2.4, "Navy hopsack\nblazer", ha="center", fontsize=9, color=INK)
    # trousers
    ax.add_patch(Polygon([(5.3, 8.5), (8.3, 8.5), (8.0, 1.5), (6.9, 1.5), (6.8, 5), (6.7, 1.5), (5.6, 1.5)],
                         closed=True, fc="#8a8e96", ec=INK, lw=1.4))
    ax.text(6.8, 0.9, "Mid-grey\ntrousers", ha="center", fontsize=9, color=INK)
    # loafer
    ax.add_patch(FancyBboxPatch((9.0, 4.2), 2.6, 0.9, boxstyle="round,pad=0.05,rounding_size=0.35",
                                fc="#6b3f24", ec=INK, lw=1.3))
    ax.add_patch(Polygon([(9.2, 5.0), (11.4, 5.0), (11.0, 6.1), (9.4, 6.1)], closed=True, fc="#8a5a36", ec=INK, lw=1.2))
    ax.text(10.3, 3.6, "Brown loafers", ha="center", fontsize=9, color=INK)
    ax.text(6, 9.7, "THE SOCIAL UNIFORM", ha="center", fontsize=13, weight="bold", color=INK)
    fig.savefig(os.path.join(OUT, "uniform.png"), bbox_inches="tight", facecolor="white")
    plt.close(fig)

if __name__ == "__main__":
    make_fabric_swatches()
    make_leather_strip()
    make_oxford_derby()
    make_toe_shapes()
    make_shoe_styles()
    make_collars()
    make_cuffs()
    make_break()
    make_canvas()
    make_watches()
    make_knots()
    make_uniform()
    print("All diagrams generated in", OUT)
    print(sorted(f for f in os.listdir(OUT) if f.endswith(".png")))
