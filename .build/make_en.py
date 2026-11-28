"""Build index.html (English) from zh/index.html: same structure, styles and scripts, English copy.

Run from the site root:  python3 .build/make_en.py
It reports any Chinese text left over. The English <head> (title, meta, structured data) starts
from .build/head.en.html and is adjusted below; the body is the Chinese page with every string
replaced by the English in R."""
import re, json, sys

zh = open('zh/index.html', encoding='utf-8').read()
head_en = open('.build/head.en.html', encoding='utf-8').read()

# ---------- head: keep the English page's own head (title, meta, structured data) ----------
body = zh[zh.index('<style>'):]
t = head_en + body

EN_TITLE = "Keep Essence — AI Read-It-Later That Keeps Only the Essence"
EN_DESC = "Hundreds of links saved, none opened again? Keep Essence turns each save into a four-line AI brief, clears the unread after 30 days, and keeps only your notes."
HEAD = [
 ('<title>Keep Essence — Save Freely. Keep the Essence.</title>', f'<title>{EN_TITLE}</title>'),
 ('<meta property="og:title" content="Keep Essence — Save Freely. Keep the Essence.">', f'<meta property="og:title" content="{EN_TITLE}">'),
 ('<meta name="twitter:title" content="Keep Essence — Save Freely. Keep the Essence.">', f'<meta name="twitter:title" content="{EN_TITLE}">'),
 ('"description": "An anti-hoarding, AI-filtered reading inbox that connects to Claude, ChatGPT, Gemini, and self-hosted agents over remote MCP and OAuth. Every captured item is distilled into a 4-line brief and a 9 PM Daily Digest, raw links expire quietly after 30 days, and only what you deep-dive becomes a permanent Note."',
  '"description": "An AI read-it-later filter. Every saved item becomes a four-line brief and joins a 9 PM Daily Digest; unread items clear after 30 days; connect Claude, ChatGPT, Gemini or your own agent over MCP to deep-dive, and only what you work through is kept as a permanent note."'),
 ('"name": "Core & Bring Your Own Assistant (MCP + OAuth)"', '"name": "Free: core product and your own assistant"'),
 ('"description": "Free core platform, built-in routing assistant (up to 200 items/day), and Bring Your Own Assistants over MCP + OAuth."', '"description": "The core product, plus connecting your own AI assistant over MCP or running your own agent, is free."'),
 ('"name": "Hosted Autonomous Assistants (Post-v1.0)"', '"name": "Paid: built-in assistant"'),
 ('"description": "Optional paid tier planned post-v1.0 for zero-setup hosted automated briefs, nightly digests, and close reads."', '"description": "For people who would rather not connect an assistant: the built-in assistant writes the four-line briefs and the Daily Digest. Free during the beta, paid afterwards."'),
 ('"operatingSystem": "Web, iOS"', '"operatingSystem": "Web, iOS, macOS"'),
]
for a, b in HEAD:
    assert t.count(a) == 1, a[:60]
    t = t.replace(a, b)
for pat in [r'(<meta name="description" content=")[^"]*(">)', r'(<meta property="og:description" content=")[^"]*(">)', r'(<meta name="twitter:description" content=")[^"]*(">)']:
    t = re.sub(pat, lambda m: m.group(1) + EN_DESC + m.group(2), t, count=1)

FAQ = [
 ("Everything expires after 30 days. Will it clear out something I wanted?",
  "No. Tap Keep on anything you want and it never expires. Anything in your deep-dive queue is protected too. The notes you keep are permanent and quick to find."),
 ("I don't have an AI assistant and I've never used MCP. Can I still use it?",
  "Yes. During the beta you can use the built-in agent and connect nothing yourself. If you later want your own Claude, ChatGPT or Gemini, you paste one address into its settings and tap Allow."),
 ("Is it free now? Will it cost money later?",
  "It's free now. The core product and connecting your own assistant stay free. Only one thing will be paid later: using the built-in assistant instead of connecting your own. Your notes and digests can be exported at any time — nothing is locked in."),
 ("Who can see what I save?",
  "Only you, and the assistants you explicitly allow. When you connect an assistant, a confirmation page says exactly what will be sent to it. Permissions are separate for each assistant and each device, and you can revoke any of them in one tap under Assistant settings. A shared monthly grid shows dots only — never any content."),
 ("Which devices does it work on?",
  "Saving: iPhone Shortcut, the phone share sheet, the browser extension, the Mac menu bar and the web. Reading: the phone app (opening with the beta) and the web."),
]

R = [
 # nav / header
 ('<a class="brand" href="/zh/" aria-label="精华 首页">', '<a class="brand" href="/" aria-label="Keep Essence Home">'),
 ('<span>精华</span>\n      </a>', '<span>Keep Essence</span>\n      </a>'),
 ('aria-label="主导航"', 'aria-label="Main"'),
 ('<a href="#screens">用法</a>', '<a href="#screens">How it works</a>'),
 ('<a href="#why">理念</a>', '<a href="#why">Why</a>'),
 ('<a href="#mcp">助手</a>', '<a href="#mcp">Assistants</a>'),
 ('<a href="#dig">深挖</a>', '<a href="#dig">Deep dive</a>'),
 ('<a href="#faq">问答</a>', '<a href="#faq">FAQ</a>'),
 ('<a class="lang" href="/" hreflang="en" lang="en">EN</a>', '<a class="lang" href="/zh/" hreflang="zh-Hans" lang="zh-Hans">中文</a>'),
 ('<a href="/" hreflang="en" lang="en">EN</a>', '<a href="/zh/" hreflang="zh-Hans" lang="zh-Hans">中文</a>'),
 ('href="#join">申请内测</a>', 'href="#join">Join the beta</a>'),
 # hero
 ('<h1>阅尽千芳，<br>只留<span class="gold">精华</span>。</h1>', '<h1>Save freely.<br>Keep the <span class="gold">essence</span>.</h1>'),
 ('<p class="hero-ans">专治「存了几百条，一条都没再打开」。</p>', '<p class="hero-ans">Built for people with hundreds saved and not one opened again.</p>'),
 ('你爱学习，爱收藏，然后就没有然后了。', 'You love learning. You love saving. And then… nothing.'),
 ('<span class="gold">精华</span>按你的规则先筛一遍，再接上 AI 助手，陪你把值得的那几条聊透。', '<span class="gold">Keep Essence</span> filters everything by your rules first, then brings in your AI assistant to work through the few that matter.'),
 ('<mark class="hl">收藏的，真正变成你自己的。</mark>', '<mark class="hl">What you save finally becomes yours.</mark>'),
 ('href="#join">申请首批内测</a>', 'href="#join">Join the first beta</a>'),
 ('href="#screens">先看怎么用</a>', 'href="#screens">See how it works</a>'),
 ('系统自带助手，也可接入你自己的 Claude、ChatGPT、Gemini，帮你整理、深挖。', 'A built-in assistant comes with it, or connect your own Claude, ChatGPT or Gemini to sort and dig deeper.'),
 ('aria-label="初步解读演示"', 'aria-label="Quick brief demo"'),
 ('看精华怎么帮你筛 · 也可以自己点一条', 'Watch it filter · or pick one yourself'),
 ('aria-label="示例条目"', 'aria-label="Sample items"'),
 ('\n              长文\n', '\n              Long read\n'),
 ('\n              代码仓库\n', '\n              Code repo\n'),
 ('\n              社交爆帖\n', '\n              Viral post\n'),
 ('\n              即时新闻\n', '\n              Breaking news\n'),
 ('\n              初步解读\n', '\n              Quick brief\n'),
 ('<span data-b-src>微信公众号 · 14 分钟前暂存</span>', '<span data-b-src>Substack · saved 14 min ago</span>'),
 ('<span data-b-life>剩余 29 天</span>', '<span data-b-life>29 days left</span>'),
 ('data-b-title>AI 时代，普通人还能靠什么吃饭</p>', 'data-b-title>AI and the future of your job</p>'),
 ('<span class="b-k">是什么</span>', '<span class="b-k">What</span>'),
 ('<strong data-b-what>一篇 8000 字长文，讲哪些工作最先被 AI 改写。</strong>', '<strong data-b-what>A 5,000-word essay on which jobs AI rewrites first.</strong>'),
 ('<span class="b-k">事实</span>', '<span class="b-k">Facts</span>'),
 ('data-b-facts>约 20 分钟阅读 · 引用 3 份行业报告</p>', 'data-b-facts>About 20 min read · cites 3 industry reports</p>'),
 ('<span class="b-k">要点</span>', '<span class="b-k">Takeaway</span>'),
 ('data-b-key>被替代的不是整个岗位，是岗位里重复的那部分。</p>', 'data-b-key>It isn’t whole jobs that get replaced — it’s the repetitive part of each job.</p>'),
 ('<span class="b-k">判断</span>', '<span class="b-k">Verdict</span>'),
 ('data-act="deepdive">深挖</button>', 'data-act="deepdive">Deep dive</button>'),
 ('data-act="dismiss">不感兴趣</button>', 'data-act="dismiss">Not interested</button>'),
 ('data-act="seen">看过了</button>', 'data-act="seen">Seen it</button>'),
 ('data-act="keep">收藏</button>', 'data-act="keep">Keep</button>'),
 ('aria-label="和助手深挖的对话示例"', 'aria-label="Sample deep-dive chat with an assistant"'),
 ('<span>你的 AI 助手 · 深挖中</span>', '<span>Your AI assistant · deep dive</span>'),
 ('data-chat-back>← 回到解读</button>', 'data-chat-back>← Back to brief</button>'),
 # stats
 ('<b>30 天</b><span><i>没看的自动清走，</i><i>不再越堆越多</i></span>', '<b>30 days</b><span><i>Unread items clear themselves,</i> <i>so the pile stops growing</i></span>'),
 ('<b>4 行</b><span><i>10 秒看懂一条，</i><i>值不值得读</i></span>', '<b>4 lines</b><span><i>Ten seconds to know</i> <i>if it’s worth your time</i></span>'),
 ('<b>21:00</b><span><i>每晚一份摘要，</i><i>静下心来消化</i></span>', '<b>9 PM</b><span><i>One digest each evening,</i> <i>to take in calmly</i></span>'),
 ('<b>1 步</b><span><i>通过 MCP</i> <i>集成你的 AI 助手</i></span>', '<b>1 step</b><span><i>Connect your AI assistant</i> <i>over MCP</i></span>'),
 # pains
 ('<div class="eyebrow">你是不是也这样</div>', '<div class="eyebrow">Sound familiar?</div>'),
 ('<h2>存了不读，不是你的错。</h2>', '<h2>Saving without reading isn’t your fault.</h2>'),
 ('存很容易，难的是筛和看。别的工具只管帮你存，剩下的全留给你自己。', 'Saving is easy. Sorting and reading are the hard part. Other tools only help you save, and leave the rest to you.'),
 ('<strong>越存越多，越多越不想看</strong>', '<strong>The more you save, the less you want to look</strong>'),
 ('几百条没读的堆在那儿，一打开就心虚，干脆不开了。', 'Hundreds of unread items sit there. Opening the app feels like guilt, so you stop opening it.'),
 ('<strong>30 天自动清走</strong>', '<strong>Cleared after 30 days</strong>'),
 ('没空看的到期就消失，没有红点，也不欠账。', 'Anything you never get to simply expires. No red badges, nothing owed.'),
 ('<strong>大部分其实不值得看</strong>', '<strong>Most of it isn’t worth reading</strong>'),
 ('标题党、软文、重复的观点一大堆，有用的那几条被埋在里面。', 'Clickbait, sponsored posts and the same take ten times over bury the few useful ones.'),
 ('<strong>先替你读成四行</strong>', '<strong>Read down to four lines first</strong>'),
 ('是什么、事实、要点、判断，一眼看完。以前见过类似的，也会提醒你。', 'What it is, the facts, the takeaway, a verdict — one glance. It also tells you when you’ve seen something like it before.'),
 ('<strong>存得到处都是</strong>', '<strong>Saved all over the place</strong>'),
 ('文章、视频、截图顺手丢进文件传输助手，过两天就找不到了。', 'Articles, videos and screenshots get messaged to yourself, and two days later you can’t find them.'),
 ('<strong>点一下就存进来</strong>', '<strong>One tap to save</strong>'),
 ('点一下就存。不用分类打标签，系统替你挑出要点、分好档：值得深挖、知道就行、可以略过。', 'One tap and it’s in. No folders, no tags. It pulls out the key point and sorts each item for you: worth digging into, good to know, or skip.'),
 ('<strong>存了不等于会了</strong>', '<strong>Saving isn’t learning</strong>'),
 ('划线、囤原文很有安全感，可下个月脑子里什么也没剩。', 'Highlighting and hoarding feel safe, yet a month later none of it is still in your head.'),
 ('<strong>聊透了才留下</strong>', '<strong>Kept only once you’ve worked it through</strong>'),
 ('每天挑一两条，和你的助手聊透，只留下你自己的结论。', 'Pick one or two a day, work them through with your assistant, and keep only your own conclusions.'),
 ('aria-label="来自公开社区的真实读者原话"', 'aria-label="Real quotes from public communities"'),
 ('<blockquote class="qcard" data-src="即刻">\n              「俗称『稍后再也不读』……累计保存了 2446 篇内容，但是我打开率极低啊。」\n              <cite>即刻 · 退订付费稍后读工具的用户公开帖</cite>',
  '<blockquote class="qcard" data-src="Jike">\n              “2,446 saved articles in my paid read-it-later app—and an open rate close to zero.”\n              <cite>Jike · user canceling a paid read-it-later subscription</cite>'),
 ('<cite>Reddit · 用助手预读数百篇长文的开发者</cite>', '<cite>Reddit · developer pre-reading hundreds of articles</cite>'),
 ('「懒得打开别的 App，就顺手发给文件传输助手……就是一换手机数据就没了。」\n              <cite>V2EX · 53 条回复的公开讨论帖</cite>',
  '“Too lazy to switch apps, so I message links to myself—until a phone switch wipes everything.”\n              <cite>V2EX · 53-reply thread on self-DM bookmarking</cite>'),
 ('<cite>Zettelkasten.de · 《The Collector’s Fallacy》，2014</cite>', '<cite>Zettelkasten.de · “The Collector’s Fallacy”, 2014</cite>'),
 # screens
 ('<div class="eyebrow">用户界面</div>', '<div class="eyebrow">The app</div>'),
 ('<h2>暂存、筛选、留下，三步走完。</h2>', '<h2>Save. Filter. Keep. Three steps.</h2>'),
 ('你只做两件事：存进来，挑出值得的。读、筛、汇总，都替你做了。', 'You do two things: save it, and pick what’s worth it. The reading, filtering and summing up are done for you.'),
 ('<strong>今天</strong><span></span>', '<strong>Today</strong><span></span>'),
 ('2 个助手在干活 · 今日暂存 14 条', '2 assistants working · 14 saved today'),
 ('<span>微信公众号 · 11:48</span><span>30 天</span>', '<span>Substack · 11:48</span><span>30 days</span>'),
 ('<p class="ph">AI 时代，普通人还能靠什么吃饭</p>\n                <p>8000 字长文 · 引用 3 份行业报告</p>', '<p class="ph">AI and the future of your job</p>\n                <p>5,000 words · cites 3 industry reports</p>'),
 ('title="点击切换左右滑预览"', 'title="Click to preview swipe right / left"'),
 ('→ 深挖</span>', '→ Deep dive</span>'),
 ('略过 ←</span>', 'Skip ←</span>'),
 ('<p class="ph">副业月入过万的 5 个方法</p>\n                  <p>点此卡片预览右滑 / 左滑手势</p>', '<p class="ph">5 side hustles that pay</p>\n                  <p>Click to preview the swipes</p>'),
 ('<span>微信公众号 · 09:20</span><span>30 天</span>', '<span>Hacker News · 09:20</span><span>30 days</span>'),
 ('<p class="ph">某大厂发布新一代 AI 模型</p>\n                <div', '<p class="ph">Big lab ships its next-gen model</p>\n                <div'),
 ('<span>小红书 · 图文</span><span>7 天</span>', '<span>X · thread</span><span>7 days</span>'),
 ('<p class="ph">炸了！这个 AI 工具一天干完一周的活</p>\n                <p>和你存过的三条重复 · 可以略过</p>', '<p class="ph">This AI tool did my week in a day</p>\n                <p>Repeats three posts you saved · Skip</p>'),
 ('<span>github.com · 刚刚</span><span>30 天</span>', '<span>github.com · just now</span><span>30 days</span>'),
 ('助手正在读，解读马上好', 'Assistant is reading — brief on its way'),
 ('<strong>1. 今天 — 10 秒扫完四行解读</strong>', '<strong>1. Today — a four-line brief</strong>'),
 ('右滑排入深挖队列先精读，左滑标不感兴趣。', 'Swipe right to deep dive, left to drop.'),
 ('<strong>每日摘要</strong>', '<strong>Daily Digest</strong>'),
 ('<span class="dot dot-g" data-unread-dot></span>21:00', '<span class="dot dot-g" data-unread-dot></span>9 PM'),
 ('今天进来 14 条 · 值得深挖 2 条', '14 in today · 2 worth digging into'),
 ('<p class="ph">AI 时代，普通人还能靠什么吃饭</p>\n                  <p>被替代的是重复的那部分，不是整个岗位。</p>', '<p class="ph">AI and the future of your job</p>\n                  <p>The repetitive part gets replaced, not the whole job.</p>'),
 ('<p class="ph">副业月入过万的 5 个方法</p>\n                  <p>五个里有两个适合只有晚上有空的人。</p>', '<p class="ph">5 side hustles that actually pay</p>\n                  <p>Two of the five fit someone with only evenings free.</p>'),
 ('<span class="dig-pill">深挖</span>', '<span class="dig-pill">Deep dive</span>'),
 ('← 左滑不感兴趣 · 右滑排入深挖队列 →', '← left: not interested · right: queue a deep dive →'),
 ('<span>其余的（12 条）</span>', '<span>Everything else (12)</span>'),
 ('<li>炸了！这个 AI 工具… · 可以略过</li>', '<li>This AI tool did my week’s work… · Skip</li>'),
 ('<li>某大厂发布新一代 AI 模型 · 知道就行</li>', '<li>Big lab ships its next-gen model · Good to know</li>'),
 ('<li>另有 10 条将在 30 天后安静清理</li>', '<li>10 more will clear quietly after 30 days</li>'),
 ('>睡前一问</strong>', '>One question before sleep</strong>'),
 ('如果今天的中间记录 30 天后都会消失，哪一条结论真正值得留下？', 'If everything from today is gone in 30 days, which one conclusion is worth keeping?'),
 ('data-read="false">读了，晚安</button>', 'data-read="false">Read, good night</button>'),
 ('<strong>2. 每日摘要 — 安静收尾</strong>', '<strong>2. Daily Digest — a calm close</strong>'),
 ('纯文字、不过期。不点也没红点，不欠待办。', 'Plain text. Skip it and nothing nags you.'),
 ('<strong>笔记与月历</strong><span>永久留存</span>', '<strong>Notes &amp; Grid</strong><span>Kept for good</span>'),
 ('<span>快速查找笔记</span>', '<span>Find a note</span>'),
 ('<b>深挖队列</b> · 副业的 5 个方法</span><span>已精读，等你来聊</span>', '<b>Queue</b> · 5 side hustles</span><span>Ready to discuss</span>'),
 ('<span>先把重复的那部分交出去</span>', '<span>Hand off the repetitive part</span>'),
 ('被 AI 替代的是重复的活，不是整个岗位。</p>', 'AI replaces repetitive work, not jobs.</p>'),
 ('<span>长文 · 署名：Claude</span><span>下载 .md</span>', '<span>Long read · by Claude</span><span>.md</span>'),
 ('<span>MCP 服务上线前，先过重放校验</span>', '<span>Test replays before you ship</span>'),
 ('重放出错不报错，却会悄悄重复执行。</p>', 'A replay bug raises no error.</p>'),
 ('<span>代码仓库 · 署名：Claude</span><span>下载 .md</span>', '<span>Code repo · by Claude</span><span>.md</span>'),
 ('<span>新版便宜一半，写稿前先关联网</span>', '<span>Half price; web off to draft</span>'),
 ('写作功能没变；新版默认联网，会带进杂讯。</p>', 'Web is on by default and adds noise.</p>'),
 ('<span>即时新闻 · 署名：ChatGPT</span><span>下载 .md</span>', '<span>News · by ChatGPT</span><span>.md</span>'),
 ('<span>11 月月历</span><span>可嵌入 SVG</span>', '<span>November</span><span>Embeddable SVG</span>'),
 ('aria-label="月历圆点图：金色实心点表示留下了笔记"', 'aria-label="Monthly grid of dots: a solid gold dot marks a day a note was kept"'),
 ('暂存 118 · 摘要 20 · 金点笔记 6', '118 saved · 20 digests · 6 notes'),
 ('<strong>3. 笔记与月历 — 只留金色精华</strong>', '<strong>3. Notes &amp; Grid — what stays</strong>'),
 ('月历可以贴到 GitHub 或个人主页，不露内容。', 'Share the grid anywhere. It shows no content.'),
 # why
 ('<div class="eyebrow">反囤积理念</div>', '<div class="eyebrow">Against hoarding</div>'),
 ('<h2>不做收藏夹墓地，也不搞倒计时焦虑。</h2>', '<h2>No bookmark graveyard. No countdown anxiety.</h2>'),
 ('>847 未读</text>', '>847 unread</text>'),
 ('aria-label="别的产品的做法"', 'aria-label="How other products do it"'),
 ('<span class="ttag">无限堆砌</span>', '<span class="ttag">Endless pile</span>'),
 ('<h3>Readwise、Raindrop、Notion</h3>', '<h3>Readwise, Raindrop, Notion</h3>'),
 ('为永远囤着而设计，连 MCP 也只是在翻一座越堆越满的旧仓库。', 'Built to keep everything forever. Even their MCP only searches an ever-growing pile.'),
 ('>23:41 过期</text>', '>23:41 left</text>'),
 ('<span class="ttag">24 小时倒计时</span>', '<span class="ttag">24-hour countdown</span>'),
 ('<h3>Burn 451 等「不读即焚」</h3>', '<h3>Burn 451 and “read or burn”</h3>'),
 ('用 24 小时倒计时逼着你抢救原文，救完依然塞进另一个文章库。', 'A 24-hour timer pushes you to rescue articles, which then land in yet another library.'),
 ('aria-label="精华的做法"', 'aria-label="How Keep Essence does it"'),
 ('<span class="ttag">精华</span>', '<span class="ttag">Keep Essence</span>'),
 ('<h3>先滤一遍，再留精华</h3>', '<h3>Filter first, keep the essence</h3>'),
 ('按你的规则先筛一遍，30 天自动清走，只有深挖过的笔记永久留下。', 'Filtered by your rules first, cleared after 30 days. Only the notes you dug into stay for good.'),
 # assistants
 ('<div class="eyebrow">接上你的助手</div>', '<div class="eyebrow">Connect your assistant</div>'),
 ('<h2>一个 MCP 地址，接上你的助手。</h2>', '<h2>One MCP address connects your assistant.</h2>'),
 ('想让助手替你筛、陪你深挖？接上你已经在用的那个就行。不用装任何东西，随时可以断开。', 'Want an assistant to filter for you and dig in with you? Connect the one you already use. Nothing to install, and you can disconnect at any time.'),
 ('<span class="mcp-note">内测开放后可用</span>', '<span class="mcp-note">Available when the beta opens</span>'),
 ('<span class="mlab">一步暂存</span>', '<span class="mlab">Save in one step</span>'),
 ('<strong>iPhone 快捷指令</strong><span>轻点即存</span>', '<strong>iPhone Shortcut</strong><span>Tap to save</span>'),
 ('<strong>浏览器扩展</strong><span>一键暂存</span>', '<strong>Browser extension</strong><span>One click</span>'),
 ('<strong>网页收件箱</strong><span>全平台</span>', '<strong>Web inbox</strong><span>Any device</span>'),
 ('<strong>手机分享菜单</strong><span>分享即存</span>', '<strong>Phone share sheet</strong><span>Share to save</span>'),
 ('<strong>Mac 菜单栏</strong><span>点一下就存</span>', '<strong>Mac menu bar</strong><span>One click</span>'),
 ('<strong>KeepEssence 核心</strong>', '<strong>KeepEssence core</strong>'),
 ('<span class="mlab">你的 AI 助手</span>', '<span class="mlab">Your AI assistant</span>'),
 ('<strong>Claude</strong><span>AI 助手</span>', '<strong>Claude</strong><span>AI assistant</span>'),
 ('<strong>ChatGPT</strong><span>AI 助手</span>', '<strong>ChatGPT</strong><span>AI assistant</span>'),
 ('<strong>Gemini</strong><span>AI 助手</span>', '<strong>Gemini</strong><span>AI assistant</span>'),
 ('<strong>你自己部署的助手</strong><span>定时自动处理</span>', '<strong>Your own agent</strong><span>Runs on a schedule</span>'),
 ('<strong>免费</strong><span>核心 + 你自己的 MCP 助手，或自己部署</span>', '<strong>Free</strong><span>Core + your own MCP assistant, or self-host</span>'),
 ('<strong>付费</strong><span>直接用内置助手，不用自己配</span>', '<strong>Paid</strong><span>Use the built-in assistant, nothing to set up</span>'),
 # dig
 ('<div class="eyebrow">深挖</div>', '<div class="eyebrow">Deep dive</div>'),
 ('<h2>每天只挑一两条，和助手聊透。</h2>', '<h2>Pick one or two a day and work them through.</h2>'),
 ('助手可以帮你筛、帮你先读，但留不留、留什么，只有你说了算。', 'An assistant can filter for you and read ahead for you. Whether to keep something, and what to keep, is yours alone to decide.'),
 ('<span class="ttag">第 1 步</span>', '<span class="ttag">Step 1</span>'),
 ('<h3>挑出值得的那一条</h3>', '<h3>Pick the one worth it</h3>'),
 ('在解读卡或每日摘要里点「深挖」，它就排进深挖队列，不会被 30 天清理带走。接了定时助手的话，它会趁你没空先把全文读透。', 'Tap Deep dive on a brief or in the Daily Digest and it joins your queue, safe from the 30-day clear-out. If you run a scheduled agent, it reads the whole thing ahead of you.'),
 ('<span class="ttag">第 2 步</span>', '<span class="ttag">Step 2</span>'),
 ('<h3>交给助手，不只是聊</h3>', '<h3>Hand it to your assistant — not just to chat</h3>'),
 ('说一句「深挖今天摘要里讲某某的那条」，助手自己把内容取过来。接下来追问、反驳、让它动手去做，都由你说了算。', 'Say “deep dive the one about X from today’s digest” and your assistant fetches it. From there you question it, push back, or have it do the work — your call.'),
 ('<span class="ttag">第 3 步</span>', '<span class="ttag">Step 3</span>'),
 ('</span>说一句「存成笔记」</h3>', '</span>Say “save it as a note”</h3>'),
 ('聊透了，你开口说存，它才变成一篇永久笔记。随时翻出来慢慢回味，也可以分享给别人。没说存的，照常到期清理。', 'Once you’ve worked it through and say so, it becomes a permanent note. Come back to it whenever you like, or share it. Anything you don’t save expires as usual.'),
 ('<span class="asks-lab">你可以对助手说</span>', '<span class="asks-lab">Things you can ask your assistant</span>'),
 ('<span class="ask">「帮我部署起来试试」</span>', '<span class="ask">“Turn the key points into a checklist”</span>'),
 ('<span class="ask">「跑一遍测试，看哪里不过」</span>', '<span class="ask">“Run the tests and show me what fails”</span>'),
 ('<span class="ask">「把这个技术细节查清楚」</span>', '<span class="ask">“Get to the bottom of this detail”</span>'),
 ('<span class="ask">「和我上次存的那篇对比一下」</span>', '<span class="ask">“Compare it with the one I saved last time”</span>'),
 ('<span class="ask">「按我的想法写成一篇新文章」</span>', '<span class="ask">“Turn my take on this into a new article”</span>'),
 ('你的助手会什么，就能对这条内容做什么。<strong>能走多远，只看你的想象力。</strong>', 'Ask for whatever you need. <strong>What it can do is limited only by your assistant.</strong>'),
 # join
 ('<div class="eyebrow">分批邀请</div>', '<div class="eyebrow">Invited in batches</div>'),
 ('<h2>申请内测</h2>', '<h2>Join the beta</h2>'),
 ('优先邀请两类人：用收藏或稍后读工具好几年的，和自己有 AI 助手、平时就用它处理知识的。', 'Two groups get invited first: people who have used bookmark or read-it-later tools for years, and people who already work through what they read with their own AI assistant.'),
 ('<label class="wlbl" for="wl-email">邮箱</label>', '<label class="wlbl" for="wl-email">Email</label>'),
 ('你存的东西，现在都堆在哪儿？<span style="color:var(--fg3);font-weight:400">（可多选）</span>', 'Where does what you save pile up today? <span style="color:var(--fg3);font-weight:400">(choose any)</span>'),
 ('value="tabs">浏览器标签页</label>', 'value="tabs">Browser tabs</label>'),
 ('value="wechat">微信文件传输助手</label>', 'value="wechat">Messages to myself</label>'),
 ('data-other-for="current_habit_other">其他</label>', 'data-other-for="current_habit_other">Other</label>'),
 ('placeholder="还有哪里？" aria-label="其他存放的地方"', 'placeholder="Where else?" aria-label="Other place you save things"'),
 ('你一般从哪里收集内容？<span style="color:var(--fg3);font-weight:400">（可多选）</span>', 'Where do you usually find things to save? <span style="color:var(--fg3);font-weight:400">(choose any)</span>'),
 ('                <label class="popt"><input type="checkbox" name="content_sources" value="wechat-mp">微信公众号</label>\n                <label class="popt"><input type="checkbox" name="content_sources" value="xiaohongshu">小红书</label>\n                <label class="popt"><input type="checkbox" name="content_sources" value="zhihu">知乎</label>\n                <label class="popt"><input type="checkbox" name="content_sources" value="bilibili">B 站</label>\n                <label class="popt"><input type="checkbox" name="content_sources" value="jike">即刻</label>\n                <label class="popt"><input type="checkbox" name="content_sources" value="weibo">微博</label>\n',
  '                <label class="popt"><input type="checkbox" name="content_sources" value="substack">Substack</label>\n                <label class="popt"><input type="checkbox" name="content_sources" value="linkedin">LinkedIn</label>\n                <label class="popt"><input type="checkbox" name="content_sources" value="medium">Medium</label>\n'),
 ('value="newsletter">邮件订阅</label>', 'value="newsletter">Newsletters</label>'),
 ('value="podcast">播客</label>', 'value="podcast">Podcasts</label>'),
 ('data-other-for="content_sources_other">其他</label>', 'data-other-for="content_sources_other">Other</label>'),
 ('placeholder="还有哪里？" aria-label="其他内容来源"', 'placeholder="Where else?" aria-label="Other source"'),
 ('<span class="wlbl">你最常用哪个 AI 助手？</span>', '<span class="wlbl">Which AI assistant do you use most?</span>'),
 ('value="self-hosted-agent">自托管 Agent</label>', 'value="self-hosted-agent">Self-hosted agent</label>'),
 ('value="none">暂时没有</label>', 'value="none">None yet</label>'),
 ('<span class="wlbl">你更想用哪种方式？</span>', '<span class="wlbl">How would you rather use it?</span>'),
 ('checked>通过 MCP 接入我自己的助手</label>', 'checked>Connect my own assistant over MCP</label>'),
 ('value="hosted-later">内测阶段用系统自带的 Agent</label>', 'value="hosted-later">Use the built-in agent during the beta</label>'),
 ('现在用的收藏工具，最让你头疼的是什么？<span style="color:var(--fg3);font-weight:400">（选填）</span>', 'What bothers you most about the tool you save with today? <span style="color:var(--fg3);font-weight:400">(optional)</span>'),
 ('placeholder="一句话就好。"', 'placeholder="One sentence is plenty."'),
 ('type="submit">申请内测</button>', 'type="submit">Join the beta</button>'),
 # faq + footer
 ('<h2>常见问题</h2>', '<h2>Questions</h2>'),
 ('<span><strong>精华</strong> · 阅尽千芳，只留精华</span>', '<span><strong>Keep Essence</strong> · Save freely. Keep the essence.</span>'),
 # script: samples
 ('src: "微信公众号 · 14 分钟前暂存", life: "剩余 29 天",', 'src: "Substack · saved 14 min ago", life: "29 days left",'),
 ('title: "AI 时代，普通人还能靠什么吃饭",', 'title: "AI and the future of your job",'),
 ('what: "一篇 8000 字长文，讲哪些工作最先被 AI 改写。",', 'what: "A 5,000-word essay on which jobs AI rewrites first.",'),
 ('facts: "约 20 分钟阅读 · 引用 3 份行业报告",', 'facts: "About 20 min read · cites 3 industry reports",'),
 ('key: "被替代的不是整个岗位，是岗位里重复的那部分。",', 'key: "It isn’t whole jobs that get replaced — it’s the repetitive part of each job.",'),
 ('["me", "深挖今天摘要里讲 AI 和饭碗的那篇。"],', '["me", "Deep dive the one about AI and jobs from today’s digest."],'),
 ('["ai", "取到了。它的核心是：被替代的是重复的那部分，不是整个岗位。你的工作里，哪些事每周都在重复？"],', '["ai", "Got it. Its core claim: the repetitive part gets replaced, not the whole job. What in your work repeats every week?"],'),
 ('["me", "写周报、整理会议纪要。那就先把这两样交出去。存成笔记。"],', '["me", "Weekly reports and meeting notes. I’ll hand those two off first. Save it as a note."],'),
 ('["note", "已存成笔记：先把重复的那部分交出去"]', '["note", "Saved as a note: Hand off the repetitive part"]'),
 ('src: "github.com · 42 分钟前暂存", life: "剩余 30 天",', 'src: "github.com · saved 42 min ago", life: "30 days left",'),
 ('what: "专门测试远程 MCP 服务的轻量测试工具。",', 'what: "A lightweight test tool for remote MCP servers.",'),
 ('facts: "TypeScript · 1.4k 星 · MIT · 昨日更新",', 'facts: "TypeScript · 1.4k stars · MIT · updated yesterday",'),
 ('key: "一条命令测完登录续期和重复调用两类问题。",', 'key: "One command checks both login renewal and repeated calls.",'),
 ('["me", "这个测试工具帮我部署一下，我们试试看。"],', '["me", "Deploy this test tool for me and let’s try it."],'),
 ('["ai", "部署好了，拿你上周写的那个 MCP 服务跑了一遍，生成了测试结果页。登录续期通过，重复调用有 2 处没过。"],', '["ai", "Deployed. I ran it against the MCP server you wrote last week and made a results page. Login renewal passes; repeated calls fail in 2 places."],'),
 ('["me", "这条经验存成笔记。"],', '["me", "Save that lesson as a note."],'),
 ('["note", "已存成笔记：MCP 服务上线前，先过重放校验"]', '["note", "Saved as a note: Test replays before you ship"]'),
 ('src: "小红书 · 2 小时前暂存", life: "剩余 7 天",', 'src: "X · saved 2 h ago", life: "7 days left",'),
 ('title: "炸了！这个 AI 工具让我一天干完一周的活",', 'title: "This AI tool did my week’s work in a day 🤯",'),
 ('what: "一条种草帖，推荐一个 AI 效率工具，文末带购买链接。",', 'what: "A promo thread for an AI productivity tool, ending in an affiliate link.",'),
 ('facts: "9 张图 · 没有实测 · 评论区多是同一套话术",', 'facts: "9 posts · no real test · replies read like one script",'),
 ('key: "它说的三个功能，你上个月存的帖子里都讲过。",', 'key: "All three features it lists were in posts you saved last month.",'),
 ('["me", "这条里有我没见过的东西吗？"],', '["me", "Is there anything in this I haven’t seen before?"],'),
 ('["ai", "没有。它说的三个功能，你上个月存的三条帖子里都讲过，这条只多了一个购买链接。"],', '["ai", "No. The three features it lists were all in three posts you saved last month. This one only adds an affiliate link."],'),
 ('["me", "那就不留了。"],', '["me", "Then I won’t keep it."],'),
 ('["end", "没存笔记，7 天后自动清理"]', '["end", "No note saved — clears itself in 7 days"]'),
 ('src: "微信公众号 · 5 分钟前暂存", life: "剩余 30 天",', 'src: "Hacker News · saved 5 min ago", life: "30 days left",'),
 ('title: "某大厂发布新一代 AI 模型",', 'title: "Big lab ships its next-gen model",'),
 ('what: "转述官方通稿的发布快讯。",', 'what: "A launch brief that restates the official announcement.",'),
 ('facts: "约 2 分钟阅读 · 3 项主要更新 · 没有第三方实测",', 'facts: "About 2 min read · 3 main changes · no independent tests",'),
 ('key: "价格降了一半；写作和整理资料的功能没有变化。",', 'key: "Half the price; writing and research features are unchanged.",'),
 ('["me", "这次更新对我有影响吗？"],', '["me", "Does this update affect me?"],'),
 ('["ai", "按你之前的笔记，你主要用它写稿和整理资料，这两样没变，只是便宜了一半。别人踩过的坑：新版默认打开联网，写稿前记得关。"],', '["ai", "Going by your earlier notes, you mainly use it to draft and to organise research. Neither changed; it’s just half the price. One trap others hit: web access is on by default now, so turn it off before drafting."],'),
 ('["me", "好，存成笔记。"],', '["me", "Good. Save it as a note."],'),
 ('["note", "已存成笔记：新版便宜一半，写稿前先关联网"]', '["note", "Saved as a note: Half price; web off to draft"]'),
 # script: messages
 ('deepdive: "已加入深挖队列。定时来的助手下次取活时将先做精读。",', 'deepdive: "Added to your deep-dive queue. A scheduled assistant reads it through on its next run.",'),
 ('dismiss: "已标为不感兴趣。移入今日摘要的「其余的」，并记录负向信号。",', 'dismiss: "Marked not interested. Moved to Everything else in today’s digest, and noted as a signal.",'),
 ('seen: "已标为看过了。仅移入「其余的」，不影响你的筛选规则。",', 'seen: "Marked as seen. Moved to Everything else; your filtering rules are unaffected.",'),
 ('keep: "已收藏：取消 30 天自动清理，条目与解读将原样保留。"', 'keep: "Kept: it no longer expires after 30 days. The item and its brief stay as they are."'),
 ('hand taps 深挖,', 'hand taps Deep dive,'),
 ('Flash the 初步解读 pill', 'Flash the Quick brief pill'),
 ('gn.textContent = next ? "已标记为已读 · 晚安" : "读了，晚安";', 'gn.textContent = next ? "Marked as read · good night" : "Read, good night";'),
 ('copyBtn.textContent = "已复制地址";', 'copyBtn.textContent = "Copied";'),
 ('// Each 其他 checkbox', '// Each Other checkbox'),
 ('sub.textContent = "申请内测 · 马上开放";', 'sub.textContent = "Join the beta · opening soon";'),
 ('return show("稍等，内测名单马上就来。开放后回到这里就能申请。");', 'return show("Hold on — the beta list opens very soon. Come back here to sign up once it does.");'),
 ('return show("请输入有效的电子邮箱地址。", true);', 'return show("Please enter a valid email address.", true);'),
 
 ('sub.textContent = "提交中…";', 'sub.textContent = "Sending…";'),
 
 ('data-done-title>报名成功</p>', 'data-done-title>You’re in</p>'),
 ('data-done-close>好的</button>', 'data-done-close>OK</button>'),
 ('show(again ? "这个邮箱已在内测名单里，我们会按批次邮件通知。" : "已加入内测名单。开放名额时我们会通过邮件联系你。");', 'show(again ? "This email is already on the beta list. We’ll email you when your batch opens." : "You’re on the beta list. We’ll email you when a spot opens.");'),
 ('if (again) confirmDone("你已经在名单里了", `${email} 之前报过名，不用重复提交。开放名额时我们会发邮件通知你。`);', 'if (again) confirmDone("You’re already on the list", `${email} signed up earlier, so there’s nothing more to do. We’ll email you when a spot opens.`);'),
 ('else confirmDone("报名成功", `${email} 已加入内测名单。开放名额时我们会发邮件通知你。`);', 'else confirmDone("You’re in", `${email} is on the beta list. We’ll email you when a spot opens.`);'),
 ('show("提交过于频繁，请一分钟后再试。", true);', 'show("Too many attempts. Please try again in a minute.", true);'),
 ('show("暂时无法连接到等待列表服务，请稍后再试。", true);', 'show("Couldn’t reach the sign-up service. Please try again later.", true);'),
 ('lang: "zh-Hans",', 'lang: "en",'),
 
]
# verdict / tab / label strings that repeat
MULTI = [
 ('值得深挖', 'Worth digging into'), ('知道就行', 'Good to know'), ('可以略过', 'Skip'),
 ('<span class="on">今天</span>', '<span class="on">Today</span>'), ('<span>今天</span>', '<span>Today</span>'),
 ('<span class="on">每日摘要</span>', '<span class="on">Digest</span>'), ('<span>每日摘要</span>', '<span>Digest</span>'),
 ('<span class="on">笔记</span>', '<span class="on">Notes</span>'), ('<span>笔记</span>', '<span>Notes</span>'),
 ('<span>助手设置</span>', '<span>Settings</span>'),
]
missing = []
for a, b in R:
    if t.count(a) != 1: missing.append((t.count(a), a[:70]))
    t = t.replace(a, b)
for a, b in MULTI:
    if t.count(a) < 1: missing.append((0, a))
    t = t.replace(a, b)

# FAQ block (visible) rebuilt in English
f = t.index('<div class="faqs">'); e = t.index('</div>', t.rindex('</details>', f, t.index('</section>', f)))
t = t[:f] + '<div class="faqs">\n' + ''.join(f'          <details class="faq">\n            <summary>{q}</summary>\n            <p>{a}</p>\n          </details>\n' for q, a in FAQ) + '        ' + t[e:]

# structured data in the English head: FAQ entries must equal the visible ones
s = t.index('"@type": "FAQPage"'); i = t.index('[', t.index('"mainEntity": [', s)); d = 0
for j in range(i, len(t)):
    if t[j] == '[': d += 1
    elif t[j] == ']':
        d -= 1
        if d == 0: break
ent = ',\n'.join('          {\n            "@type": "Question",\n            "name": %s,\n            "acceptedAnswer": {\n              "@type": "Answer",\n              "text": %s\n            }\n          }' % (json.dumps(q, ensure_ascii=False), json.dumps(a, ensure_ascii=False)) for q, a in FAQ)
t = t[:i] + '[\n' + ent + '\n        ]' + t[j + 1:]

# English body font stack and line height
t = t.replace('--font: "Inter", -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;', '--font: "Inter", -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans SC", sans-serif;')

EN_CSS = """
    /* English page only: longer words than the Chinese page */
    .brand span, .lang, .btn-sm { white-space: nowrap; }
    .pcap { min-height: 70px; }
    .chat-top { gap: 10px; white-space: nowrap; }
    .sw-fg { transform: translateX(88px); }
    .sw-wrap[data-sw="left"] .sw-fg { transform: translateX(-62px); }
    .sw-wrap[data-sw="rest"] .sw-fg { transform: translateX(0); }
    @media (max-width: 640px) {
      .brand { font-size: 15px; letter-spacing: .02em; gap: 8px; }
      .nav-r { gap: 8px; }
      .btn-sm { padding: 0 11px; }
    }
  </style>"""
t = t.replace('  </style>', EN_CSS, 1)
open('index.html', 'w', encoding='utf-8').write(t)
json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', t, re.S).group(1))
print('unmatched replacements:', len(missing))
for m in missing: print('  ', m)
left = [(n, l.strip()[:150]) for n, l in enumerate(t.split('\n'), 1) if re.search(r'[一-鿿「」，。？！：；、（）]', l)]
print('lines still containing Chinese:', len(left))
for n, l in left: print('  ', n, l)
