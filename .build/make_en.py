"""Build index.html (English) from zh/index.html: same structure, styles and script, English copy.

Run from the site root:  python3 .build/make_en.py           (writes index.html)
                         python3 .build/make_en.py --check   (fails when index.html was edited by hand)
Every Chinese string of the page is replaced by the English in R below, in order. The script stops
with a list when a string of R is not found in the Chinese page (the page changed and this list did
not) or when Chinese text is left over in the English page (a string that has no English yet).
The English product name is "Keep Essence"; the English words of the product (analysis, key fact,
key points, verdict, daily digest, deep dive, notes) are the ones in the app (web/src/i18n/en.ts)."""
import re
import sys

zh = open('zh/index.html', encoding='utf-8').read()
t = zh

# ---------- the page's own head and address ----------
T_ZH = "精华 KeepEssence｜先帮我看清，再由我决定"
T_EN = "Keep Essence | Help me see clearly first, then I decide"
D_ZH = "存得下很多，只留精华。你存进来的文章，助手先读一遍，告诉你它讲了什么、值不值得花时间；留不留、深不深挖，由你决定。内测中，只对受邀邮箱开放。"
D_EN = ("Save a lot, keep only the essence. An assistant reads what you save first and tells you what it says and whether it is "
        "worth your time; whether to keep it or dig deeper is up to you. In beta, open only to invited emails.")
D2_ZH = "你存进来的文章，助手先读一遍，告诉你它讲了什么、值不值得花时间；留不留、深不深挖，由你决定。内测中，只对受邀邮箱开放。"
D2_EN = ("An assistant reads what you save first and tells you what it says and whether it is worth your time; whether to keep it "
         "or dig deeper is up to you. In beta, open only to invited emails.")

R = [
 # <head>
 ('<html lang="zh-Hans">', '<html lang="en">'),
 (f'<title>{T_ZH}</title>', f'<title>{T_EN}</title>'),
 (f'<meta property="og:title" content="{T_ZH}">', f'<meta property="og:title" content="{T_EN}">'),
 (f'<meta name="twitter:title" content="{T_ZH}">', f'<meta name="twitter:title" content="{T_EN}">'),
 (f'<meta name="description" content="{D_ZH}">', f'<meta name="description" content="{D_EN}">'),
 (f'<meta property="og:description" content="{D_ZH}">', f'<meta property="og:description" content="{D_EN}">'),
 (f'<meta name="twitter:description" content="{D_ZH}">', f'<meta name="twitter:description" content="{D_EN}">'),
 ('<link rel="canonical" href="https://www.keepessence.app/zh/">', '<link rel="canonical" href="https://www.keepessence.app/">'),
 ('<meta property="og:url" content="https://www.keepessence.app/zh/">', '<meta property="og:url" content="https://www.keepessence.app/">'),
 ('<meta property="og:locale" content="zh_CN">\n  <meta property="og:locale:alternate" content="en_US">', '<meta property="og:locale" content="en_US">\n  <meta property="og:locale:alternate" content="zh_CN">'),
 (f'"description": "{D2_ZH}"', f'"description": "{D2_EN}"'),
 # <body>: header, notice, footer
 ('<div class="notice" role="note">内测中，只对受邀邮箱开放</div>', '<div class="notice" role="note">In beta. Open only to invited emails.</div>'),
 ('<a class="brand" href="/zh/" aria-label="精华">', '<a class="brand" href="/" aria-label="Keep Essence">'),
 ('<span>精华</span>', '<span>Keep Essence</span>'),
 ('<a class="lang" href="/" hreflang="en" lang="en">EN</a>', '<a class="lang" href="/zh/" hreflang="zh-Hans" lang="zh-Hans">中文</a>'),
 ('<a href="/" hreflang="en" lang="en">EN</a>', '<a href="/zh/" hreflang="zh-Hans" lang="zh-Hans">中文</a>'),
 ('<span><strong>精华</strong> · 存得下很多，只留精华</span>', '<span><strong>Keep Essence</strong> · Save a lot, keep only the essence</span>'),
 # hero
 ('<h1>存得下很多，<span class="nb">只留<strong>精华</strong>。</span></h1>', '<h1>Save a lot. <span class="nb">Keep only the <strong>essence</strong>.</span></h1>'),
 ('<p class="claim">先帮我看清，再由我决定。</p>', '<p class="claim">Help me see clearly first, then I decide.</p>'),
 ('你随手存进来的文章，助手先读一遍，告诉你它讲了什么、值不值得花时间。留不留，你说了算。',
  'An assistant reads what you save first and tells you what it says and whether it is worth your time. Whether to keep it is up to you.'),
 ('<a class="btn" href="#join">申请内测</a>', '<a class="btn" href="#join">Join the beta</a>'),
 ('存了几百条，一条都没回头看？不是你懒，是没人先帮你看一眼。', 'Hundreds saved and not one opened again? You are not lazy. Nobody took a first look for you.'),
 # how it works
 ('<h2>怎么用</h2>', '<h2>How it works</h2>'),
 ('<strong>存入</strong>在网页上粘贴链接、文字或图片；电脑上装了浏览器扩展的，点一下就存。',
  '<strong>Save</strong>Paste a link, text or an image on the web; with the browser extension on a computer, one click saves.'),
 ('<strong>看清</strong>几分钟内，助手给出四项解读：内容概述、关键事实、最多三条要点，和一个判定。',
  '<strong>See</strong>Within a few minutes the assistant writes four lines: a summary, a key fact, up to three key points, and a verdict.'),
 ('<strong>你决定</strong>值得的，点「深挖」；不感兴趣的，标「不感兴趣」。每晚的每日摘要帮你收个尾。',
  '<strong>You decide</strong>Worth it: tap “Deep dive”. Not for you: mark “Not interested”. The daily digest wraps up each night.'),
 ('aria-label="示例：一条解读"', 'aria-label="Example: one analysis"'),
 ('<span class="tag">示例</span>', '<span class="tag">Example</span>'),
 ('<h3>任务队列里，怎么让一份活只归一个人</h3>', '<h3>In a task queue, how to make a piece of work belong to one person</h3>'),
 ('<dt>内容概述</dt><dd>用「租约」让一份任务同一时间只归一个人做，过期自动放回队列。</dd>',
  '<dt>Summary</dt><dd>A “lease” lets a task belong to one person at a time, and it goes back to the queue when the lease runs out.</dd>'),
 ('<dt>关键事实</dt><dd>文章 · 约 3200 字。</dd>', '<dt>Key fact</dt><dd>Article · about 3,200 words.</dd>'),
 ('<dt>要点</dt>', '<dt>Key points</dt>'),
 ('<li>认领要带期限，过期自动放回。</li>', '<li>Claiming comes with a time limit; when it runs out the task goes back.</li>'),
 ('<li>交回要能重放，同一份交两遍只留一份。</li>', '<li>A hand-in can be replayed: handing in the same piece twice keeps only one.</li>'),
 ('<li>续期只能由持有者做。</li>', '<li>Only the holder can renew.</li>'),
 ('<dt>判定</dt>', '<dt>Verdict</dt>'),
 ('</i>值得深挖</span>', '</i>Worth a deep dive</span>'),
 # daily digest
 ('<h2>每日摘要</h2>', '<h2>Daily digest</h2>'),
 ('每晚 21:00 之后，把今天存的东西整理成一页：值得深挖的、其余的，再加一个睡前问题。看完点「读了，晚安」。',
  'After 9 PM every night, what you saved today becomes one page: what is worth a deep dive, the rest, and a question to sleep on. When you have read it, tap “Read. Good night”.'),
 ('aria-label="示例：一份每日摘要"', 'aria-label="Example: one daily digest"'),
 ('<h3>这份每日摘要里有 6 条。2 条值得深挖的还没处理。</h3>', '<h3>6 in this daily digest. 2 worth a deep dive not dealt with yet.</h3>'),
 ('<b>总结</b>今天存的多是任务队列和代码评审的文章，其中两条值得细读。',
  '<b>Summary</b>Most of what you saved today is about task queues and code review; two of them deserve a close read.'),
 ('<b>值得深挖的</b>任务队列里，怎么让一份活只归一个人<br>把评审意见写成可以执行的句子',
  '<b>Worth a deep dive</b>In a task queue, how to make a piece of work belong to one person<br>Writing review comments as sentences someone can act on'),
 ('<b>其余的 · 4 条</b>另外 4 条了解一下就够，已收在这一份里。', '<b>The rest · 4 items</b>The other 4 are fine to just know about, and are already in this one.'),
 ('<b>睡前一问</b>今天存的两条值得深挖的，哪一条会改变你明天的做法？',
  '<b>A question to sleep on</b>Of the two worth a deep dive that you saved today, which one will change what you do tomorrow?'),
 ('<p class="bye">读了，晚安</p>', '<p class="bye">Read. Good night</p>'),
 # deep dive and notes
 ('<h2>深挖与笔记</h2>', '<h2>Deep dive and notes</h2>'),
 ('挑出值得的那一条，和助手聊透，存成你自己的笔记。笔记可以快速查找，也可以下载成 Markdown。留下笔记的那天，月历上会亮一个金点。',
  'Pick the one that is worth it, talk it through with an assistant, and keep it as your own note. Notes have a quick find and can be downloaded as Markdown. On a day you keep a note, the calendar shows a gold dot.'),
 ('aria-label="示例：一个月的月历"', 'aria-label="Example: one month of the calendar"'),
 ('<h3>月历</h3>', '<h3>Calendar</h3>'),
 ('<p class="cap">一天一个圆点。金点：那天留下了笔记。</p>', '<p class="cap">One dot a day. Gold dot: a note was kept that day.</p>'),
 # assistants
 ('<h2>接上你自己的助手</h2>', '<h2>Connect your own assistant</h2>'),
 ('一个 MCP 地址，就能接入你自己用的、支持 MCP 的助手。没有自己的助手也没关系，内置助手会出解读和每日摘要，内测期间不收费。',
  'One MCP address connects the assistant you already use, if it supports MCP. No assistant of your own? No problem: the built-in assistant writes the analyses and the daily digest, and it is free during the beta.'),
 # what works
 ('<h2>现在能用什么</h2>', '<h2>What works today</h2>'),
 ('<h3>可以</h3>', '<h3>Yes</h3>'),
 ('<h3>还没有</h3>', '<h3>Not yet</h3>'),
 ('<li>网页：电脑和手机的浏览器都能打开</li>', '<li>The web app: it opens in the browser on a computer and on a phone</li>'),
 ('<li>浏览器扩展：Chromium 内核的浏览器，需手动安装，还没上架商店，安装步骤随邀请发</li>',
  '<li>Browser extension: Chromium-based browsers, installed by hand, not in any store yet; the steps come with your invitation</li>'),
 ('<li>内置助手出解读和每日摘要</li>', '<li>The built-in assistant writes the analyses and the daily digest</li>'),
 ('<li>笔记</li>', '<li>Notes</li>'),
 ('<li>用 MCP 接入你自己的助手</li>', '<li>Connect your own assistant over MCP</li>'),
 ('<li>iPhone App 暂不开放安装</li>', '<li>The iPhone app is not open for installation</li>'),
 ('<li>浏览器扩展在 Chrome、Edge、Brave 里还没有逐个试过，目前只在 Chromium 里测过</li>',
  '<li>The extension has not been tried in Chrome, Edge and Brave one by one; so far it was tested only in Chromium</li>'),
 ('有些网页的正文读不到，比如要登录或要验证的页面。这时会如实显示「没取到内容」，并附上原文链接。',
  'Some pages cannot be read, for example pages that ask you to sign in or to verify. Then it says so, “Content could not be fetched”, and links the original.'),
 ('不用 Cookie。数据怎么保留、保留多久，以正式的隐私说明为准（正在定稿）。',
  'No cookies. How data is kept, and for how long, follows the formal privacy statement (being finalised).'),
 # sign-up
 ('<h2>存得再多，也只留精华。</h2>', '<h2>Save as much as you like. Keep only the essence.</h2>'),
 ('分批邀请。优先邀请两类人：用收藏或稍后读工具好几年的，和自己有 AI 助手、平时就用它处理知识的。',
  'Invitations go out in batches. First in line: people who have used bookmarking or read-it-later tools for years, and people who have an AI assistant and already use it to work with knowledge.'),
 ('<label class="wlbl" for="wl-email">邮箱</label>', '<label class="wlbl" for="wl-email">Email</label>'),
 ('你存的东西，现在都堆在哪儿？', 'Where does everything you save pile up now?'),
 ('你一般从哪里收集内容？', 'Where do you usually find things to save?'),
 ('<span class="opt">（可多选）</span>', '<span class="opt">(pick any)</span>'),
 ('>浏览器标签页</label>', '>Browser tabs</label>'),
 ('>微信文件传输助手</label>', '>WeChat File Transfer</label>'),
 ('>其他</label>', '>Other</label>'),
 ('placeholder="还有哪里？"', 'placeholder="Where else?"'),
 ('aria-label="其他存放的地方"', 'aria-label="Another place you keep things"'),
 ('aria-label="其他内容来源"', 'aria-label="Another source"'),
 ('>微信公众号</label>', '>WeChat Official Accounts</label>'),
 ('>小红书</label>', '>Xiaohongshu</label>'),
 ('>知乎</label>', '>Zhihu</label>'),
 ('>B 站</label>', '>Bilibili</label>'),
 ('>即刻</label>', '>Jike</label>'),
 ('>微博</label>', '>Weibo</label>'),
 ('>邮件订阅</label>', '>Email newsletters</label>'),
 ('>播客</label>', '>Podcasts</label>'),
 ('你最常用哪个 AI 助手？', 'Which AI assistant do you use most?'),
 ('>自托管 Agent</label>', '>Self-hosted agent</label>'),
 ('>暂时没有</label>', '>None yet</label>'),
 ('你更想用哪种方式？', 'How would you rather use it?'),
 ('>通过 MCP 接入我自己的助手</label>', '>Connect my own assistant over MCP</label>'),
 ('>内测阶段用系统自带的 Agent</label>', '>Use the built-in agent during the beta</label>'),
 ('现在用的收藏工具，最让你头疼的是什么？', 'What annoys you most about the tool you use now?'),
 ('<span class="opt">（选填）</span>', '<span class="opt">(optional)</span>'),
 ('placeholder="一句话就好。"', 'placeholder="One sentence is enough."'),
 ('<button class="btn" type="submit">申请内测</button>', '<button class="btn" type="submit">Join the beta</button>'),
 ('<p class="wdone-title" id="wdone-title" data-done-title>报名成功</p>', '<p class="wdone-title" id="wdone-title" data-done-title>You are signed up</p>'),
 ('data-done-close>好的</button>', 'data-done-close>OK</button>'),
 # script
 ('lang: "zh-Hans",', 'lang: "en",'),
 ('sub.textContent = "申请内测 · 马上开放";', 'sub.textContent = "Join the beta · opening soon";'),
 ('show("稍等，内测名单马上就来。开放后回到这里就能申请。")', 'show("Hold on, the beta list is about to open. Come back here once it does.")'),
 ('show("请输入有效的电子邮箱地址。", true)', 'show("Please enter a valid email address.", true)'),
 ('sub.textContent = "提交中…";', 'sub.textContent = "Sending…";'),
 ('show(again ? "这个邮箱已在内测名单里，我们会按批次邮件通知。" : "已加入内测名单。开放名额时我们会通过邮件联系你。");',
  'show(again ? "This email is already on the beta list. We will write to you as each batch opens." : "You are on the beta list. We will email you when places open.");'),
 ('confirmDone("你已经在名单里了", `${email} 之前报过名，不用重复提交。开放名额时我们会发邮件通知你。`)',
  'confirmDone("You are already on the list", `${email} signed up before, so there is no need to send it again. We will email you when places open.`)'),
 ('confirmDone("报名成功", `${email} 已加入内测名单。开放名额时我们会发邮件通知你。`)',
  'confirmDone("You are signed up", `${email} is on the beta list. We will email you when places open.`)'),
 ('show("提交过于频繁，请一分钟后再试。", true)', 'show("Too many tries. Please wait a minute and try again.", true)'),
 ('show("暂时无法连接到等待列表服务，请稍后再试。", true)', 'show("Cannot reach the sign-up service for now. Please try again later.", true)'),
 # other
 ('// Each 其他 checkbox reveals', '// Each “Other” checkbox reveals'),
 ('"alternateName": "精华"', '"alternateName": "精华"'),
]

missing = []
for zh_s, en_s in R:
    if zh_s not in t:
        missing.append(zh_s)
        continue
    t = t.replace(zh_s, en_s)
if missing:
    print("Not found in zh/index.html (the page changed, or the string is written twice with different markup):")
    for m in missing:
        print("  -", m[:100])
    sys.exit(1)

# the page links its files one level up from zh/
t = t.replace('../assets/', 'assets/')

# ---------- what is still Chinese ----------
# allowed: the name 精华 as the organisation's alternate name, and the 中文 link to the Chinese page.
left = []
for n, line in enumerate(t.split('\n'), 1):
    s = line.replace('"alternateName": "精华"', '').replace('>中文</a>', '>').replace('lang="zh-Hans"', '')
    if re.search(r'[㐀-鿿＀-￯　-〿]', s):
        left.append((n, line.strip()[:110]))
if left:
    print("Chinese text left in the English page (add the English to R):")
    for n, l in left:
        print(f"  line {n}: {l}")
    sys.exit(1)

if '--check' in sys.argv:
    # Does the English page on disk equal what this script makes? (Nobody edited it by hand.)
    if open('index.html', encoding='utf-8').read() != t:
        print("index.html is not what .build/make_en.py makes from zh/index.html: run  python3 .build/make_en.py")
        sys.exit(1)
    print("index.html is what make_en.py makes")
else:
    open('index.html', 'w', encoding='utf-8').write(t)
    print(f"index.html written ({len(R)} strings replaced)")
