#!/usr/bin/env python3
"""Build bilingual static article pages from structured JSON content."""

from __future__ import annotations

import html
import json
import shutil
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTICLES_DIR = ROOT / "articles"
SITE_URL = "https://payment.0xhowe.top"
ZH_SOCIAL_URL = "https://x.com/allscale_zh"
EN_SOCIAL_URL = "https://x.com/allscale"


@dataclass(frozen=True)
class Locale:
    code: str
    html_lang: str
    base: str
    data_file: Path
    social_url: str
    og_site_name: str
    glossary_label: str
    articles_label: str
    social_label: str
    social_cta: str
    language_label: str
    alternate_label: str
    index_title: str
    index_description: str
    hero_eyebrow: str
    hero_title: str
    hero_summary: str
    facts: tuple[str, str, str]
    about_eyebrow: str
    about_title: str
    about_copy: str
    about_link: str
    library_eyebrow: str
    library_title: str
    search_placeholder: str
    empty_state: str
    read_more: str
    article_kicker: str
    previous_label: str
    next_label: str
    breadcrumb_glossary: str
    breadcrumb_articles: str
    cta_title: str
    cta_copy: str
    cta_link: str
    cover_image: str
    cover_alt: str

    @property
    def articles_base(self) -> str:
        return f"{self.base}/articles"

    @property
    def alternate_code(self) -> str:
        return "en" if self.code == "zh" else "zh"

    @property
    def alternate_base(self) -> str:
        return "/en" if self.code == "zh" else "/zh"


LOCALES = {
    "zh": Locale(
        code="zh",
        html_lang="zh-CN",
        base="/zh",
        data_file=ARTICLES_DIR / "content.json",
        social_url=ZH_SOCIAL_URL,
        og_site_name="AllScale 支付知识库",
        glossary_label="术语手册",
        articles_label="专题文章",
        social_label="中文社媒 ↗",
        social_cta="关注 AllScale 中文社媒",
        language_label="Language",
        alternate_label="English",
        index_title="支付术语科普系列文章｜AllScale",
        index_description="AllScale 支付术语科普系列：从 Checkout、跨境清算到稳定币与全球支付牌照。",
        hero_eyebrow="Payments Education Series",
        hero_title="支付术语<em>科普系列</em>",
        hero_summary="从一次“立即支付”出发，把卡支付、跨境清算、稳定币与合规牌照讲清楚。每篇解决一个具体问题，持续更新。",
        facts=("16 篇专题", "60 页合集", "持续更新"),
        about_eyebrow="About The Series",
        about_title="从“看懂一个词”，走到“理解一条完整资金链路”",
        about_copy="术语手册适合快速查询，这套专题文章则负责解释来龙去脉。现有内容覆盖收银台、开票、拒付、卡支付角色、跨境汇款、稳定币、钱包托管和全球牌照。",
        about_link="关注中文社媒，获取后续更新 ↗",
        library_eyebrow="Article Library",
        library_title="全部文章",
        search_placeholder="搜索文章，例如 Checkout、KYC、稳定币",
        empty_state="没有找到匹配文章",
        read_more="阅读全文 →",
        article_kicker="AllScale 支付术语科普",
        previous_label="上一篇",
        next_label="下一篇",
        breadcrumb_glossary="术语手册",
        breadcrumb_articles="专题文章",
        cta_title="继续关注 AllScale 支付科普",
        cta_copy="后续文章和支付行业内容会在 AllScale 中文社媒同步发布。",
        cta_link="关注 @allscale_zh ↗",
        cover_image="/articles/assets/series-cover.webp",
        cover_alt="AllScale 支付术语科普系列文章完整合集封面",
    ),
    "en": Locale(
        code="en",
        html_lang="en",
        base="/en",
        data_file=ARTICLES_DIR / "content.en.json",
        social_url=EN_SOCIAL_URL,
        og_site_name="AllScale Payments Knowledge Base",
        glossary_label="Glossary",
        articles_label="Articles",
        social_label="AllScale ↗",
        social_cta="Follow AllScale",
        language_label="Language",
        alternate_label="中文",
        index_title="Payment Glossary Article Series | AllScale",
        index_description="AllScale Payment Glossary Series, covering checkout, cross-border settlement, stablecoins, compliance, and payment licenses.",
        hero_eyebrow="Payments Education Series",
        hero_title="Payment Glossary <em>Article Series</em>",
        hero_summary="A practical guide to card payments, cross-border settlement, stablecoins, compliance, wallets, and global payment licenses.",
        facts=("16 articles", "67-page anthology", "Continuously updated"),
        about_eyebrow="About The Series",
        about_title="From knowing a term to understanding the full money movement",
        about_copy="The glossary is built for quick lookup. This article series explains the why behind each term, from checkout and invoicing to stablecoins, custody, compliance, and global licensing.",
        about_link="Follow AllScale for updates ↗",
        library_eyebrow="Article Library",
        library_title="All Articles",
        search_placeholder="Search articles, e.g. Checkout, KYC, stablecoins",
        empty_state="No matching articles found",
        read_more="Read article →",
        article_kicker="AllScale Payment Glossary",
        previous_label="Previous",
        next_label="Next",
        breadcrumb_glossary="Glossary",
        breadcrumb_articles="Articles",
        cta_title="Keep learning with AllScale",
        cta_copy="Future articles and payment education updates will be published through AllScale channels.",
        cta_link="Follow AllScale ↗",
        cover_image="/articles/assets/en-series-cover.webp",
        cover_alt="AllScale Payment Glossary Series complete anthology cover",
    ),
}


GLOSSARY_SECTIONS = [
    "fund-flow",
    "card-acquiring",
    "trade-payments",
    "fx-cross-border",
    "crypto-payments",
    "crypto-card",
    "compliance",
    "licenses",
    "stablecoin-licenses",
    "institutional-roles",
    "transaction-lifecycle",
    "business-metrics",
]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def locale_url(locale: Locale, suffix: str = "") -> str:
    return SITE_URL + locale.base + suffix


def language_switch_url(locale: Locale, suffix: str = "") -> str:
    return locale.alternate_base + suffix


def site_header(locale: Locale, active: str = "articles", alternate_suffix: str = "/articles/") -> str:
    article_class = ' class="active"' if active == "articles" else ""
    glossary_class = ' class="active"' if active == "glossary" else ""
    return f"""<header class="site-header">
  <div class="site-header-inner">
    <a class="brand" href="{locale.base}/" aria-label="AllScale {esc(locale.glossary_label)}">
      <img src="/articles/assets/allscale-logo.png" alt="AllScale">
    </a>
    <nav class="site-nav" aria-label="Primary navigation">
      <a href="{locale.base}/"{glossary_class}>{esc(locale.glossary_label)}</a>
      <a href="{locale.articles_base}/"{article_class}>{esc(locale.articles_label)}</a>
      <a class="language-link" href="{language_switch_url(locale, alternate_suffix)}">{esc(locale.alternate_label)}</a>
      <a class="social-link" href="{locale.social_url}" target="_blank" rel="noreferrer">{esc(locale.social_label)}</a>
    </nav>
  </div>
</header>"""


def site_footer(locale: Locale) -> str:
    return f"""<footer class="site-footer">
  <div class="footer-inner">
    <span>© 2026 AllScale · Payments Knowledge Base</span>
    <a href="{locale.social_url}" target="_blank" rel="noreferrer">{esc(locale.social_cta)}</a>
  </div>
</footer>"""


def hreflang_links(path_suffix: str) -> str:
    return "\n".join(
        f'  <link rel="alternate" hreflang="{loc.code}" href="{esc(locale_url(loc, path_suffix))}">'
        for loc in LOCALES.values()
    )


def page_head(locale: Locale, title: str, description: str, canonical: str, image: str, path_suffix: str) -> str:
    return f"""<!doctype html>
<html lang="{locale.html_lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
{hreflang_links(path_suffix)}
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" href="/favicon-32x32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="{esc(locale.og_site_name)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(SITE_URL + image)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="/articles/styles.css">
  <script defer src="/analytics.js" data-allscale-analytics></script>
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


def redirect_page(destination: str, title: str = "Redirecting") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={esc(destination)}">
  <link rel="canonical" href="{esc(SITE_URL + destination)}">
  <title>{esc(title)}</title>
  <script>location.replace({json.dumps(destination)});</script>
</head>
<body><a href="{esc(destination)}">Continue</a></body>
</html>
"""


def build_index(locale: Locale, articles: list[dict[str, object]]) -> None:
    cards = []
    for article in articles:
        search_text = f"{article['title']} {article['summary']}".lower()
        cards.append(
            f"""<a class="article-card" href="{locale.articles_base}/{esc(article['slug'])}/" data-search="{esc(search_text)}">
  <img class="article-card-image" src="{esc(article['image'])}" alt="" loading="lazy">
  <span class="article-card-copy">
    <span class="series-number">{article['order']:02d}</span>
    <h3>{esc(article['title'])}</h3>
    <p>{esc(article['summary'])}</p>
    <span class="read-more">{esc(locale.read_more)}</span>
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
                "url": f"{locale_url(locale, f'/articles/{article['slug']}/')}",
            }
            for article in articles
        ],
    }
    structured_data = json.dumps(item_list, ensure_ascii=False).replace("</", "<\\/")
    facts = "".join(f"<span>{esc(fact)}</span>" for fact in locale.facts)
    canonical = locale_url(locale, "/articles/")
    page = f"""{page_head(locale, locale.index_title, locale.index_description, canonical, locale.cover_image, "/articles/")}
<body>
{site_header(locale, alternate_suffix="/articles/")}
<main>
  <section class="library-hero">
    <div class="page-shell">
      <div class="eyebrow">{esc(locale.hero_eyebrow)}</div>
      <h1>{locale.hero_title}</h1>
      <p class="hero-summary">{esc(locale.hero_summary)}</p>
      <div class="series-facts">{facts}</div>
    </div>
  </section>

  <div class="page-shell">
    <section class="series-intro">
      <img class="series-cover" src="{esc(locale.cover_image)}" alt="{esc(locale.cover_alt)}">
      <div class="series-copy">
        <div class="eyebrow">{esc(locale.about_eyebrow)}</div>
        <h2>{esc(locale.about_title)}</h2>
        <p>{esc(locale.about_copy)}</p>
        <a href="{locale.social_url}" target="_blank" rel="noreferrer">{esc(locale.about_link)}</a>
      </div>
    </section>

    <section class="article-library" aria-labelledby="article-list-title">
      <div class="library-heading">
        <div>
          <div class="eyebrow">{esc(locale.library_eyebrow)}</div>
          <h2 id="article-list-title">{esc(locale.library_title)}</h2>
        </div>
        <input class="article-search" type="search" placeholder="{esc(locale.search_placeholder)}" aria-label="{esc(locale.search_placeholder)}">
      </div>
      <div class="article-grid">{''.join(cards)}</div>
      <div class="empty-state">{esc(locale.empty_state)}</div>
    </section>
  </div>
</main>
{site_footer(locale)}
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
    output_dir = ROOT / locale.base.strip("/") / "articles"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(page, encoding="utf-8")


def build_article(locale: Locale, article: dict[str, object], previous: dict[str, object] | None, following: dict[str, object] | None) -> None:
    suffix = f"/articles/{article['slug']}/"
    canonical = locale_url(locale, suffix)
    nav_items = []
    if previous:
        nav_items.append(
            f"<a href=\"{locale.articles_base}/{esc(previous['slug'])}/\"><small>{esc(locale.previous_label)}</small><strong>{esc(previous['title'])}</strong></a>"
        )
    else:
        nav_items.append("<span></span>")
    if following:
        nav_items.append(
            f"<a href=\"{locale.articles_base}/{esc(following['slug'])}/\"><small>{esc(locale.next_label)}</small><strong>{esc(following['title'])}</strong></a>"
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
        "inLanguage": locale.html_lang,
    }
    structured_data = json.dumps(article_schema, ensure_ascii=False).replace("</", "<\\/")
    page = f"""{page_head(locale, f"{article['title']} | AllScale", article['summary'], canonical, article['image'], suffix)}
<body>
{site_header(locale, alternate_suffix=suffix)}
<main class="article-shell">
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="{locale.base}/">{esc(locale.breadcrumb_glossary)}</a><span>/</span><a href="{locale.articles_base}/">{esc(locale.breadcrumb_articles)}</a><span>/</span><span>{article['order']:02d}</span>
  </nav>
  <article>
    <header class="article-header">
      <div class="article-kicker">{esc(locale.article_kicker)} · {article['order']:02d}</div>
      <h1>{esc(article['title'])}</h1>
      <p class="article-deck">{esc(article['summary'])}</p>
    </header>
    <img class="article-hero-image" src="{esc(article['image'])}" alt="{esc(article['title'])}">
    <div class="article-body">{render_blocks(article['blocks'])}</div>
  </article>

  <section class="social-cta">
    <h2>{esc(locale.cta_title)}</h2>
    <p>{esc(locale.cta_copy)}</p>
    <a href="{locale.social_url}" target="_blank" rel="noreferrer">{esc(locale.cta_link)}</a>
  </section>
  <nav class="article-pagination" aria-label="Article pagination">{''.join(nav_items)}</nav>
</main>
{site_footer(locale)}
<script type="application/ld+json">{structured_data}</script>
</body>
</html>
"""
    output_dir = ROOT / locale.base.strip("/") / "articles" / str(article["slug"])
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(page, encoding="utf-8")


def build_locale(locale: Locale) -> list[dict[str, object]]:
    articles = json.loads(locale.data_file.read_text(encoding="utf-8"))
    build_index(locale, articles)
    for index, article in enumerate(articles):
        previous = articles[index - 1] if index > 0 else None
        following = articles[index + 1] if index + 1 < len(articles) else None
        build_article(locale, article, previous, following)
    return articles


def build_legacy_article_redirects(zh_articles: list[dict[str, object]]) -> None:
    (ARTICLES_DIR / "index.html").write_text(redirect_page("/zh/articles/", "Articles moved"), encoding="utf-8")
    for article in zh_articles:
        output_dir = ARTICLES_DIR / str(article["slug"])
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "index.html").write_text(
            redirect_page(f"/zh/articles/{article['slug']}/", "Article moved"),
            encoding="utf-8",
        )


def copy_glossary_routes() -> None:
    for locale in LOCALES.values():
        source = ROOT / locale.base.strip("/") / "index.html"
        if not source.exists():
            continue
        for section in GLOSSARY_SECTIONS:
            output_dir = ROOT / locale.base.strip("/") / "glossary" / section
            output_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, output_dir / "index.html")


def build_discovery_files(articles_by_locale: dict[str, list[dict[str, object]]]) -> None:
    urls = [f"{SITE_URL}/", f"{SITE_URL}/zh/", f"{SITE_URL}/en/"]
    for locale in LOCALES.values():
        urls.extend(f"{SITE_URL}{locale.base}/glossary/{section}/" for section in GLOSSARY_SECTIONS)
        urls.append(f"{SITE_URL}{locale.articles_base}/")
        urls.extend(f"{SITE_URL}{locale.articles_base}/{article['slug']}/" for article in articles_by_locale[locale.code])

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
    articles_by_locale = {code: build_locale(locale) for code, locale in LOCALES.items()}
    build_legacy_article_redirects(articles_by_locale["zh"])
    copy_glossary_routes()
    build_discovery_files(articles_by_locale)
    print(
        "Built "
        + ", ".join(f"{len(articles)} {code} articles" for code, articles in articles_by_locale.items())
        + " with bilingual indexes"
    )


if __name__ == "__main__":
    main()
