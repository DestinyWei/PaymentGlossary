# PaymentGlossary

PaymentGlossary 是 AllScale 的支付知识站，包括支付行业术语手册和持续更新的支付科普专题。内容覆盖常见概念、交易链路、跨境清算、稳定币、合规牌照、风控与商业指标。

## 项目结构

- `index.html`：Vercel 部署入口和支付术语手册主页。
- `articles/index.html`：专题文章索引，对应线上 `/articles/`。
- `articles/<slug>/index.html`：独立文章页面，对应线上 `/articles/<slug>/`。
- `articles/content.json`：文章标题、摘要和正文的结构化数据源。
- `articles/assets/`：文章插图、系列封面和 AllScale Logo。
- `articles/styles.css`：文章索引和正文页共用样式。
- `scripts/build_articles.py`：根据 `content.json` 生成文章页、站点地图和爬虫配置。
- `scripts/import_articles.py`：从完整合集 PDF 导入首批文章及插图的一次性工具。
- `scripts/import_docx_images.py`：从完整合集 DOCX 导入文章原始配图并插入对应章节。
- `sitemap.xml`、`robots.txt`：搜索引擎发现文件，由构建脚本生成。

## 本地预览

线上页面都是静态 HTML，不需要 Node.js 依赖。由于站内链接使用根路径，建议在仓库根目录启动静态服务预览：

```bash
python3 -m http.server 8787
```

然后访问：

- 术语手册：`http://127.0.0.1:8787/`
- 专题文章：`http://127.0.0.1:8787/articles/`

## 部署说明

Vercel 会识别仓库根目录和各文章目录中的 `index.html`。更新主页设计稿时，请确保根入口仍命名为 `index.html`；新增文章时，每个 slug 目录也必须保留自己的 `index.html`。

当前正式域名为 `https://payment.0xhowe.top`，文章地址格式为：

```text
https://payment.0xhowe.top/articles/<slug>/
```

AllScale 中文社媒：<https://x.com/allscale_zh>

## 新增文章

1. 在 `articles/content.json` 末尾新增文章对象，按现有结构填写 `order`、`slug`、`title`、`summary`、`image` 和 `blocks`。
2. 将文章插图放入 `articles/assets/`，建议使用 WebP 格式。
3. 运行生成脚本：

```bash
python3 scripts/build_articles.py
```

4. 本地检查文章索引、独立页面、上一篇/下一篇链接和移动端布局。

`slug` 发布后应保持稳定，避免已有分享链接和搜索引擎收录失效。

## 重新导入完整合集

当完整合集源文件更新时，按“正文 → 配图 → 静态页面”的顺序重新生成：

```bash
python3 scripts/import_articles.py "/path/to/AllScale 支付术语科普系列文章 · 完整合集.pdf"
python3 scripts/import_docx_images.py "/path/to/AllScale 支付术语科普系列文章 · 完整合集.docx"
python3 scripts/build_articles.py
```

DOCX 图片导入必须在 PDF 正文导入之后执行，否则正文导入会覆盖图片块。

## 更新流程

1. 更新主页或 `articles/content.json` 中的文章内容。
2. 修改文章后运行 `python3 scripts/build_articles.py` 重新生成静态页面。
3. 本地预览并检查页面标题、导航、搜索、交互地图和移动端布局。
4. 执行基础校验后提交并推送到 `main`，交由 Vercel 自动部署。
