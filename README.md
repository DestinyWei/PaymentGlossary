# PaymentGlossary

PaymentGlossary 是 AllScale 的双语支付知识站，包括中英文支付行业术语手册和持续更新的支付科普专题。内容覆盖常见概念、交易链路、跨境清算、稳定币、合规牌照、风控与商业指标。

## 项目结构

- `index.html`：Vercel 部署入口，默认跳转到 `/zh/`。
- `zh/index.html`：中文支付术语手册主页，对应线上 `/zh/`。
- `en/index.html`：英文支付术语手册主页，对应线上 `/en/`。
- `zh/glossary/<section>/index.html`、`en/glossary/<section>/index.html`：术语手册板块 SEO 入口。
- `analytics.js`：Vercel Web Analytics 的全站加载入口，本地预览时不会发送数据。
- `favicon.ico`、`favicon-32x32.png`、`apple-touch-icon.png`：由 AllScale 官方 Media Kit 图标生成的站点图标。
- `zh/articles/index.html`、`en/articles/index.html`：中英文专题文章索引。
- `zh/articles/<slug>/index.html`、`en/articles/<slug>/index.html`：中英文独立文章页面。
- `articles/index.html`、`articles/<slug>/index.html`：旧文章路径兼容跳转到中文新路径。
- `articles/content.json`：中文文章标题、摘要和正文的结构化数据源。
- `articles/content.en.json`：英文文章标题、摘要和正文的结构化数据源。
- `articles/assets/`：文章插图、系列封面和 AllScale Logo。
- `articles/styles.css`：文章索引和正文页共用样式。
- `scripts/build_articles.py`：根据 `content.json` 生成文章页、站点地图和爬虫配置。
- `scripts/import_articles.py`：从完整合集 PDF 导入首批文章及插图的一次性工具。
- `scripts/import_english_articles.py`：从英文完整合集 PDF 导入英文文章及英文头图的一次性工具。
- `scripts/import_docx_images.py`：从完整合集 DOCX 导入文章原始配图并插入对应章节。
- `sitemap.xml`、`robots.txt`：搜索引擎发现文件，由构建脚本生成。

## 本地预览

线上页面都是静态 HTML，不需要 Node.js 依赖。由于站内链接使用根路径，建议在仓库根目录启动静态服务预览：

```bash
python3 -m http.server 8787
```

然后访问：

- 中文术语手册：`http://127.0.0.1:8787/zh/`
- 英文术语手册：`http://127.0.0.1:8787/en/`
- 中文专题文章：`http://127.0.0.1:8787/zh/articles/`
- 英文专题文章：`http://127.0.0.1:8787/en/articles/`

## 部署说明

Vercel 会识别仓库根目录和各文章目录中的 `index.html`。更新主页设计稿时，请确保根入口仍命名为 `index.html`；新增文章时，每个 slug 目录也必须保留自己的 `index.html`。

当前正式域名为 `https://payment.0xhowe.top`，双语地址格式为：

```text
https://payment.0xhowe.top/zh/
https://payment.0xhowe.top/en/
https://payment.0xhowe.top/zh/glossary/<section>/
https://payment.0xhowe.top/en/glossary/<section>/
https://payment.0xhowe.top/zh/articles/<slug>/
https://payment.0xhowe.top/en/articles/<slug>/
```

根路径 `/` 会自动跳转到 `/zh/`。旧文章路径 `/articles/` 和 `/articles/<slug>/` 保留为兼容跳转，避免已有分享链接失效。

AllScale 中文社媒：<https://x.com/allscale_zh>

## 访问数据

网站已接入 Vercel Web Analytics。首次使用时，在对应 Vercel 项目的 **Analytics** 页面点击 **Enable**，然后重新部署一次；数据会显示在该项目的 Analytics 仪表盘中。

- `Page Views`：所选时间范围内的总浏览量，可切换到每日趋势。
- `Visitors`：每日独立访客及所选时间范围内的访客趋势。
- `Bounce Rate`：只浏览一个页面便离开的会话比例。
- `Pages / Referrers`：热门页面、热门文章及外部访问来源。
- `Country / Device / Browser / OS`：地区和访问设备分布。

Vercel 的访客识别不使用 Cookie；本地 `localhost` 或 `127.0.0.1` 预览不会加载统计脚本。可查看的历史总量取决于当前 Vercel 套餐的数据保留周期。

AllScale 品牌图标来源：<https://www.allscale.io/media-kit>

## 新增文章

1. 在 `articles/content.json` 和/或 `articles/content.en.json` 末尾新增文章对象，按现有结构填写 `order`、`slug`、`title`、`summary`、`image` 和 `blocks`。
2. 将文章插图放入 `articles/assets/`，建议使用 WebP 格式。
3. 运行生成脚本：

```bash
python3 scripts/build_articles.py
```

4. 本地检查文章索引、独立页面、上一篇/下一篇链接和移动端布局。

`slug` 发布后应保持稳定。中英文文章建议使用相同 `slug`，这样语言切换和 hreflang 能指向对应内容。

## 重新导入完整合集

当完整合集源文件更新时，按“正文 → 配图 → 静态页面”的顺序重新生成：

```bash
python3 scripts/import_articles.py "/path/to/AllScale 支付术语科普系列文章 · 完整合集.pdf"
python3 scripts/import_docx_images.py "/path/to/AllScale 支付术语科普系列文章 · 完整合集.docx"
python3 scripts/import_english_articles.py "/path/to/AllScale Payment Glossary Series · Complete Anthology_Watermark.pdf"
python3 scripts/build_articles.py
```

DOCX 图片导入必须在中文 PDF 正文导入之后执行，否则中文正文导入会覆盖图片块。英文 PDF 导入会生成 `articles/content.en.json` 和 `articles/assets/en-*.webp`。

## 更新流程

1. 更新 `zh/index.html`、`en/index.html` 或文章 JSON 中的内容。
2. 修改文章后运行 `python3 scripts/build_articles.py` 重新生成静态页面。
3. 本地预览并检查 `/zh/`、`/en/`、`/zh/glossary/<section>/`、`/en/glossary/<section>/`、中英文文章页、语言切换、搜索和移动端布局。
4. 执行基础校验后提交并推送到 `main`，交由 Vercel 自动部署。
