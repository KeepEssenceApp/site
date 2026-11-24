# KeepEssence site

官网 [keepessence.app](https://keepessence.app) 的源文件。纯静态，不需要构建。
Source of the KeepEssence website. Plain static files, no build step.

| 路径 | 内容 |
|---|---|
| `index.html` | 英文首页 |
| `zh/index.html` | 中文首页 |
| `assets/` | 图标、标志、分享图 |
| `llms.txt`、`robots.txt`、`sitemap.xml` | 给搜索引擎和 AI 的说明 |

## 怎么看

直接用浏览器打开 `index.html`，或在本目录起一个静态服务器：

```
python3 -m http.server 8000
```

## 怎么改

直接改 HTML。中英文两页内容要同步改。页面上关于产品的说法以 [spec](https://github.com/KeepEssenceApp/spec) 为准。

## 参与

错字、失效的链接、翻译问题直接提 PR。见 [贡献指南](https://github.com/KeepEssenceApp/.github/blob/main/CONTRIBUTING.md)。

许可证：代码 [AGPL-3.0](LICENSE)。KeepEssence 的名称和标志不在许可范围内。
