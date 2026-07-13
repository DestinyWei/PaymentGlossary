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

EN_VISUALS = {
    "fund": """
<div class="card" data-en-visual="fund">
  <div class="card-title">Payment movement: collection -> clearing -> settlement -> payout</div>
  <div class="chain">
    <div class="chain-node cn-gray">Customer pays</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-blue">COBO collection<br><small style="font-weight:400;font-size:10px">platform receives funds</small></div><div class="chain-arrow">-></div>
    <div class="chain-node cn-amber">Clearing<br><small style="font-weight:400;font-size:10px">fees, FX, net positions</small></div><div class="chain-arrow">-></div>
    <div class="chain-node cn-teal">Settlement<br><small style="font-weight:400;font-size:10px">money actually moves</small></div><div class="chain-arrow">-></div>
    <div class="chain-node cn-green">POBO payout</div>
  </div>
  <div class="case-box teal">
    <div class="case-label teal">Example: group treasury pool</div>
    Subsidiaries in Germany, France, and Poland collect into a UK treasury account, then pay suppliers centrally. Benefits: lower bank fees, centralized FX hedging, and real-time visibility into group cash.
  </div>
</div>
""",
    "card": """
<div class="card" data-en-visual="card">
  <div class="card-title">A $100 online card payment, step by step</div>
  <div class="step"><div class="step-num">1</div><div class="step-body"><strong>Card data enters checkout.</strong> The browser sends encrypted card data to the gateway.</div></div>
  <div class="step"><div class="step-num">2</div><div class="step-body"><strong>Tokenization.</strong> The gateway replaces raw PAN with a token and routes the auth request.</div></div>
  <div class="step"><div class="step-num">3</div><div class="step-body"><strong>Network routing.</strong> The acquirer sends the request through Visa/Mastercard to the issuer.</div></div>
  <div class="step"><div class="step-num">4</div><div class="step-body"><strong>Issuer decision.</strong> The issuer checks balance, CVV, fraud signals, and places a hold. No final settlement yet.</div></div>
  <div class="step"><div class="step-num green">5</div><div class="step-body"><strong>Capture, clearing, settlement.</strong> The merchant captures after fulfillment; the network clears and settles net funds, usually T+1/T+2.</div></div>
  <hr class="div">
  <div class="chain"><div class="chain-node cn-blue">MDR</div><div class="chain-arrow">=</div><div class="chain-node cn-pink">Interchange</div><div class="chain-arrow">+</div><div class="chain-node cn-purple">Scheme fee</div><div class="chain-arrow">+</div><div class="chain-node cn-teal">Acquirer markup</div></div>
</div>
""",
    "trade": """
<div class="card" data-en-visual="trade">
  <div class="card-title">Trade-payment instruments by risk allocation</div>
  <table class="tbl">
    <tbody><tr><th>Instrument</th><th>When buyer pays</th><th>Who carries risk</th><th>Typical use</th></tr>
    <tr><td><span class="badge badge-blue">LC</span> Letter of Credit</td><td>Bank pays when documents match</td><td>Bank-backed, lowest seller risk</td><td>Large first-time international deals</td></tr>
    <tr><td><span class="badge badge-teal">D/P</span> Documents against Payment</td><td>Buyer pays before receiving documents</td><td>Moderate seller protection</td><td>Medium-trust trade flows</td></tr>
    <tr><td><span class="badge badge-amber">D/A</span> Documents against Acceptance</td><td>Buyer accepts bill and pays later</td><td>Seller carries buyer credit risk</td><td>Long-term buyers with bargaining power</td></tr>
  </tbody></table>
  <div class="case-box amber">
    <div class="case-label amber">LC flow</div>
    Contract -> buyer asks issuing bank to open LC -> advising bank notifies seller -> seller ships goods -> documents are checked -> bank pays -> buyer reimburses bank and collects goods.
  </div>
</div>
""",
    "fx": """
<div class="card" data-en-visual="fx">
  <div class="card-title">Where cross-border cost hides</div>
  <div class="chain">
    <div class="chain-node cn-gray">Sender currency</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-amber">FX quote<br><small style="font-weight:400;font-size:10px">mid-market +/- spread</small></div><div class="chain-arrow">-></div>
    <div class="chain-node cn-blue">Correspondent chain</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-teal">Local rail</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-green">Beneficiary receives</div>
  </div>
  <div class="grid2">
    <div class="grid-card"><div class="label">Bank wire</div><div class="body">Costs can appear as transfer fees, intermediary deductions, FX spread, and delayed value date.</div></div>
    <div class="grid-card"><div class="label">Stablecoin rail</div><div class="body">The chain transfer can settle quickly, but on/off-ramp spread, liquidity, and compliance still determine final cost.</div></div>
  </div>
</div>
""",
    "crypto": """
<div class="card" data-en-visual="crypto">
  <div class="card-title">Stablecoin checkout lifecycle</div>
  <div class="step"><div class="step-num">1</div><div class="step-body"><strong>Payment request.</strong> Merchant creates an invoice, QR code, address, asset, network, and expiry window.</div></div>
  <div class="step"><div class="step-num">2</div><div class="step-body"><strong>Broadcast.</strong> Payer signs and submits the transaction from a wallet or exchange account.</div></div>
  <div class="step"><div class="step-num">3</div><div class="step-body"><strong>Detection.</strong> Payment provider monitors mempool and confirmations, then fires a webhook.</div></div>
  <div class="step"><div class="step-num green">4</div><div class="step-body"><strong>Settlement choice.</strong> Merchant keeps stablecoins, swaps to another asset, or off-ramps to fiat.</div></div>
  <table class="tbl">
    <tbody><tr><th>License trigger</th><th>Why it matters</th></tr>
    <tr><td>VASP / CASP</td><td>Custody, exchange, broker, transfer, or crypto-asset service activity.</td></tr>
    <tr><td>MSB / MTL / EMI</td><td>Fiat movement, money transmission, stored value, or e-money issuance.</td></tr>
  </tbody></table>
</div>
""",
    "ucard": """
<div class="card" data-en-visual="ucard">
  <div class="card-title">Crypto card spend flow, inside roughly 200ms</div>
  <div class="chain">
    <div class="chain-node cn-gray">Card tap</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-purple">Visa/MC auth</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-amber">Issuer checks crypto balance</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-teal">Real-time off-ramp</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-green">Merchant receives fiat</div>
  </div>
  <div class="grid2">
    <div class="grid-card"><div class="label">Pre-converted balance</div><div class="body">Crypto is converted to fiat before spending. Simpler UX and lower spend-time volatility.</div></div>
    <div class="grid-card"><div class="label">Real-time conversion</div><div class="body">Crypto remains crypto until authorization. More flexible, but depends on instant liquidity and risk controls.</div></div>
  </div>
</div>
""",
    "comp": """
<div class="card" data-en-visual="comp">
  <div class="card-title">Compliance pipeline for payment and crypto flows</div>
  <div class="chain">
    <div class="chain-node cn-blue">KYC / KYB</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-purple">Sanctions screening</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-amber">Transaction monitoring</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-red">Alert review</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-teal">SAR / STR filing</div>
  </div>
  <table class="tbl">
    <tbody><tr><th>Regulator / standard setter</th><th>Scope</th></tr>
    <tr><td>FinCEN / OFAC</td><td>US MSB registration, AML reporting, and sanctions enforcement.</td></tr>
    <tr><td>FATF</td><td>Global AML/CFT standards including Travel Rule for VASPs.</td></tr>
    <tr><td>MAS / SFC / FCA / EBA</td><td>Regional payment, e-money, virtual asset, and conduct supervision.</td></tr>
  </tbody></table>
</div>
""",
    "lic": """
<div class="card" data-en-visual="lic">
  <div class="card-title">World license map, simplified by operating region</div>
  <div class="diagram">
    <svg viewBox="0 0 760 320" role="img" aria-label="Simplified world license map">
      <rect width="760" height="320" fill="#F2F8F5"></rect>
      <ellipse cx="155" cy="125" rx="105" ry="58" fill="#CFE0F2" stroke="#2E6DA4"></ellipse>
      <ellipse cx="215" cy="225" rx="70" ry="46" fill="#D8D2F2" stroke="#5C4BB0"></ellipse>
      <ellipse cx="380" cy="108" rx="82" ry="48" fill="#BFE6D6" stroke="#0E7C6B"></ellipse>
      <ellipse cx="455" cy="170" rx="58" ry="36" fill="#EFD9AE" stroke="#8C5A11"></ellipse>
      <ellipse cx="430" cy="235" rx="72" ry="48" fill="#C9E0AE" stroke="#047857"></ellipse>
      <ellipse cx="590" cy="150" rx="125" ry="68" fill="#EFC6D4" stroke="#A6396A"></ellipse>
      <text x="155" y="116" text-anchor="middle" fill="#2E6DA4" font-size="15" font-weight="700">US / Canada</text>
      <text x="155" y="137" text-anchor="middle" fill="#2E6DA4" font-size="12">MSB · MTL · BitLicense</text>
      <text x="215" y="222" text-anchor="middle" fill="#5C4BB0" font-size="15" font-weight="700">LatAm</text>
      <text x="215" y="243" text-anchor="middle" fill="#5C4BB0" font-size="12">PSP · Pix</text>
      <text x="380" y="101" text-anchor="middle" fill="#0E7C6B" font-size="15" font-weight="700">Europe / UK</text>
      <text x="380" y="122" text-anchor="middle" fill="#0E7C6B" font-size="12">EMI · PI · MiCA</text>
      <text x="455" y="166" text-anchor="middle" fill="#8C5A11" font-size="15" font-weight="700">Middle East</text>
      <text x="455" y="187" text-anchor="middle" fill="#8C5A11" font-size="12">VARA · ADGM</text>
      <text x="430" y="232" text-anchor="middle" fill="#047857" font-size="15" font-weight="700">Africa</text>
      <text x="430" y="253" text-anchor="middle" fill="#047857" font-size="12">PSO · PSP</text>
      <text x="590" y="145" text-anchor="middle" fill="#A6396A" font-size="15" font-weight="700">APAC</text>
      <text x="590" y="166" text-anchor="middle" fill="#A6396A" font-size="12">MPI · VATP · SVF</text>
    </svg>
  </div>
  <div class="case-box teal"><div class="case-label teal">How to read it</div>Licensing is activity-based and jurisdiction-specific. The same product may need payment, e-money, money transmission, virtual asset, custody, and FX permissions in different markets.</div>
</div>
""",
    "stable": """
<div class="card" data-en-visual="stable">
  <div class="card-title">Stablecoin license and trust stack</div>
  <div class="chain"><div class="chain-node cn-blue">Issuer</div><div class="chain-arrow">-></div><div class="chain-node cn-teal">Segregated reserve</div><div class="chain-arrow">-></div><div class="chain-node cn-amber">Attestation</div><div class="chain-arrow">-></div><div class="chain-node cn-purple">Redemption right</div><div class="chain-arrow">-></div><div class="chain-node cn-green">Payment utility</div></div>
  <table class="tbl">
    <tbody><tr><th>Project type</th><th>Typical compliance signal</th><th>Why users care</th></tr>
    <tr><td>USDC-style issuer</td><td>US state licenses, money service registration, reserve attestations</td><td>Institutional trust and redemption confidence.</td></tr>
    <tr><td>MiCA EMT issuer</td><td>EU e-money token authorization</td><td>EU market access and clearer consumer rights.</td></tr>
    <tr><td>Payment platform</td><td>Payment/e-money licenses plus crypto permissions</td><td>Can combine checkout, settlement, conversion, and payout.</td></tr>
  </tbody></table>
</div>
""",
    "roles": """
<div class="card" data-en-visual="roles">
  <div class="card-title">Institution role map</div>
  <div class="diagram">
    <svg viewBox="0 0 700 360" role="img" aria-label="Payment institution role map">
      <defs><marker id="arrow-en" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5"/></marker></defs>
      <rect width="700" height="360" fill="#F2F8F5"></rect>
      <g fill="#FFFFFF" stroke="#C5DDD4" stroke-width="1">
        <rect x="260" y="24" width="180" height="48" rx="8"></rect>
        <rect x="250" y="102" width="200" height="54" rx="8"></rect>
        <rect x="45" y="205" width="150" height="54" rx="8"></rect>
        <rect x="275" y="205" width="150" height="54" rx="8"></rect>
        <rect x="505" y="205" width="150" height="54" rx="8"></rect>
        <rect x="250" y="292" width="200" height="44" rx="8"></rect>
      </g>
      <g fill="none" stroke="#83968F" marker-end="url(#arrow-en)">
        <path d="M350 72V102"></path><path d="M250 129H195"></path><path d="M450 129H505"></path>
        <path d="M120 205L300 156"></path><path d="M350 156V205"></path><path d="M580 205L400 156"></path><path d="M350 259V292"></path>
      </g>
      <g font-family="Inter, sans-serif" text-anchor="middle" font-size="13" fill="#0C3124" font-weight="700">
        <text x="350" y="53">Cardholder / Buyer</text><text x="350" y="128">Gateway</text><text x="350" y="146" font-size="11" fill="#83968F" font-weight="500">encrypt · tokenize · route</text>
        <text x="120" y="230">PSP / PayFac</text><text x="350" y="230">Acquirer / MoR</text><text x="580" y="230">Processor</text><text x="350" y="318">Network / Issuer</text>
      </g>
    </svg>
  </div>
  <div class="case-box"><div class="case-label">Risk ownership</div>The entity touching the customer is not always the regulated principal. Contracts, sponsorship, agency status, and outsourcing rules decide who owns settlement, chargeback, safeguarding, and AML risk.</div>
</div>
""",
    "txlife": """
<div class="card" data-en-visual="txlife">
  <div class="card-title">Transaction lifecycle overview</div>
  <div class="chain">
    <div class="chain-node cn-gray">Auth</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-blue">Capture</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-blue">Clearing</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-teal">Settlement</div><div class="chain-arrow">-></div>
    <div class="chain-node cn-green">Payout</div><div class="chain-arrow">/</div>
    <div class="chain-node cn-red">Refund or dispute</div>
  </div>
  <div class="grid2">
    <div class="grid-card" style="border-left:3px solid #8C5A11"><div class="label" style="color:var(--amber)">Void</div><div class="body">Before capture: release the hold, no new money movement, usually no fee.</div></div>
    <div class="grid-card" style="border-left:3px solid #C13A2D"><div class="label" style="color:var(--red)">Refund</div><div class="body">After settlement: reverse value back to the payer, usually slower and costlier.</div></div>
  </div>
</div>
""",
    "biz": """
<div class="card" data-en-visual="biz">
  <div class="card-title">Core payment-business math</div>
  <div class="chain">
    <div class="chain-node cn-blue">TPV</div><div class="chain-arrow">x</div>
    <div class="chain-node cn-amber">Take rate</div><div class="chain-arrow">=</div>
    <div class="chain-node cn-teal">Gross revenue</div><div class="chain-arrow">-</div>
    <div class="chain-node cn-purple">Pass-through costs</div><div class="chain-arrow">=</div>
    <div class="chain-node cn-green">Net revenue</div>
  </div>
  <div class="grid2">
    <div class="grid-card"><div class="label">GMV</div><div class="body">Total commerce value on a platform, including transactions not processed by the platform's own payment stack.</div></div>
    <div class="grid-card"><div class="label">TPV</div><div class="body">Payment value actually processed. Payment-company valuation usually starts from TPV, take rate, and margin quality.</div></div>
  </div>
</div>
""",
}


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
        return enrich_sections(main.group(1).strip())

    sections = []
    for match in re.finditer(r'<section class="section[^"]*" id="([^"]+)">.*?</section>', html, re.S):
        source_id = match.group(1)
        if source_id not in SECTION_ID_MAP:
            continue
        sections.append(transform_section(match.group(0), source_id))
    if len(sections) != len(SECTION_ID_MAP):
        raise RuntimeError(f"Expected {len(SECTION_ID_MAP)} English sections, found {len(sections)}")
    return enrich_sections("\n\n".join(sections))


def enrich_sections(main_html: str) -> str:
    for section_id, visual in EN_VISUALS.items():
        marker = f'data-en-visual="{section_id}"'
        section_match = re.search(
            r'(<div id="sec-' + re.escape(section_id) + r'" class="section[^>]*>)(.*?)(?=\n<div id="sec-|</main>|$)',
            main_html,
            re.S,
        )
        if not section_match or marker in section_match.group(2):
            continue
        section = section_match.group(0)
        section = re.sub(
            r'(<p class="section-desc">.*?</p>)',
            r'\1\n' + visual.strip(),
            section,
            count=1,
            flags=re.S,
        )
        main_html = main_html[:section_match.start()] + section + main_html[section_match.end():]
    return main_html


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
