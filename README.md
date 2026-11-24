# KeepEssence site

官网 [www.keepessence.app](https://www.keepessence.app) 的源文件。不带 www 的 keepessence.app 留给应用（网页应用、接口和 MCP），不是官网。页面是静态文件；唯一的服务端代码是 `worker.js`，负责接收内测报名。
Source of the KeepEssence website: static pages, plus one small Worker that stores beta sign-ups.

| 路径 | 内容 |
|---|---|
| `index.html` | 英文首页 |
| `zh/index.html` | 中文首页 |
| `assets/` | 图标、标志、分享图 |
| `llms.txt`、`robots.txt`、`sitemap.xml` | 给搜索引擎和 AI 的说明 |
| `worker.js` | 接收内测报名（`POST /api/v1/waitlist`），存进 D1 数据库。不发邮件 |
| `migrations/` | 报名数据库的表结构 |
| `.build/make_en.py` | 从中文页生成英文页的脚本 |

## 怎么看

直接用浏览器打开 `index.html`，或在本目录起一个静态服务器：

```
python3 -m http.server 8000
```

## 怎么改

改中文页 `zh/index.html`。英文页 `index.html` 不要手改：它由脚本从中文页生成，结构、样式和动效与中文页一致，英文文案写在脚本里。改完中文页后运行：

```
python3 .build/make_en.py
```

脚本会报告还没翻译的中文。新增或改动了中文文案，要在脚本里补上对应的英文。

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
