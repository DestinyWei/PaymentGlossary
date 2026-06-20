#!/usr/bin/env python3
"""Build static article pages from articles/content.json."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"
DATA_FILE = ARTICLES_DIR / "content.json"
SITE_URL = "https://payment.0xhowe.top"
SOCIAL_URL = "https://x.com/allscale_zh"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def site_header(active: str = "articles") -> str:
    article_class = ' class="active"' if active == "articles" else ""
    glossary_class = ' class="active"' if active == "glossary" else ""
    return f"""<header class="site-header">
  <div class="site-header-inner">
    <a class="brand" href="/" aria-label="AllScale 支付术语手册">
      <img src="/articles/assets/allscale-logo.png" alt="AllScale">
    </a>
    <nav class="site-nav" aria-label="主导航">
      <a href="/"{glossary_class}>术语手册</a>
      <a href="/articles/"{article_class}>专题文章</a>
      <a class="social-link" href="{SOCIAL_URL}" target="_blank" rel="noreferrer">中文社媒 ↗</a>
    </nav>
  </div>
</header>"""


def site_footer() -> str:
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <span>© 2026 AllScale · Payments Knowledge Base</span>
    <a href="{SOCIAL_URL}" target="_blank" rel="noreferrer">关注 AllScale 中文社媒</a>
  </div>
</footer>"""


def page_head(title: str, description: str, canonical: str, image: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="AllScale 支付知识库">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(SITE_URL + image)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="/articles/styles.css">
</head>"""


def render_blocks(blocks: list[dict[str, object]]) -> str:
    rendered = []
    for block in blocks:
        kind = block["type"]
        if kind == "h2":
            rendered.append(f"<h2>{esc(block['text'])}</h2>")
        elif kind == "p":
            rendered.append(f"<p>{esc(block['text'])}</p>")
        elif kind in {"ul", "ol"}:
            items = "".join(f"<li>{esc(item)}</li>" for item in block["items"])
            rendered.append(f"<{kind}>{items}</{kind}>")
        elif kind == "image":
            rendered.append(
                f'<figure class="article-figure"><img src="{esc(block["src"])}" '
                f'alt="{esc(block["alt"])}" loading="lazy" decoding="async"></figure>'
            )
    return "\n".join(rendered)


def build_index(articles: list[dict[str, object]]) -> None:
    cards = []
    for article in articles:
        search_text = f"{article['title']} {article['summary']}".lower()
        cards.append(
            f"""<a class="article-card" href="/articles/{esc(article['slug'])}/" data-search="{esc(search_text)}">
  <img class="article-card-image" src="{esc(article['image'])}" alt="" loading="lazy">
  <span class="article-card-copy">
    <span class="series-number">第 {article['order']:02d} 篇</span>
    <h3>{esc(article['title'])}</h3>
    <p>{esc(article['summary'])}</p>
    <span class="read-more">阅读全文 →</span>
  </span>
</a>"""
        )

    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": article["order"],
                "name": article["title"],
                "url": f"{SITE_URL}/articles/{article['slug']}/",
            }
            for article in articles
        ],
    }
    structured_data = json.dumps(item_list, ensure_ascii=False).replace("</", "<\\/")
    page = f"""{page_head('支付术语科普系列文章｜AllScale', 'AllScale 支付术语科普系列：从 Checkout、跨境清算到稳定币与全球支付牌照。', f'{SITE_URL}/articles/', '/articles/assets/series-cover.webp')}
<body>
{site_header()}
<main>
  <section class="library-hero">
    <div class="page-shell">
      <div class="eyebrow">Payments Education Series</div>
      <h1>支付术语<em>科普系列</em></h1>
      <p class="hero-summary">从一次“立即支付”出发，把卡支付、跨境清算、稳定币与合规牌照讲清楚。每篇解决一个具体问题，持续更新。</p>
      <div class="series-facts"><span>16 篇专题</span><span>60 页合集</span><span>持续更新</span></div>
    </div>
  </section>

  <div class="page-shell">
    <section class="series-intro">
      <img class="series-cover" src="/articles/assets/series-cover.webp" alt="AllScale 支付术语科普系列文章完整合集封面">
      <div class="series-copy">
        <div class="eyebrow">About The Series</div>
        <h2>从“看懂一个词”，走到“理解一条完整资金链路”</h2>
        <p>术语手册适合快速查询，这套专题文章则负责解释来龙去脉。现有内容覆盖收银台、开票、拒付、卡支付角色、跨境汇款、稳定币、钱包托管和全球牌照。</p>
        <a href="{SOCIAL_URL}" target="_blank" rel="noreferrer">关注中文社媒，获取后续更新 ↗</a>
      </div>
    </section>

    <section class="article-library" aria-labelledby="article-list-title">
      <div class="library-heading">
        <div>
          <div class="eyebrow">Article Library</div>
          <h2 id="article-list-title">全部文章</h2>
        </div>
        <input class="article-search" type="search" placeholder="搜索文章，例如 Checkout、KYC、稳定币" aria-label="搜索文章">
      </div>
      <div class="article-grid">{''.join(cards)}</div>
      <div class="empty-state">没有找到匹配文章</div>
    </section>
  </div>
</main>
{site_footer()}
<script>
  const search = document.querySelector('.article-search');
  const cards = [...document.querySelectorAll('.article-card')];
  const empty = document.querySelector('.empty-state');
  search.addEventListener('input', () => {{
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {{
      const matches = !query || card.dataset.search.includes(query);
      card.hidden = !matches;
      if (matches) visible += 1;
    }});
    empty.style.display = visible ? 'none' : 'block';
  }});
</script>
<script type="application/ld+json">{structured_data}</script>
</body>
</html>
"""
    (ARTICLES_DIR / "index.html").write_text(page, encoding="utf-8")


def build_article(article: dict[str, object], previous: dict[str, object] | None, following: dict[str, object] | None) -> None:
    canonical = f"{SITE_URL}/articles/{article['slug']}/"
    nav_items = []
    if previous:
        nav_items.append(
            f"<a href=\"/articles/{esc(previous['slug'])}/\"><small>上一篇</small><strong>{esc(previous['title'])}</strong></a>"
        )
    else:
        nav_items.append("<span></span>")
    if following:
        nav_items.append(
            f"<a href=\"/articles/{esc(following['slug'])}/\"><small>下一篇</small><strong>{esc(following['title'])}</strong></a>"
        )
    else:
        nav_items.append("<span></span>")

    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["title"],
        "description": article["summary"],
        "image": SITE_URL + article["image"],
        "author": {"@type": "Organization", "name": "AllScale"},
        "publisher": {"@type": "Organization", "name": "AllScale"},
        "mainEntityOfPage": canonical,
    }
    structured_data = json.dumps(article_schema, ensure_ascii=False).replace("</", "<\\/")
    page = f"""{page_head(f"{article['title']}｜AllScale", article['summary'], canonical, article['image'])}
<body>
{site_header()}
<main class="article-shell">
  <nav class="breadcrumb" aria-label="面包屑">
    <a href="/">术语手册</a><span>/</span><a href="/articles/">专题文章</a><span>/</span><span>第 {article['order']:02d} 篇</span>
  </nav>
  <article>
    <header class="article-header">
      <div class="article-kicker">AllScale 支付术语科普 · 第 {article['order']:02d} 篇</div>
      <h1>{esc(article['title'])}</h1>
      <p class="article-deck">{esc(article['summary'])}</p>
    </header>
    <img class="article-hero-image" src="{esc(article['image'])}" alt="{esc(article['title'])}">
    <div class="article-body">{render_blocks(article['blocks'])}</div>
  </article>

  <section class="social-cta">
    <h2>继续关注 AllScale 支付科普</h2>
    <p>后续文章和支付行业内容会在 AllScale 中文社媒同步发布。</p>
    <a href="{SOCIAL_URL}" target="_blank" rel="noreferrer">关注 @allscale_zh ↗</a>
  </section>
  <nav class="article-pagination" aria-label="文章翻页">{''.join(nav_items)}</nav>
</main>
{site_footer()}
<script type="application/ld+json">{structured_data}</script>
</body>
</html>
"""
    output_dir = ARTICLES_DIR / str(article["slug"])
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(page, encoding="utf-8")


def build_discovery_files(articles: list[dict[str, object]]) -> None:
    urls = [f"{SITE_URL}/", f"{SITE_URL}/articles/"] + [
        f"{SITE_URL}/articles/{article['slug']}/" for article in articles
    ]
    sitemap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += "".join(f"  <url><loc>{esc(url)}</loc></url>\n" for url in urls)
    sitemap += "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )


def main() -> None:
    articles = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    build_index(articles)
    for index, article in enumerate(articles):
        previous = articles[index - 1] if index > 0 else None
        following = articles[index + 1] if index + 1 < len(articles) else None
        build_article(article, previous, following)
    build_discovery_files(articles)
    print(f"Built {len(articles)} article pages and the article index")


if __name__ == "__main__":
    main()
