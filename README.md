# KeepEssence site

官网 [www.keepessence.app](https://www.keepessence.app) 的源文件。不带 www 的 keepessence.app 留给应用（网页应用、接口和 MCP），不是官网。页面是静态文件；唯一的服务端代码是 `worker.js`，负责接收内测报名。
Source of the KeepEssence website: static pages, plus one small Worker that stores beta sign-ups.

| 路径 | 内容 |
|---|---|
| `index.html` | 英文首页 |
| `zh/index.html` | 中文首页 |
| `assets/` | 图标、标志、分享图 |
| `llms.txt`、`robots.txt`、`sitemap.xml` | 给搜索引擎和 AI 的说明。`llms.txt` 的文字由 Marketing 写（marketing 仓库 `content/site-refresh-2026-11-27/llms.txt`），这里整份照用 |
| `worker.js` | 接收内测报名（`POST /api/v1/waitlist`），存进 D1 数据库。不发邮件 |
| `migrations/` | 报名数据库的表结构 |
| `.build/make_en.py` | 从中文页生成英文页的脚本 |
| `.build/check.py` | 两个页面的检查：配色是不是 spec 的 token、用词、金色、示例角标、中英结构一致、链接；`llms.txt` 不带旧说法；分享图 |
| `.build/og-draft/` | 分享图的**草稿**，不是线上资源：不在 `assets/`，页面不引用，`.assetsignore` 不让它发布。见里面的 README |

## 怎么看

直接用浏览器打开 `index.html`，或在本目录起一个静态服务器：

```
python3 -m http.server 8000
```

## 怎么改

改中文页 `zh/index.html`。英文页 `index.html` 不要手改：它由脚本从中文页生成，结构、样式和脚本与中文页一致，英文文案写在 `.build/make_en.py` 里。改完中文页后运行：

```
python3 .build/make_en.py
python3 .build/check.py        # 要有 ../spec 这个仓库在旁边，或者加 --spec <spec 里 design/tokens.css 的路径>
```

`make_en.py` 在中文页有一句英文里没有对应、或英文页里还剩中文时会停下来，列出是哪几句。`check.py` 检查：

- **配色、圆角、字号**是 spec 的设计 token（`design/tokens.css`）：页面里 `tokens:start` 到 `tokens:end` 之间是原样的拷贝，和 spec 差一个值就报错。spec 改了 token，这里改完再跑。
- **用词**：词表里不用的词、品牌稿里写明不能写成已上线的能力（快捷指令、菜单栏、PDF、保留天数、点名某个助手已接通、没逐个试过的浏览器）。
- **金色**只在「值得深挖」的判定和月历的金点上。
- **一个主按钮**：页面上的按钮只有一个标签（申请内测），首屏和结尾各一次。
- **示例**：三张示意卡片（解读、每日摘要、月历）各有「示例」角标。
- 中英两页结构一致，英文页就是 `make_en.py` 生成的那一份，页内链接和引用的文件都在。
- **`llms.txt`** 不带旧说法（快捷指令、菜单栏、保留天数、点名助手、报价、没逐个试过的浏览器）。
- **分享图**：草稿（文件名带 DRAFT）不在发布的目录里、页面不引用；`python3 .build/check.py --release` 在分享图还是旧的那张（图里有旧标语）时报错，发布前要这样跑一次。

页面上关于产品能做什么的话，只写 `marketing` 的 `IMPLEMENTATION-FACTS.md` 和验收记录里验过的。

## 内测报名

报名表单提交到本站的 `/api/v1/waitlist`，由 `worker.js` 校验后写入 D1 数据库 `keepessence-waitlist`。同一个邮箱只留第一次；机器人填的隐藏字段会被丢弃；同一地址一分钟最多 5 次。

部署（数据库已建好，id 在 `wrangler.toml` 里）：

```
wrangler d1 migrations apply keepessence-waitlist --remote   # 只在 migrations/ 有新文件时需要
wrangler secret put ENROLLED_PASSWORD                         # 只在第一次或换密码时需要
wrangler deploy
```

### 看名单

打开 `https://www.keepessence.app/enrolled`，浏览器会弹出登录框：用户名随便填，密码是上面设的那个。页面上可以按中英文页筛选、搜索，也可以下载表格（`/enrolled.csv`）。这个地址不在任何页面上挂链接，也不让搜索引擎收录。

密码只存在 Cloudflare 的密钥里，不写进代码（本仓库是公开的）。本地测试时放在 `.dev.vars`，该文件不进 git、不会被部署。

导出名单：

```
wrangler d1 execute keepessence-waitlist --remote --json --command "SELECT * FROM signups ORDER BY created_at"
```

本地测试：`wrangler d1 migrations apply keepessence-waitlist --local`，然后 `wrangler dev --local`。

临时关掉报名：把两个页面脚本里的 `WAITLIST_OPEN` 改成 `false`，按钮会变灰且不发送任何数据。页面上关于产品的说法以 [spec](https://github.com/KeepEssenceApp/spec) 为准。

## 参与

错字、失效的链接、翻译问题直接提 PR。见 [贡献指南](https://github.com/KeepEssenceApp/.github/blob/main/CONTRIBUTING.md)。

许可证：代码 [AGPL-3.0](LICENSE)。KeepEssence 的名称和标志不在许可范围内。
