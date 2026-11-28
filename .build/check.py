"""Checks for the two landing pages (zh/index.html and index.html). Run from the site root:

    python3 .build/check.py [--spec ../spec/design/tokens.css]

What it checks, and why:
  1. tokens      the colours, radii and sizes in the pages are the spec's design tokens, value for value
  2. words       none of the words the glossary does not use, and none of the claims the marketing brief
                 says must not be made (spec product/glossary.md; marketing content/landing-refresh)
  3. gold        gold is only on the "worth a deep dive" verdict (dot and word) and the calendar's gold dot
  4. one button  every button outside the confirmation window has the same label (the one main button)
  5. examples    every example card carries the badge; the three cards are there
  6. parity      the English page has the same structure as the Chinese one, and is what make_en.py makes
  6b. form       the English form offers every value the Worker accepts (so nobody who could sign up before cannot now),
                 the Chinese form only values the Worker accepts; the two forms differ in the three English-only sources
                 and nowhere else; the English headline phrase is not `nowrap` (it overflowed a 360px screen)
  7. links       every in-page link has its target; every file the pages name exists
  8. llms.txt    the text for assistants (/llms.txt) makes none of the claims the pages must not make, and the share
                 image: no draft is served or named by a page. With --release it also fails while the share image
                 is still the old one (it has the old tagline in the picture): run it that way before publishing.
It reports every problem and exits 1. Needs only Python 3."""
import hashlib
import html
import os
import re
import subprocess
import sys

ROOT = os.getcwd()
PAGES = {"zh": "zh/index.html", "en": "index.html"}
text = {k: open(v, encoding="utf-8").read() for k, v in PAGES.items()}
fails = []


def fail(group, msg):
    fails.append(f"[{group}] {msg}")


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


# ---------------------------------------------------------------- 1. tokens
def tokens(css):
    """{(context, name): value} for the three places the spec sets them."""
    css = strip_comments(css)
    out = {}
    def decls(block, ctx):
        for name, value in re.findall(r"(--ke-[a-z0-9-]+)\s*:\s*([^;]+);", block):
            out[(ctx, name)] = " ".join(value.split())
    m = re.search(r"(?m)^\s*:root\s*\{(.*?)\}", css, re.S)
    if m:
        decls(m.group(1), "root")
    m = re.search(r"@media\s*\(max-width:\s*640px\)\s*\{\s*:root\s*\{(.*?)\}", css, re.S)
    if m:
        decls(m.group(1), "phone")
    m = re.search(r"@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*:root:not\(\[data-theme=\"light\"\]\)\s*\{(.*?)\}", css, re.S)
    if m:
        decls(m.group(1), "dark")
    return out


spec_path = None
if "--spec" in sys.argv:
    spec_path = sys.argv[sys.argv.index("--spec") + 1]
else:
    for p in ("../spec/design/tokens.css", "../../spec/design/tokens.css"):
        if os.path.exists(p):
            spec_path = p
            break
if spec_path and os.path.exists(spec_path):
    spec = tokens(open(spec_path, encoding="utf-8").read())
    for k, page in text.items():
        m = re.search(r"/\* tokens:start \*/(.*?)/\* tokens:end \*/", page, re.S)
        if not m:
            fail("tokens", f"{PAGES[k]}: the tokens block is not marked (tokens:start / tokens:end)")
            continue
        mine = tokens(m.group(1))
        for key, value in spec.items():
            if mine.get(key) != value:
                fail("tokens", f"{PAGES[k]}: {key[1]} ({key[0]}) is {mine.get(key)!r}, the spec has {value!r}")
        for key in mine:
            if key not in spec:
                fail("tokens", f"{PAGES[k]}: {key[1]} ({key[0]}) is not in the spec")
else:
    print("tokens: skipped (no spec/design/tokens.css found; pass --spec PATH)")


# ---------------------------------------------------------------- 2. words
def visible(page):
    """What a reader (and a screen reader) gets: the text, and the words in aria-label, placeholder, alt, title, and the head's title and descriptions."""
    head = page[: page.index("<body")]
    body = re.sub(r"<script.*?</script>", " ", page[page.index("<body"):], flags=re.S)
    attrs = re.findall(r'(?:aria-label|placeholder|alt|title)="([^"]*)"', body)
    metas = re.findall(r'<meta (?:name|property)="(?:description|og:description|og:title|twitter:title|twitter:description)" content="([^"]*)"', head)
    titles = re.findall(r"<title>(.*?)</title>", head)
    return html.unescape(" ".join([re.sub(r"<[^>]+>", " ", body), *attrs, *metas, *titles]))


NOT_USED_ZH = ["书签", "知识库", "存档", "搜索", "分类", "首页", "暂存", "钥匙", "API key", "token",
               "千芳", "阅尽", "花蜜", "蜂", "蜜", "凋谢", "封盖", "养蜂", "摇摆舞", "口味", "骨架", "工蜂", "晚课", "攒存",
               "标签(?!页)"]  # a tag is hidden from the user (A6); 标签页 is the browser's own tab
# claims the brief says not to make, and the old page made
NOT_CLAIMED = [
    (r"快捷指令", "iPhone Shortcut (not built)"), (r"菜单栏", "Mac menu bar (not built)"), (r"Shortcut", "iPhone Shortcut (not built)"),
    (r"menu bar", "Mac menu bar (not built)"), (r"PDF", "PDF (not verified live)"), (r"30\s*天|30 days", "a retention period (not decided)"),
    (r"永久|到期|permanent|expire", "a retention promise (not decided)"), (r"五个入口|5 种|five ways|five entry", "the old five ways to save"),
    (r"分享菜单|share sheet|装成应用", "a phone share entry (not verified on devices)"),
    (r"App 随|app comes with", "the phone app coming with the beta"), (r"付费|收费(?!.*内测)|paid|price", "pricing"),
]

# Chrome, Edge and Brave. The extension was tested only in Chromium, so these three may be named only to say they were not tested
# (or were only loaded in a test setup). Two checks, the same for the pages and for llms.txt:
#  1. the whole line: when a browser is named, the approved line about them is there word for word. Nothing can be added to it or swapped
#     for it, not even a claim that names no browser ("saving works in all of them"). When the line is re-approved, change it here in the same commit.
#  2. each clause: a piece of text that names a browser says by itself that it was not tested. A piece ends at . ; : , a bracket, a line end or a
#     word like "but" / 而, so a "not tested" about one browser never covers a claim about another, whichever comes first.
APPROVED_BROWSER_LINE = {
    "zh/index.html": "<li>浏览器扩展点工具栏按钮存入只在 Chromium 里测过；在桌面版 Brave 和 Edge 里只以测试方式加载过、离线打开过选项页，照说明手动安装、连接账号和存入都还没测；Chrome 还没单独试过</li>",
    "index.html": "<li>Saving from the extension's toolbar button was tested only in Chromium. In desktop Brave and Edge it was only loaded in a test setup and its options page opened offline; installing it by hand, connecting your account and saving are not tested there yet. Chrome has not been tried on its own</li>",
    "llms.txt": "(saving from its toolbar button was tested in Chromium; in desktop Brave and Edge it was only loaded in a test setup and its options page opened offline, and installing it by hand, connecting your account and saving are not tested there yet; Chrome has not been tried on its own)",
}
BROWSER = re.compile(r"Chrome|Edge|Brave")
NOT_TESTED = re.compile(r"还没单独试|只以测试方式|还没测|has not been tried|only loaded in a test setup|not tested")
CLAUSE_END = re.compile(r"[。.；;：:，,!?！？()（）\n]|\b(?:but|while|whereas|though|although|except)\b|而|但是?|不过|只是|却|除了", re.I)


def page_units(page):
    """What a reader gets from a page, one string per place: the body without the sign-up form (its questions name tools people use today,
    they are not claims), each attribute value, and the head's title and descriptions. A block ending is a line end, so one list item never runs into the next."""
    body = re.sub(r"<form.*?</form>|<script.*?</script>|<style.*?</style>", " ", page, flags=re.S)
    body = body[body.index("<body"):]
    attrs = re.findall(r'\s(?:aria-label|placeholder|alt|title)="([^"]*)"', body)
    metas = re.findall(r'<meta (?:name|property)="[^"]*" content="([^"]*)"', page[: page.index("<body")])
    titles = re.findall(r"<title>(.*?)</title>", page[: page.index("<body")])
    block = r"</?(?:li|p|h[1-6]|div|ul|ol|dl|dd|dt|table|tr|td|th|section|article|details|summary|header|footer|nav|main|blockquote|figure|figcaption)\b[^>]*>|<br\s*/?>"
    body = re.sub(r"<[^>]+>", " ", re.sub(block, "\n", body))
    return [html.unescape(u) for u in [body, *attrs, *metas, *titles]]


def browser_problems(label, raw, units):
    """label: the file's name (a key of APPROVED_BROWSER_LINE). raw: the file as it is. units: the text a reader gets from it."""
    out = []
    if any(BROWSER.search(u) for u in units) and APPROVED_BROWSER_LINE[label] not in raw:
        out.append("names a browser, but the line about them is not the approved one word for word "
                   "(nothing may be added to it or swapped for it; a re-approved line is changed in APPROVED_BROWSER_LINE in .build/check.py)")
    for u in units:
        for clause in CLAUSE_END.split(u):
            found = sorted(set(BROWSER.findall(clause)))
            if found and not NOT_TESTED.search(clause):
                out.append(f"names {', '.join(found)} as supported (only tested in Chromium): …{' '.join(clause.split())[:120]}…")
    return out


for k, page in text.items():
    vis = visible(page)
    for w in NOT_USED_ZH:
        if re.search(w if w.endswith(")") else re.escape(w), vis, re.I):
            fail("words", f"{PAGES[k]}: uses “{w}” (the glossary does not)")
    for m in re.finditer("花", vis):
        if vis[m.end(): m.end() + 2] not in ("时间", "钱", "费"):
            fail("words", f"{PAGES[k]}: uses 花 as something other than spending time or money")
    for pat, what in NOT_CLAIMED:
        # the sign-up form asks what people use today: tools and assistants named there are questions, not claims
        scan = re.sub(r"<form.*?</form>", " ", page, flags=re.S)
        scan = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", scan[scan.index("<body"):], flags=re.S)))
        for m in re.finditer(pat, scan):
            ctx = scan[max(0, m.start() - 12): m.end() + 12].replace("\n", " ")
            # “不收费 / free” and “not … yet” lines are the honest side of the claim
            if pat.startswith("付费") and (scan[max(0, m.start() - 1): m.start()] == "不" or "free" in ctx):
                continue
            fail("words", f"{PAGES[k]}: mentions {what}: …{ctx}…")
    scan_nf = re.sub(r"<form.*?</form>", " ", page, flags=re.S)
    scan_nf = re.sub(r"<script.*?</script>|<style.*?</style>", " ", scan_nf[scan_nf.index("<body"):], flags=re.S)
    for name in ("Claude", "ChatGPT", "Gemini"):
        if name in scan_nf:
            fail("words", f"{PAGES[k]}: names {name} outside the sign-up question (not verified as connected)")
    if "阅尽千芳" in page:
        fail("words", f"{PAGES[k]}: still carries the tagline that uses a flower image")
    # Chrome, Edge and Brave: only as browsers the extension was not tested in (see APPROVED_BROWSER_LINE above)
    for msg in browser_problems(PAGES[k], page, page_units(page)):
        fail("words", f"{PAGES[k]}: {msg}")

# ---------------------------------------------------------------- 3. gold
for k, page in text.items():
    style = re.search(r"<style>(.*?)</style>", page, re.S)
    if not style:
        fail("gold", f"{PAGES[k]}: no style block")
        continue
    css = strip_comments(re.sub(r"/\* tokens:start.*?tokens:end \*/", "", style.group(1), flags=re.S))
    allowed = {".dot.ring-gold", ".state.worth", ".month .n::before"}
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if "--ke-gold" in body:
            sel = " ".join(sel.split())
            if sel not in allowed:
                fail("gold", f"{PAGES[k]}: gold used on “{sel}” (only the verdict and the calendar's gold dot may carry it)")
    for sel in allowed:
        if not any(" ".join(s.split()) == sel for s, b in re.findall(r"([^{}]+)\{([^{}]*)\}", css) if "--ke-gold" in b):
            fail("gold", f"{PAGES[k]}: expected gold on “{sel}”")
    if "--ke-gold-ink" in css and ".state.worth" not in css:
        fail("gold", f"{PAGES[k]}: a gold word that is not the verdict")

# ---------------------------------------------------------------- 4. one button
for k, page in text.items():
    page_nd = re.sub(r"<dialog.*?</dialog>", " ", page, flags=re.S)
    labels = []
    for m in re.finditer(r'<(a|button)\b[^>]*class="[^"]*\bbtn\b[^"]*"[^>]*>(.*?)</\1>', page_nd, re.S):
        labels.append(" ".join(re.sub(r"<[^>]+>", "", m.group(2)).split()))
    if len(set(labels)) != 1 or len(labels) < 2:
        fail("one button", f"{PAGES[k]}: the main button should be one label, shown at the top and at the end; found {labels}")
    if re.search(r'class="[^"]*\bbtn\b[^"]*"[^>]*>[^<]*</a>', page_nd) is None:
        fail("one button", f"{PAGES[k]}: no link button at the top")

# ---------------------------------------------------------------- 5. examples
for k, page in text.items():
    n_cards = len(re.findall(r'<div class="sample"', page))
    n_tags = len(re.findall(r'<span class="tag">(?:示例|Example)</span>', page))
    if n_cards != 3 or n_tags != 3:
        fail("examples", f"{PAGES[k]}: expected 3 example cards each with the badge, found {n_cards} cards and {n_tags} badges")
    for m in re.finditer(r'<div class="sample"([^>]*)>(?!\s*<span class="tag">)', page):
        fail("examples", f"{PAGES[k]}: an example card whose first child is not the badge")

# ---------------------------------------------------------------- 6. parity
# Sources the English form offers and the Chinese form does not (they were the English page's own before it was built
# from the Chinese one; the Worker accepts them). They are the one allowed difference between the forms.
EN_ONLY_SOURCES = ["substack", "linkedin", "medium"]
ONLY_EN_LABEL = re.compile(r'[ \t]*<label class="popt"><input type="checkbox" name="content_sources" value="(?:%s)">[^<]*</label>\n' % "|".join(EN_ONLY_SOURCES))


def skeleton(page):
    page = ONLY_EN_LABEL.sub("", page)
    body = page[page.index("<body"):]
    body = re.sub(r"<script.*?</script>", "<script/>", body, flags=re.S)
    out = []
    for m in re.finditer(r"<(/?[a-zA-Z0-9]+)([^>]*)>", body):
        cls = re.search(r'class="([^"]*)"', m.group(2))
        ident = re.search(r'\bid="([^"]*)"', m.group(2))
        out.append(f"{m.group(1)}.{cls.group(1) if cls else ''}#{ident.group(1) if ident else ''}")
    return out

if skeleton(text["zh"]) != skeleton(text["en"]):
    a, b = skeleton(text["zh"]), skeleton(text["en"])
    i = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    fail("parity", f"the two pages differ in structure at element {i}: zh {a[i] if i < len(a) else None} / en {b[i] if i < len(b) else None}")
r = subprocess.run([sys.executable, ".build/make_en.py", "--check"], capture_output=True, text=True)
if r.returncode != 0:
    fail("parity", (r.stdout + r.stderr).strip().splitlines()[0] if (r.stdout + r.stderr).strip() else "make_en.py --check failed")

# ---------------------------------------------------------------- 6b. form
def inputs(page):
    out = []
    for m in re.finditer(r"<input\b([^>]*)>", page):
        attrs = dict(re.findall(r'\b([a-z-]+)="([^"]*)"', m.group(1)))
        if attrs.get("name"):
            out.append((attrs["name"], attrs.get("type", ""), attrs.get("value", ""), attrs.get("maxlength", "")))
    return out


worker = open("worker.js", encoding="utf-8").read()


def worker_list(const):
    m = re.search(r"const %s = \[(.*?)\];" % const, worker, re.S)
    return re.findall(r'"([^"]+)"', m.group(1)) if m else []


# form field -> the Worker's list of values it accepts
FIELDS = {"current_habit": "STORAGE", "content_sources": "SOURCES", "primary_assistant": "ASSISTANTS"}
forms = {k: inputs(v) for k, v in text.items()}
for field, const in FIELDS.items():
    accepted = worker_list(const)
    if not accepted:
        fail("form", f"worker.js has no {const} list (this check reads it)")
        continue
    offered = {k: {v for n, _t, v, _m in forms[k] if n == field} for k in forms}
    lost = [v for v in accepted if v not in offered["en"]]
    if lost:
        fail("form", f"the English form no longer offers {', '.join(lost)} for {field}, which the Worker accepts")
    odd = sorted(offered["zh"] - set(accepted)) + sorted(offered["en"] - set(accepted))
    if odd:
        fail("form", f"{field}: a value the Worker does not accept is offered: {', '.join(sorted(set(odd)))}")
# the forms differ in the English-only sources and nowhere else
zh_rest = [i for i in forms["zh"]]
en_rest = [i for i in forms["en"] if not (i[0] == "content_sources" and i[2] in EN_ONLY_SOURCES)]
if zh_rest != en_rest:
    fail("form", "the Chinese and English forms differ in more than the English-only sources (the fields, their order, their values or limits)")
if sorted(i[2] for i in forms["en"] if i[0] == "content_sources" and i[2] in EN_ONLY_SOURCES) != sorted(EN_ONLY_SOURCES):
    fail("form", f"the English form is missing one of {', '.join(EN_ONLY_SOURCES)}")
for k, page in text.items():
    if k == "zh":
        continue
    rule = re.search(r"\.nb\s*\{([^}]*)\}", page)
    if rule and "nowrap" in rule.group(1):
        fail("form", "the English `.nb` rule is `nowrap`: \"Keep only the essence.\" is 345px and the page scrolls sideways under 375px")

# ---------------------------------------------------------------- 7. links
for k, page in text.items():
    ids = set(re.findall(r'\bid="([^"]+)"', page))
    for target in re.findall(r'href="#([^"]+)"', page):
        if target not in ids:
            fail("links", f"{PAGES[k]}: #{target} has no target")
    base = os.path.dirname(PAGES[k])
    for ref in set(re.findall(r'(?:src|href|srcset)="((?:\.\./)?assets/[^"]+)"', page)):
        if not os.path.exists(os.path.normpath(os.path.join(base, ref))):
            fail("links", f"{PAGES[k]}: {ref} does not exist")

# ---------------------------------------------------------------- 8. llms.txt and the share image
llms = open("llms.txt", encoding="utf-8").read()
for pat, what in NOT_CLAIMED + [(r"200 items|v1\.0", "a quota or a roadmap (not announced)")]:
    for m in re.finditer(pat, llms):
        ctx = llms[max(0, m.start() - 12): m.end() + 12].replace("\n", " ")
        fail("llms.txt", f"mentions {what}: …{ctx}…")
for name in ("Claude", "ChatGPT", "Gemini", "Readwise", "Raindrop", "Instapaper", "Burn 451"):
    if name in llms:
        fail("llms.txt", f"names {name} (not verified as connected; no comparisons)")
if "阅尽千芳" in llms:
    fail("llms.txt", "carries the tagline that uses a flower image")
for msg in browser_problems("llms.txt", llms, [llms]):
    fail("llms.txt", msg)

# The share image the pages name is the one that is served. A draft is never served, and no page names it.
OLD_SHARE_IMAGE_SHA256 = "44b75cca2a9be8b90cb8a32fbe21c559ca1fb48f29604a3de5b5274d3c178091"  # "Save freely. Keep the essence. · 阅尽千芳，只留精华" in the picture
if ".build" not in open(".assetsignore", encoding="utf-8").read().split():
    fail("share image", ".build is not in .assetsignore: the draft image under it would be served")
for root, _dirs, files in os.walk("."):
    if root.startswith(("./.git", "./.build", "./node_modules")):
        continue
    for name in files:
        if "DRAFT" in name.upper():
            fail("share image", f"{os.path.join(root, name)}: a draft outside .build is served")
for k, page in text.items():
    if "DRAFT" in page:
        fail("share image", f"{PAGES[k]}: names a draft file")
share = "assets/keepessence-og-1200x630.png"
if os.path.exists(share) and hashlib.sha256(open(share, "rb").read()).hexdigest() == OLD_SHARE_IMAGE_SHA256:
    note = f"{share} is still the old share image (the old tagline is in the picture): replace it with the approved one before publishing"
    if "--release" in sys.argv:
        fail("release", note)
    else:
        print("note:", note)

if fails:
    print("\n".join(fails))
    print(f"\n{len(fails)} problem(s)")
    sys.exit(1)
print("ok: tokens, words, gold, one button, examples, parity, form, links, llms.txt, share image")
