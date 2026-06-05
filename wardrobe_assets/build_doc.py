#!/usr/bin/env python3
"""Build the illustrated wardrobe guide as a .docx (opens natively in Google Docs)."""
import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.shared import OxmlElement, qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

A = os.path.dirname(os.path.abspath(__file__))
def img(n): return os.path.join(A, n)

doc = Document()

# ---- base styling
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
NAVY = RGBColor(0x1F, 0x2D, 0x4E)
GREY = RGBColor(0x55, 0x55, 0x55)
GREEN = RGBColor(0x2B, 0x6B, 0x2B)
RED = RGBColor(0x9C, 0x2B, 0x2B)

def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    hl = OxmlElement("w:hyperlink"); hl.set(qn("r:id"), r_id)
    r = OxmlElement("w:r"); rPr = OxmlElement("w:rPr")
    c = OxmlElement("w:color"); c.set(qn("w:val"), "0563C1"); rPr.append(c)
    u = OxmlElement("w:u"); u.set(qn("w:val"), "single"); rPr.append(u)
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "18"); rPr.append(sz)
    r.append(rPr)
    t = OxmlElement("w:t"); t.text = text; r.append(t)
    hl.append(r); paragraph._p.append(hl)

def photo_link(query, label="🔗 See real photos online"):
    p = doc.add_paragraph()
    url = "https://www.google.com/search?tbm=isch&q=" + query.replace(" ", "+")
    add_hyperlink(p, url, label)
    p.paragraph_format.space_after = Pt(6)

def h1(text):
    p = doc.add_heading(text, level=1)
    for r in p.runs: r.font.color.rgb = NAVY
    return p

def h2(text):
    p = doc.add_heading(text, level=2)
    for r in p.runs: r.font.color.rgb = NAVY
    return p

def para(text, italic=False, color=None, bold=False, size=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = italic; r.bold = bold
    if color is not None: r.font.color.rgb = color
    if size: r.font.size = Pt(size)
    return p

def bullet(text, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet")
    if bold_lead:
        r = p.add_run(bold_lead); r.bold = True
        p.add_run(text)
    else:
        p.add_run(text)
    return p

def figure(fname, width=6.2, caption=None):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(img(fname), width=Inches(width))
    if caption:
        c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.add_run(caption); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = GREY

def swatch_grid(items, cols=4, w=1.45):
    """items = list of (filename, label, sublabel)."""
    rows = (len(items) + cols - 1) // cols
    t = doc.add_table(rows=rows * 2, cols=cols)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, (fname, label, sub) in enumerate(items):
        r, c = (i // cols) * 2, i % cols
        cell = t.cell(r, c)
        pp = cell.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pp.add_run().add_picture(img(fname), width=Inches(w))
        lab = t.cell(r + 1, c).paragraphs[0]; lab.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rr = lab.add_run(label); rr.bold = True; rr.font.size = Pt(9.5)
        if sub:
            lab.add_run("\n" + sub).font.size = Pt(8)
    doc.add_paragraph()

# ============================================================ TITLE
title = doc.add_paragraph(); title.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title.add_run("THE PARTNER-TRACK WARDROBE")
tr.bold = True; tr.font.size = Pt(26); tr.font.color.rgb = NAVY
sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sub.add_run("A Visual Field Guide to Dressing for Quiet Status")
sr.italic = True; sr.font.size = Pt(14); sr.font.color.rgb = GREY
meta = doc.add_paragraph(); meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
mr = meta.add_run("Tailored for: warm-climate (US South / Southwest / West) client base  ·  "
                  "menswear  ·  mid-premium “smart value”  ·  status without flash")
mr.font.size = Pt(10); mr.font.color.rgb = GREY
doc.add_paragraph()

note = doc.add_paragraph()
note.add_run("How to use this guide.  ").bold = True
note.add_run("Every diagram and fabric swatch here was drawn specifically to teach the "
             "vocabulary — these are illustrations, not photos. Under each term you'll find a blue ")
add_hyperlink(note, "https://www.google.com/search?tbm=isch&q=menswear", "“See real photos online”")
note.add_run(" link; click it to pull up live examples on your screen. Read this top-to-bottom once; "
             "after that it's a reference. The buying plan at the end tells you what to get first.")
doc.add_paragraph()

# ============================================================ 0. THE ONE IDEA
h1("The One Idea Everything Hangs On")
para("In the rooms you're trying to enter, status is signaled by discernment and restraint — not by "
     "spending visibly. The academic name for this is inconspicuous consumption (Elizabeth "
     "Currid-Halkett, The Sum of Small Things, 2017): the modern elite abandoned logos because logos "
     "are now cheap to fake and therefore worthless as a marker. Today wealth is read through fit, "
     "fabric, craftsmanship, grooming, and demonstrated knowledge — cues only insiders decode.")
para("Fit  >  fabric  >  restraint.  No visible logos. Muted solids. Natural fibers. A matte finish. "
     "One good watch. And the evident ease of a man who isn't trying to impress anyone.",
     bold=True, color=NAVY)
para("Loud branding now signals the opposite of wealth — it reads as hungry, not secure. Keep that "
     "lens on every choice below.", italic=True, color=GREY)

# ============================================================ 1. SUITS
h1("1.  Suits — Your High-Impact Tool, Not a Daily Uniform")
para("Reality check: in modern consulting the everyday suit is largely gone. The rule is still "
     "“dress one notch better than your client,” but the baseline dropped — partners live in sport "
     "coats and odd trousers, and pull out a real suit for the pitch, the board readout, the final "
     "presentation, or the banking/insurance/pharma/government client. So you need few suits, but "
     "excellent ones. Start with two solids: navy and charcoal (or mid-grey).")

h2("Suit colors — what reads serious")
swatch_grid([
    ("sw_navy.png", "Navy", "#1 — dynamic credibility"),
    ("sw_charcoal.png", "Charcoal", "sober authority"),
    ("sw_midgrey.png", "Mid-grey", "versatile, cool in heat"),
    ("sw_black.png", "Black", "AVOID by day (funeral/waiter)"),
])
photo_link("navy charcoal grey business suit")

h2("Suit patterns — from quietest to loudest")
para("A “solid” is one flat color. The patterns below add subtle interest. The first three read as "
     "solid from across a room (safe and high-status); the last three get progressively bolder. "
     "For your goal, stay in the top row.")
swatch_grid([
    ("sw_birdseye.png", "Birdseye", "tiny dots — reads solid"),
    ("sw_nailhead.png", "Nailhead", "slightly bigger dots"),
    ("sw_sharkskin.png", "Sharkskin", "fine diagonal weave"),
    ("sw_pinstripe.png", "Pinstripe", "thin crisp lines — banker"),
    ("sw_chalkstripe.png", "Chalk stripe", "softer, wider — bolder"),
    ("sw_glencheck.png", "Glen check", "the “Prince of Wales” check"),
    ("sw_windowpane.png", "Windowpane", "wide grid — too loud for suits"),
], cols=4)
para("Quiet-wealth sweet spot: solids and the “semi-solids” (birdseye, nailhead, sharkskin) — same "
     "formality as a solid, with quiet depth. A faint glen-check grey is a tasteful third suit. Skip "
     "chalk stripe and windowpane — they say “look at me.”", italic=True, color=GREY)
photo_link("birdseye nailhead sharkskin glen check suit fabric")

h2("Fabric & weight — the most important choice for the heat")
para("The variable that keeps you cool isn't just weight — it's the weave. An open, airy weave vents "
     "heat far better than a dense one. Your targets:")
bullet("— the top warm-weather cloth. Tightly twisted yarn in an open weave; breathes like linen but "
       "resists wrinkles all day, so you look composed while everyone else is crumpled.",
       bold_lead="High-twist worsted / “fresco” ")
bullet("— softer and dressier than fresco; great if fresco feels a touch coarse to you.",
       bold_lead="Tropical worsted (~230 gsm / 8–10 oz) ")
bullet("— a loose basketweave (shown below). Breathable, springs back from wrinkles, but reads "
       "casual — it's a blazer/sport-coat cloth, not a formal-suit cloth.", bold_lead="Hopsack ")
bullet("for client work (wrinkles aggressively — keep it for weekend jackets); avoid synthetics "
       "entirely (sheen + sweat); insist on breathable Bemberg/cupro lining, and prefer half- or "
       "quarter-lined jackets.", bold_lead="Skip linen ")
figure("sw_hopsack.png", width=2.6, caption="Hopsack: the open basketweave you can see up close — breezy, casual, blazer territory.")
photo_link("tropical wool fresco suit warm weather")

h2("Construction — the #1 quality tell")
para("Inside the chest of a good jacket floats a layer of “canvas” that lets it mold to your body and "
     "drape cleanly. A cheap jacket glues a stiff “fusible” layer instead — it feels like cardboard "
     "and can bubble after dry-cleaning. The rule:")
para("Avoid fused at all costs. Half-canvas is the value pick. Full canvas only if the budget stretches.",
     bold=True, color=NAVY)
figure("canvas.png", width=6.4)
para("How to check in the store: pinch the front of the jacket just below the bottom button. If you "
     "feel a separate floating layer between the outer cloth and the lining, it's canvassed (good). "
     "If it feels glued into one stiff sheet, it's fused (skip it).", italic=True, color=GREY)
photo_link("half canvas vs fused suit construction")

h2("Fit — “modern classic,” never shrunken-slim, never baggy")
bullet("the seam ends right at your shoulder bone — no overhang, no pulling. This is the hardest "
       "thing to alter, so it must be right off the rack.", bold_lead="Shoulder: ")
bullet("the jacket covers your seat; too-short reads “trying too hard.”", bold_lead="Length: ")
bullet("show about ¼–½ inch of shirt cuff below the jacket sleeve.", bold_lead="Sleeve: ")
bullet("slight taper, hem just kissing the shoe (see “break” in the next section).", bold_lead="Trousers: ")
photo_link("well fitted navy suit men")

h2("Mid-premium brands worth your money")
bullet("best price-to-quality; has a purpose-built warm-weather “tropical” line.", bold_lead="Spier & Mackay — ")
bullet("the benchmark; their made-to-measure (~$660–715) even gets you full canvas in tropical cloth.",
       bold_lead="Suitsupply — ")
bullet("best remote made-to-measure for fit precision + breathable fabrics.", bold_lead="Proper Cloth — ")
bullet("solid on sale; Brooks Brothers 1818 is fine if you confirm it isn't fused.",
       bold_lead="J.Crew Ludlow — ")

# ============================================================ 2. BUSINESS CASUAL
h1("2.  The Consultant's Real Uniform — Business Casual")
para("This is what you'll actually wear most days, and where most of your status signal now lives. "
     "The cornerstone is the navy hopsack blazer: a “sport coat” (a jacket worn with non-matching "
     "trousers) in that breathable basketweave. One blazer dresses up with a shirt and tie, or down "
     "with a fine knit — endlessly. Go for a soft, lightly-structured jacket; a fully “deconstructed” "
     "one (no internal structure at all) flatters only a minority of builds.")
photo_link("navy hopsack blazer chinos business casual")

h2("Trousers & the “break”")
para("“Break” is how the trouser hem meets your shoe — the small fold (or lack of one) at the bottom. "
     "It's one of the quickest tells of whether trousers were hemmed by someone who knows what they're "
     "doing. Aim for no break or a quarter break; avoid the dated “full break” pooling.")
figure("trouser_break.png", width=6.0)
para("Fabrics: high-twist/tropical wool for the dressy end, quality cotton chinos for everyday "
     "(pressed, never wrinkled). Palette: grey, stone, olive, navy. Flat front is the safe default.",
     italic=True, color=GREY)
photo_link("trouser break no break quarter break men")

h2("Dress-shirt collars")
para("The collar shape sets how formal a shirt looks and whether it works without a tie. The gap "
     "between the collar points widens as you go from point → spread.")
figure("collars.png", width=6.6)
bullet("the best all-rounder — works with a tie or open at the neck.", bold_lead="Semi-spread: ")
bullet("more formal/authoritative with a tie; needs enough body to not collapse when open.",
       bold_lead="Spread / point: ")
bullet("the collar literally buttons down to the shirt; casual, and the ideal collar for the "
       "no-tie look because it stays put instead of flopping open.", bold_lead="Button-down (OCBD): ")
photo_link("dress shirt collar styles spread semi-spread point button-down")

h2("Cuffs")
para("Two kinds. For a no-tie consulting office you want the everyday barrel cuff. French (double) "
     "cuffs need cufflinks and read black-tie-formal — too dressy for daily wear.")
figure("cuffs.png", width=4.8)
photo_link("barrel cuff vs french cuff shirt")

para("Shirt colors: white (most formal) and light blue (everyday) are your core. Subtle stripes or "
     "micro-checks for casual days only. Fabrics: poplin (crispest/dressiest) → twill → oxford-cloth "
     "(most casual, the home of the button-down). Knitwear: fine-gauge merino polos and crewnecks "
     "read upscale; avoid heavy logo'd “golf-dad” piqué polos in corporate-bright colors.",
     italic=False)

# ============================================================ 3. SHOES
h1("3.  Shoes, Belts & Leather — Where the Cognoscenti Look First")
para("The quality signal in a shoe is resoleable welted construction. A “Goodyear-welted” shoe is "
     "stitched (not glued) so it can be resoled and last decades; cheap shoes are glued and die when "
     "the sole wears. Insiders genuinely read this.")

h2("The single most useful distinction: Oxford vs. Derby")
para("This is the term people most often get wrong. It's about the lacing, not the toe:")
figure("oxford_vs_derby.png", width=6.6)
photo_link("oxford vs derby shoe difference closed open lacing")

h2("Styles, most formal → most casual")
figure("shoe_styles.png", width=6.8)
para("In your warm climate, penny loafers and suede loafers/derbies are the smart-casual workhorses; "
     "own one pair of black cap-toe oxfords for the formal end.", italic=True, color=GREY)
photo_link("cap toe oxford wholecut monk strap penny loafer tassel loafer")

h2("Toe shape — a quiet cheap-shoe giveaway")
figure("toe_shapes.png", width=6.6)
photo_link("shoe toe shapes round almond square chiseled")

h2("Leather color — formality runs light → dark")
para("“No brown in town” has been dead since the 1950s; brown is your everyday default. Reserve black "
     "for the most formal settings. Oxblood/burgundy is a knowing, high-status choice with navy and grey.")
figure("leather_shades.png", width=6.6)
photo_link("brown dress shoes chestnut dark oak oxblood")

h2("Belts & socks")
bullet("match the belt's leather color AND finish to your shoes (shiny belt with shiny shoes; "
       "matte/suede with matte). Keep the buckle plain and small — a logo buckle is the clearest "
       "“trying too hard” tell. Skip the belt entirely with a tux or side-adjuster trousers.",
       bold_lead="Belts: ")
bullet("wear over-the-calf length so no shin shows when you cross your legs; match socks to your "
       "trousers, not your shoes. White athletic socks with dress shoes is the #1 mistake. For "
       "loafers in heat, use no-show socks with a silicone grip — never go truly sockless (it ruins "
       "the lining).", bold_lead="Socks: ")
photo_link("over the calf dress socks loafers no show")

para("Brands at smart value: Allen Edmonds “Park Avenue” on sale (~$250–350), Carmina (~$475, the "
     "quality sweet spot), Loake 1880 / Meermin (entry Goodyear-welt). Keep them on cedar shoe trees, "
     "brush them, and resole rather than replace — well-kept shoes are themselves a quiet-wealth signal.",
     italic=True, color=GREY)

# ============================================================ 4. WATCHES & ACCESSORIES
h1("4.  Watches & Accessories — Handled Right")
para("The watch is the single biggest male status signal — and the easiest place to out yourself as "
     "new money. The principle: the right watch is legible only to people who know. A watch worn to be "
     "seen across a room reads as insecurity. Quiet status lives in the dress and tool registers, not "
     "the flashy gold or hyped pieces.")
figure("watches.png", width=6.6)
bullet("steel Rolex Datejust/Explorer, Cartier Tank (the “intellectual's” watch), Grand Seiko, Nomos. "
       "At mid-premium: Tudor (Rolex-owned, ~$4k), Omega, Nomos.", bold_lead="Quietly correct: ")
bullet("gold/two-tone, diamond bezels, oversized “trophy” watches. An Apple Watch is fine but neutral "
       "— it signals busyness, not taste; if you wear one with tailoring, use a leather band.",
       bold_lead="Reads try-hard: ")
photo_link("Rolex Datejust Explorer Cartier Tank Tudor Black Bay dress watch")

h2("Ties & the knot")
para("Ties have receded to client days, pitches, and formal meetings; a deliberate open collar is now "
     "a legitimate senior move. When you do wear one, the knot matters more than people think — smaller "
     "is more refined.")
figure("knots.png", width=4.8)
bullet("textured “grenadine” silk (matte, not shiny) in solid navy or burgundy is almost foolproof. "
       "Tie it with a four-in-hand knot. Avoid shiny satin and novelty/logo ties.",
       bold_lead="Ties: ")
photo_link("grenadine tie four in hand knot navy burgundy")

h2("Everything else — keep it quiet")
bullet("white linen, folded flat. Never match it exactly to your tie (looks pre-packaged).",
       bold_lead="Pocket square: ")
bullet("understated, logo-free frames (Oliver Peoples, Cutler & Gross, Garrett Leight).",
       bold_lead="Eyewear: ")
bullet("a single unbranded quality leather piece beats logo luggage every time. Monogram/print bags "
       "(LV, Goyard, Gucci) are a top new-money tell.", bold_lead="Bags: ")
bullet("wedding band + watch and essentially nothing else. Slim plain wallet. Persol sunglasses over "
       "flashy designer shades.", bold_lead="Jewelry: ")
photo_link("white linen pocket square flat fold suit")

# ============================================================ 5. SOCIAL
h1("5.  Dinner Parties, Client Dinners & Social Events")
para("Memorize one combination and you're covered for almost any social or client-entertainment "
     "setting: navy blazer + grey trousers + brown loafers, with a white or light-blue shirt.")
figure("uniform.png", width=5.0, caption="The social uniform — works from a partner's dinner to a client restaurant to a bar.")
bullet("pair one dressier item with one casual item, and when unsure, dress one notch up (a jacket "
       "can always come off).", bold_lead="Smart casual decoded: ")
bullet("the social uniform above, or dark clean denim + a casual button-down + loafers. No full suit "
       "— it reads stiff in someone's home.", bold_lead="Partner's dinner (at home): ")
bullet("sport coat with an open collar (or a fine roll-neck when cooler). Tie optional, often omitted.",
       bold_lead="Client dinner (restaurant): ")
bullet("quality polos, well-fitting chinos, tailored above-knee shorts in real heat. Keep performance "
       "polyester to the course, not the clubhouse.", bold_lead="Country club / golf: ")
bullet("dark, clean, well-fitted, no rips or fading. Dress the jacket down (light textured sport coat), "
       "never the jeans up. Never a t-shirt under the coat.", bold_lead="Good denim in upscale-casual: ")
photo_link("navy blazer grey trousers loafers smart casual men")

# ============================================================ 6. MISTAKES
h1("6.  The Mistakes That Mark You as an Outsider")
mistakes = [
    "Visible logos / monograms — the cardinal sin; now reads new-money.",
    "Shiny fabric — the classic cheap-synthetic tell (quality wool is matte).",
    "Bad shoulder fit, “X” pull-lines at the button, wrong sleeve or trouser length.",
    "A flashy gold/diamond “trophy” watch — or an Apple sport-loop with a suit.",
    "Matched tie-and-pocket-square sets; a big shiny Windsor knot.",
    "White or athletic socks with dress shoes; socks that show ankle when seated.",
    "Square-toe or plasticky “corrected-grain” shoes; logo belt buckles.",
    "Heavy logo'd golf polos in corporate-bright colors.",
    "Over-tight, “sprayed-on” tailoring — strained buttons read trying-too-hard.",
    "Distressed or faded jeans in an upscale setting.",
]
for m in mistakes:
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run("✗  "); r.bold = True; r.font.color.rgb = RED
    p.add_run(m)

# ============================================================ 7. BUYING PLAN
h1("7.  Your Prioritized Buying Plan")
para("Buy in this order — each tier delivers the most status-per-dollar before the next.")

def tier_table(title, rows):
    h2(title)
    t = doc.add_table(rows=len(rows) + 1, cols=2)
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for cell, txt in zip(hdr, ["Item", "What to get / notes"]):
        r = cell.paragraphs[0].add_run(txt); r.bold = True
    for i, (item, note) in enumerate(rows, start=1):
        c = t.rows[i].cells
        c[0].paragraphs[0].add_run(item).bold = True
        c[1].paragraphs[0].add_run(note)
    doc.add_paragraph()

tier_table("Tier 1 — the anchors (do these first)", [
    ("Navy suit", "Half-canvas, tropical/high-twist wool. Spier & Mackay or Suitsupply (MTM gets full canvas); Proper Cloth for remote fit."),
    ("Black cap-toe oxfords", "Goodyear-welted. Allen Edmonds Park Avenue on sale (~$250–350) or Carmina (~$475)."),
    ("Navy hopsack blazer", "The cornerstone. Spier & Mackay (~$250 on sale) or Suitsupply Havana."),
    ("A good watch", "Highest-leverage single signal. Tudor, Omega, Grand Seiko, Nomos — or a Cartier Tank / steel Datejust if you stretch."),
])
tier_table("Tier 2 — round out the uniform", [
    ("Charcoal/grey suit", "Same fabric & construction logic as the navy."),
    ("Dress shirts ×3", "White + light-blue poplin (semi-spread), one button-down oxford. Proper Cloth MTM (~$125) or Spier & Mackay."),
    ("Brown shoes", "A chestnut/dark-oak derby or penny loafer + one suede loafer for the heat."),
    ("Trousers", "Grey + stone tropical wool or quality chinos (Sid Mashburn, Todd Snyder — size up at Sid Mashburn)."),
    ("Fine merino knits ×2–3", "John Smedley, Sunspel, Luca Faloni; Uniqlo extra-fine merino is a budget sleeper."),
    ("Belts & socks", "One belt matching each shoe finish; over-the-calf socks."),
])
tier_table("Tier 3 — the finishing signals", [
    ("Ties & pocket squares", "Navy + burgundy grenadine ties; white linen squares."),
    ("Eyewear & sunglasses", "Logo-free frames; Persol sunglasses."),
    ("Bag & shoe care", "One unbranded leather bag; cedar shoe trees + a horsehair brush."),
])

# ============================================================ CAVEATS + SOURCES
h1("Two Honest Caveats")
bullet("The “old-money insider code” is eroding under social media, so chasing a recognizable “quiet "
       "luxury aesthetic” can itself look trend-driven. The durable move is the timeless fundamentals "
       "— fit, fabric, restraint — not the hashtag.", bold_lead="1.  ")
bullet("Norms are office-, partner-, and engagement-specific. Read your actual partners and clients; "
       "“dress for the client” always wins over any rule in this guide.", bold_lead="2.  ")

doc.add_paragraph()
h2("Where this comes from")
para("Synthesized from menswear and horology authorities and the academic literature on status "
     "signaling, including: Permanent Style, Put This On, Die Workwear, Gentleman's Gazette, He Spoke "
     "Style, Hodinkee, A Collected Man, StyleForum, Dappered, and Elizabeth Currid-Halkett's "
     "“The Sum of Small Things” (Princeton, 2017). Diagrams and swatches were drawn for this guide to "
     "illustrate the terminology; use the blue links throughout for live photo examples.",
     italic=True, color=GREY, size=9)

out = os.path.join(A, "Partner-Track_Wardrobe_Guide.docx")
doc.save(out)
print("Saved", out)
