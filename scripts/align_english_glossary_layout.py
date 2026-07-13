#!/usr/bin/env python3
"""Rebuild the English glossary with the same visual system as the Chinese page."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ZH_INDEX = ROOT / "zh" / "index.html"
EN_INDEX = ROOT / "en" / "index.html"

SECTION_ID_MAP = {
    "fund-flow": "fund",
    "card-acquiring": "card",
    "trade-payments": "trade",
    "fx-cross-border": "fx",
    "crypto-payments": "crypto",
    "crypto-card": "ucard",
    "compliance": "comp",
    "licenses": "lic",
    "stablecoin-licenses": "stable",
    "institutional-roles": "roles",
    "transaction-lifecycle": "txlife",
    "business-metrics": "biz",
}

NAV_GROUPS = [
    ("Core Architecture", [
        ("fund", "Fund Flow", "#2E6DA4"),
        ("card", "Card Acquiring", "#2E6DA4"),
        ("trade", "Trade Payments", "#2E6DA4"),
        ("fx", "FX & Cross-Border", "#2E6DA4"),
    ]),
    ("Crypto", [
        ("crypto", "Crypto Payments", "#0E7C6B"),
        ("ucard", "Crypto Cards", "#0E7C6B"),
    ]),
    ("Compliance & Regulation", [
        ("comp", "Compliance", "#A6396A"),
        ("lic", "License Map", "#A6396A"),
        ("stable", "Stablecoin Licenses", "#A6396A"),
    ]),
    ("Institutions & Operations", [
        ("roles", "Institutional Roles", "#8C5A11"),
        ("txlife", "Transaction Lifecycle", "#8C5A11"),
        ("biz", "Business Metrics", "#8C5A11"),
    ]),
]


def extract_chinese_design_css() -> str:
    zh = ZH_INDEX.read_text()
    template = json.loads(re.search(
        r'<script type="__bundler/template">\s*(.*?)\s*</script>',
        zh,
        re.S,
    ).group(1))
    css_blocks = re.findall(r"<style>(.*?)</style>", template, re.S)
    css = "\n\n".join(css_blocks)
    css = re.sub(r"@font-face\s*\{.*?\}\s*", "", css, flags=re.S)
    css = css.replace(
        "--serif: 'Playfair Display', Georgia, serif;",
        "--serif: Georgia, 'Times New Roman', serif;",
    ).replace(
        "--sans: 'Archivo', -apple-system, system-ui, sans-serif;",
        "--sans: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;",
    ).replace(
        "--mono: 'DM Mono', ui-monospace, monospace;",
        "--mono: 'SFMono-Regular', Consolas, ui-monospace, monospace;",
    )
    css += """

.header-top { position: relative; }
.glossary-site-links {
  display: flex;
  align-items: center;
  gap: 8px;
  width: auto;
  margin-left: auto;
}
.glossary-site-links a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: auto;
  min-height: 40px;
  border: 1px solid var(--border2);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text);
  padding: 8px 14px;
  text-decoration: none;
  font: 13px/1.2 var(--sans);
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(12,49,36,0.06);
}
.glossary-site-links a:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-1px); }
.glossary-site-links a:first-child {
  border-color: var(--accent);
  background: var(--accent);
  color: #fff;
  box-shadow: 0 7px 18px rgba(0,152,89,0.22);
}
.glossary-search { position: relative; max-width: 560px; margin-top: 22px; }
.glossary-search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 44px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  box-shadow: var(--shadow);
  padding: 0 14px;
}
.glossary-search-icon { color: var(--accent); font-family: var(--mono); font-size: 18px; line-height: 1; }
.glossary-search input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text);
  font: 14px/1.4 var(--sans);
}
.glossary-search input::placeholder { color: var(--text3); }
.glossary-search-results {
  display: none;
  position: absolute;
  z-index: 30;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  box-shadow: 0 12px 34px rgba(12,49,36,0.12);
}
.glossary-search-results.open { display: block; }
.glossary-search-result {
  display: grid;
  gap: 3px;
  width: 100%;
  border: 0;
  border-bottom: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  cursor: pointer;
  padding: 11px 14px;
  text-align: left;
  font: 13px/1.35 var(--sans);
}
.glossary-search-result:hover,
.glossary-search-result:focus { background: var(--bg2); outline: 0; }
.glossary-search-result small { color: var(--text2); font: 11px/1.3 var(--mono); }
.glossary-search-empty { padding: 12px 14px; color: var(--text2); font: 13px/1.4 var(--sans); }
.glossary-hit { animation: glossary-pulse 1.6s ease; }
@keyframes glossary-pulse {
  0%, 100% { box-shadow: var(--shadow); }
  25% { box-shadow: 0 0 0 3px rgba(0,152,89,0.18), var(--shadow); }
}
@media (max-width: 720px) {
  .glossary-search { max-width: none; }
  .header-top-label, .header-top-div { display: none; }
  .glossary-site-links { gap: 5px; }
  .glossary-site-links a { min-height: 36px; padding: 7px 11px; font-size: 12px; }
  .glossary-site-links a:last-child { display: none; }
}
"""
    return css


def transform_section(section_html: str, source_id: str) -> str:
    target_id = SECTION_ID_MAP[source_id]
    section_html = re.sub(
        r'<section class="section([^"]*)" id="' + re.escape(source_id) + r'">',
        lambda m: f'<div id="sec-{target_id}" class="section{" active" if "active" in m.group(1) else ""}">',
        section_html,
    )
    section_html = section_html.replace("</section>", "</div>")
    section_html = re.sub(r"<h2>(.*?)</h2>", r'<h2 class="section-title">\1</h2>', section_html, flags=re.S)
    section_html = re.sub(r"<h3>(.*?)</h3>", r'<div class="card-title">\1</div>', section_html, flags=re.S)
    section_html = section_html.replace('class="grid"', 'class="grid2"')
    section_html = re.sub(
        r'<div class="term"><b>(.*?)</b><span>(.*?)</span></div>',
        r'<div class="term-item"><div class="term-abbr">\1</div><div class="term-zh">\2</div></div>',
        section_html,
        flags=re.S,
    )
    section_html = re.sub(r'<p class="note">(.*?)</p>', r'<div class="case-box">\1</div>', section_html, flags=re.S)
    return section_html


def extract_english_sections() -> str:
    html = EN_INDEX.read_text()

    if 'id="sec-fund"' in html:
        main = re.search(r"<main>\s*(.*?)\s*</main>", html, re.S)
        if not main:
            raise RuntimeError("Could not find aligned English <main> content")
        return main.group(1).strip()

    sections = []
    for match in re.finditer(r'<section class="section[^"]*" id="([^"]+)">.*?</section>', html, re.S):
        source_id = match.group(1)
        if source_id not in SECTION_ID_MAP:
            continue
        sections.append(transform_section(match.group(0), source_id))
    if len(sections) != len(SECTION_ID_MAP):
        raise RuntimeError(f"Expected {len(SECTION_ID_MAP)} English sections, found {len(sections)}")
    return "\n\n".join(sections)


def build_nav() -> str:
    parts = ['<nav id="sidebar">']
    for label, links in NAV_GROUPS:
        parts.append(f'  <div class="nav-section-label">{escape(label)}</div>')
        for section_id, title, color in links:
            active = ' class="active"' if section_id == "fund" else ""
            parts.append(
                f'  <a href="#" onclick="show(\'{section_id}\')" {active}>'
                f'<span class="nav-dot" style="background:{color}"></span>{escape(title)}</a>'
            )
    parts.append("</nav>")
    return "\n".join(parts)


def build_script() -> str:
    slug_by_id = {
        "fund": "fund-flow",
        "card": "card-acquiring",
        "trade": "trade-payments",
        "fx": "fx-cross-border",
        "crypto": "crypto-payments",
        "ucard": "crypto-card",
        "comp": "compliance",
        "lic": "licenses",
        "stable": "stablecoin-licenses",
        "roles": "institutional-roles",
        "txlife": "transaction-lifecycle",
        "biz": "business-metrics",
    }
    return f"""
<script>
const slugById = {json.dumps(slug_by_id, ensure_ascii=False)};
const idBySlug = Object.fromEntries(Object.entries(slugById).map(([id, slug]) => [slug, id]));
const localeBase = '/en';
const sections = Array.from(document.querySelectorAll('.section[id^="sec-"]'));
const navLinks = Array.from(document.querySelectorAll('#sidebar a'));
const searchInput = document.querySelector('.glossary-search input');
const searchResults = document.querySelector('.glossary-search-results');
const anchorBySlug = {{}};
const searchItems = [];
const slugCounts = {{}};

function normalize(text) {{
  return (text || '').toLowerCase().replace(/\\s+/g, ' ').trim();
}}
function escapeHtml(text) {{
  return String(text).replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
}}
function readableTitle(el, sectionTitle) {{
  if (el.classList.contains('term-item')) {{
    return [el.querySelector('.term-abbr'), el.querySelector('.term-en'), el.querySelector('.term-zh')]
      .map(node => node ? node.textContent.trim() : '').filter(Boolean).join(' · ');
  }}
  const titleNode = el.querySelector('.card-title, .label, .level-head, .case-label, .section-title');
  return titleNode ? titleNode.textContent.replace(/\\s+/g, ' ').trim() : sectionTitle;
}}
function makeSlug(text, fallback) {{
  const base = (text || fallback).toLowerCase().replace(/&/g, ' and ').replace(/\\+/g, ' plus ')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 48) || fallback;
  slugCounts[base] = (slugCounts[base] || 0) + 1;
  return slugCounts[base] === 1 ? base : base + '-' + slugCounts[base];
}}
function sectionUrl(sectionSlug, targetSlug = '') {{
  return localeBase + '/glossary/' + sectionSlug + '/' + (targetSlug ? '#' + encodeURIComponent(targetSlug) : '');
}}
function setActiveSection(id, options = {{}}) {{
  const section = document.getElementById('sec-' + id);
  if (!section) return false;
  sections.forEach(item => item.classList.remove('active'));
  navLinks.forEach(item => item.classList.remove('active'));
  section.classList.add('active');
  const link = navLinks.find(item => item.dataset.sectionId === id);
  if (link) link.classList.add('active');
  const slug = slugById[id] || id;
  const targetSlug = options.target && options.target !== section ? options.target.dataset.glossaryAnchor : '';
  if (options.updateUrl !== false) history.pushState(null, '', sectionUrl(slug, targetSlug));
  const target = options.target || section;
  if (options.scroll !== false) target.scrollIntoView({{ behavior: options.instant ? 'auto' : 'smooth', block: 'start' }});
  if (options.target) {{
    options.target.classList.remove('glossary-hit');
    void options.target.offsetWidth;
    options.target.classList.add('glossary-hit');
    window.setTimeout(() => options.target.classList.remove('glossary-hit'), 1600);
  }}
  return true;
}}
navLinks.forEach(link => {{
  const raw = link.getAttribute('onclick') || '';
  const match = raw.match(/show\\('([^']+)'\\)/);
  if (!match) return;
  const id = match[1];
  link.dataset.sectionId = id;
  link.href = sectionUrl(slugById[id] || id);
  link.removeAttribute('onclick');
  link.addEventListener('click', event => {{
    event.preventDefault();
    setActiveSection(id, {{ updateUrl: true }});
  }});
}});
sections.forEach(section => {{
  const sectionId = section.id.replace(/^sec-/, '');
  const sectionSlug = slugById[sectionId] || sectionId;
  const sectionTitle = readableTitle(section, sectionId);
  const sectionAnchor = makeSlug(sectionTitle, sectionSlug);
  section.dataset.glossaryAnchor = sectionAnchor;
  anchorBySlug[sectionSlug] = section;
  searchItems.push({{ title: sectionTitle, context: 'Section', text: normalize(section.innerText), sectionId, sectionSlug, targetSlug: sectionAnchor, target: section }});
  Array.from(section.querySelectorAll('.term-item, .grid-card, .level-card, .card')).forEach((el, index) => {{
    const title = readableTitle(el, sectionTitle);
    if (!title || title === sectionTitle) return;
    const targetSlug = makeSlug(title, sectionSlug + '-' + index);
    el.dataset.glossaryAnchor = targetSlug;
    anchorBySlug[sectionSlug + '/' + targetSlug] = el;
    searchItems.push({{ title, context: sectionTitle, text: normalize(el.innerText), sectionId, sectionSlug, targetSlug, target: el }});
  }});
}});
window.show = function(id) {{ return setActiveSection(id, {{ updateUrl: true }}); }};
function routeFromLocation(options = {{}}) {{
  const parts = window.location.pathname.split('/').filter(Boolean);
  const glossaryIndex = parts.indexOf('glossary');
  const pathSlug = glossaryIndex >= 0 ? parts[glossaryIndex + 1] : '';
  const hashSlug = decodeURIComponent(window.location.hash.replace(/^#/, ''));
  const sectionId = idBySlug[pathSlug] || 'fund';
  const sectionSlug = slugById[sectionId] || sectionId;
  const target = hashSlug ? anchorBySlug[sectionSlug + '/' + hashSlug] : null;
  setActiveSection(sectionId, {{ target, updateUrl: false, scroll: !!target, instant: options.instant }});
}}
function findMatches(query) {{
  const q = normalize(query);
  if (!q) return [];
  return searchItems.map(item => {{
    const title = normalize(item.title);
    let score = 0;
    if (title === q) score += 120;
    if (title.startsWith(q)) score += 80;
    if (title.includes(q)) score += 55;
    if (item.text.includes(q)) score += 20;
    return {{ ...item, score }};
  }}).filter(item => item.score > 0).sort((a, b) => b.score - a.score || a.title.length - b.title.length).slice(0, 8);
}}
function renderSearch(matches) {{
  if (!searchInput.value.trim()) {{
    searchResults.innerHTML = '';
    searchResults.classList.remove('open');
    return;
  }}
  if (!matches.length) {{
    searchResults.innerHTML = '<div class="glossary-search-empty">No matching terms found</div>';
    searchResults.classList.add('open');
    return;
  }}
  searchResults.innerHTML = matches.map((item, index) => `
    <button type="button" class="glossary-search-result" data-index="${{index}}">
      <span>${{escapeHtml(item.title)}}</span>
      <small>${{escapeHtml(item.context)}}</small>
    </button>`).join('');
  searchResults.classList.add('open');
}}
let activeMatches = [];
function jump(item) {{
  if (!item) return;
  searchInput.value = item.title;
  searchResults.classList.remove('open');
  setActiveSection(item.sectionId, {{ target: item.target, updateUrl: true }});
}}
document.querySelector('.glossary-search').addEventListener('submit', event => {{
  event.preventDefault();
  jump(activeMatches[0]);
}});
searchInput.addEventListener('input', () => {{
  activeMatches = findMatches(searchInput.value);
  renderSearch(activeMatches);
}});
searchInput.addEventListener('focus', () => {{
  activeMatches = findMatches(searchInput.value);
  renderSearch(activeMatches);
}});
searchResults.addEventListener('click', event => {{
  const button = event.target.closest('.glossary-search-result');
  if (button) jump(activeMatches[Number(button.dataset.index)]);
}});
document.addEventListener('click', event => {{
  if (!document.querySelector('.glossary-search').contains(event.target)) searchResults.classList.remove('open');
}});
routeFromLocation({{ instant: true }});
window.addEventListener('popstate', () => routeFromLocation({{ instant: true }}));
window.addEventListener('hashchange', () => routeFromLocation({{ instant: true }}));
</script>
"""


def build_html() -> str:
    css = extract_chinese_design_css()
    sections = extract_english_sections()
    nav = build_nav()
    script = build_script()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Payment Industry Glossary — AllScale</title>
  <meta name="description" content="AllScale English payment glossary covering fund flows, card acquiring, trade payments, cross-border FX, crypto payments, compliance, licensing, operating roles, transaction lifecycles, and payment metrics.">
  <link rel="canonical" href="https://payment.0xhowe.top/en/">
  <link rel="alternate" hreflang="en" href="https://payment.0xhowe.top/en/">
  <link rel="alternate" hreflang="zh" href="https://payment.0xhowe.top/zh/">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" type="image/png" href="/favicon-32x32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <script defer src="/analytics.js" data-allscale-analytics></script>
  <style>
{css}
  </style>
</head>
<body>
<header>
  <div class="header-top">
    <img class="header-logo" src="/articles/assets/allscale-logo.png" alt="AllScale">
    <div class="header-top-div"></div>
    <span class="header-top-label">Checkout · Knowledge Base</span>
    <div class="glossary-site-links" role="navigation" aria-label="Site navigation">
      <a href="/en/articles/">Articles →</a>
      <a href="/zh/">中文</a>
      <a href="https://x.com/allscaleio" target="_blank" rel="noreferrer">AllScale ↗</a>
    </div>
  </div>
  <div class="header-eyebrow">Payments Reference</div>
  <h1>Payment Industry <em>Glossary</em></h1>
  <div class="header-meta">
    <span class="header-badge">v3.0 · March 2026</span>
    <span class="header-badge">12 sections · 200+ terms</span>
    <span class="header-badge">For Crypto operators</span>
  </div>
  <form class="glossary-search" role="search">
    <div class="glossary-search-box">
      <span class="glossary-search-icon">⌕</span>
      <input type="search" autocomplete="off" spellcheck="false" placeholder="Search terms, e.g. TPV, COBO, PCI, stablecoin">
    </div>
    <div class="glossary-search-results" aria-live="polite"></div>
  </form>
</header>

<div class="layout">
{nav}
<main>
{sections}
</main>
</div>
{script}
</body>
</html>
"""


def main() -> None:
    EN_INDEX.write_text(build_html())
    print("Aligned English glossary layout with Chinese visual system")


if __name__ == "__main__":
    main()
