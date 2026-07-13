#!/usr/bin/env python3
"""Rebuild the English glossary with the same visual system as the Chinese page."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

from english_glossary_content import build_english_sections


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
.header-logo-link { display: inline-flex; align-items: center; }
.header-logo-link:focus-visible { outline: 2px solid var(--accent); outline-offset: 4px; border-radius: 6px; }
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
.map-leg { cursor: pointer; border-radius: 999px; padding: 2px 6px; }
.map-leg > span { display: inline-block; width: 9px; height: 9px; border-radius: 999px; flex-shrink: 0; }
.map-leg:hover,
.map-leg.active { background: var(--bg2); }
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
    return build_english_sections()


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


def build_license_map_script() -> str:
    return """
<script>
const LICENSE_REGION_META = {
  americas: { name: 'US / Canada', color: '#2E6DA4',
    items: [
      { n: 'MTL', d: 'Money Transmitter License — state-by-state approval across 48 states + DC, typically 2-3 years and multi-million cost.' },
      { n: 'MSB', d: 'Money Services Business — FinCEN federal registration, usually completed in about 14 days, but still requires state MTL coverage.' },
      { n: 'BitLicense', d: 'NYDFS crypto license — one of the strictest US crypto approvals, with heavy legal, compliance, and review burden.' },
      { n: 'National Bank Charter', d: 'OCC federal bank charter — can reduce state-by-state money transmission exposure, but the threshold is extremely high.' },
      { n: 'FINTRAC MSB', d: 'Canada money services business registration — comparatively accessible, with ongoing AML reporting obligations.' },
    ]
  },
  latam: { name: 'Latin America', color: '#5C4BB0',
    items: [
      { n: 'Brazil PSP License', d: 'BCB payment service provider framework; open banking and Pix real-time payments have become a global reference model.' },
      { n: 'Mexico PSSP', d: 'Payment Service Provider / Institution under the 2018 Fintech Law framework, a key digital-payment license in Latin America.' },
      { n: 'Regional PSP', d: 'Argentina, Colombia, Chile, and others regulate PSP activity through local central-bank frameworks with fast-growing demand.' },
    ]
  },
  europe: { name: 'Europe / UK', color: '#0E7C6B',
    items: [
      { n: 'EMI', d: 'Electronic Money Institution — one EU license can passport across 27 member states; Lithuania is a common application hub.' },
      { n: 'PI', d: 'Payment Institution — payment services only, lower capital requirement than EMI, and no stored-value issuance.' },
      { n: 'Small EMI / PI', d: 'Simplified low-volume regimes in some markets, useful for early-stage market validation.' },
      { n: 'AISP / PISP', d: 'PSD2 account information and payment initiation permissions with the lowest payment-regulatory threshold.' },
      { n: 'MiCA CASP', d: 'Crypto-Asset Service Provider authorization under MiCA, creating an EU-level crypto regulatory passport.' },
      { n: 'UK FCA E-money', d: 'Post-Brexit UK e-money permission is separate from the EU passport and is required for UK coverage.' },
    ]
  },
  apac: { name: 'APAC', color: '#A6396A',
    items: [
      { n: 'MPI + DPT', d: 'Singapore MAS Major Payment Institution plus Digital Payment Token permissions; no payment-volume cap and an Asian benchmark.' },
      { n: 'VATP', d: 'Hong Kong SFC Virtual Asset Trading Platform regime, effective from June 2023 with custody and capital requirements.' },
      { n: 'SVF', d: 'Hong Kong HKMA Stored Value Facility license; the same category behind Octopus and Alipay HK and a stablecoin prerequisite.' },
      { n: 'MSO', d: 'Hong Kong Customs Money Service Operator license for money changing and remittance activity.' },
      { n: 'JFSA', d: 'Japan crypto-asset exchange registration under the Financial Services Agency; mature but compliance-heavy.' },
      { n: 'AUSTRAC', d: 'Australia digital currency exchange provider registration under the FATF-style AML framework.' },
      { n: 'SEA PSP', d: 'Indonesia OJK, Philippines BSP, Thailand BOT, Vietnam SBV and others regulate PSP activity locally, often with foreign ownership limits.' },
    ]
  },
  me: { name: 'Middle East', color: '#8C5A11',
    items: [
      { n: 'Dubai VARA VASP', d: 'Dubai Virtual Assets Regulatory Authority license, established in 2022 and relatively friendly to crypto operators.' },
      { n: 'ADGM FSRA', d: 'Abu Dhabi Global Market Financial Services Regulatory Authority framework, favored by institutional Web3 businesses and funds.' },
      { n: 'CBUAE SVF + RPP', d: 'UAE Central Bank stored value and retail payment service permissions for wallets and payment gateways.' },
    ]
  },
  africa: { name: 'Africa', color: '#047857',
    items: [
      { n: 'Nigeria PSO', d: 'Central Bank of Nigeria Payment Service Operator regime; key market for Flutterwave, Paystack, and regional payment growth.' },
      { n: 'Kenya PSP', d: 'Central Bank of Kenya payment service provider framework; M-Pesa birthplace and a leading mobile-money market.' },
      { n: 'South Africa EMI', d: 'South African Reserve Bank framework in one of Africa’s most mature financial markets, often compared with European e-money models.' },
    ]
  }
};

const LICENSE_COUNTRY_REGION = {
  840:'americas', 124:'americas',
  484:'latam', 76:'latam', 32:'latam', 152:'latam', 170:'latam', 604:'latam', 858:'latam', 862:'latam', 600:'latam', 328:'latam', 740:'latam', 531:'latam', 630:'latam',
  276:'europe', 250:'europe', 826:'europe', 380:'europe', 724:'europe', 620:'europe', 528:'europe', 56:'europe', 40:'europe', 756:'europe', 578:'europe', 752:'europe', 208:'europe', 246:'europe', 233:'europe', 428:'europe', 440:'europe', 616:'europe', 203:'europe', 703:'europe', 348:'europe', 642:'europe', 100:'europe', 300:'europe', 191:'europe', 705:'europe', 372:'europe', 352:'europe', 470:'europe', 442:'europe', 196:'europe', 112:'europe', 804:'europe', 498:'europe', 688:'europe', 807:'europe', 8:'europe',
  702:'apac', 344:'apac', 392:'apac', 36:'apac', 410:'apac', 356:'apac', 360:'apac', 764:'apac', 704:'apac', 458:'apac', 608:'apac', 50:'apac', 144:'apac', 524:'apac', 104:'apac', 116:'apac', 418:'apac', 496:'apac', 887:'apac', 586:'apac', 64:'apac',
  682:'me', 784:'me', 512:'me', 634:'me', 414:'me', 368:'me', 400:'me', 376:'me',
  566:'africa', 404:'africa', 710:'africa', 818:'africa', 288:'africa', 231:'africa', 716:'africa', 504:'africa', 12:'africa', 686:'africa', 332:'africa', 466:'africa', 120:'africa', 24:'africa', 516:'africa', 508:'africa', 800:'africa', 834:'africa', 894:'africa', 426:'africa', 748:'africa', 140:'africa', 646:'africa', 108:'africa', 270:'africa', 324:'africa', 384:'africa', 204:'africa', 854:'africa', 562:'africa', 768:'africa', 174:'africa',
};

const LICENSE_REGION_FILL = {
  americas:'#CFE0F2', latam:'#D8D2F2', europe:'#BFE6D6',
  apac:'#EFC6D4', me:'#EFD9AE', africa:'#C9E0AE'
};
const LICENSE_REGION_HOVER = {
  americas:'#2E6DA4', latam:'#5C4BB0', europe:'#0E7C6B',
  apac:'#A6396A', me:'#8C5A11', africa:'#047857'
};

let licenseCurrentRegion = null;
let licenseMapSvg = null;

async function initEnglishLicenseMap() {
  const loading = document.getElementById('loading-map');
  const mapEl = document.getElementById('world-map');
  if (!loading || !mapEl) return;
  if (!window.d3 || !window.topojson) {
    loading.textContent = 'Map libraries failed to load. Please refresh the page.';
    return;
  }
  try {
    const atlasUrl = (window.__resources && window.__resources.worldAtlas) || 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json';
    const world = await d3.json(atlasUrl);
    loading.style.display = 'none';
    mapEl.style.display = 'block';
    licenseMapSvg = d3.select('#world-map');
    licenseMapSvg.selectAll('*').remove();
    const projection = d3.geoNaturalEarth1().scale(153).translate([480, 250]);
    const pathGen = d3.geoPath().projection(projection);

    licenseMapSvg.append('rect').attr('width', 960).attr('height', 500).attr('fill', 'var(--bg2)');
    licenseMapSvg.append('path').datum({ type: 'Sphere' }).attr('d', pathGen).attr('fill', '#DCEAF2').attr('opacity', '0.5');
    licenseMapSvg.append('path').datum(d3.geoGraticule()()).attr('d', pathGen).attr('fill', 'none').attr('stroke', 'rgba(0,0,0,0.06)').attr('stroke-width', '0.3');

    const countries = topojson.feature(world, world.objects.countries);
    licenseMapSvg.selectAll('.country')
      .data(countries.features)
      .enter().append('path')
      .attr('class', 'country')
      .classed('clickable', d => !!LICENSE_COUNTRY_REGION[+d.id])
      .attr('d', pathGen)
      .attr('fill', d => {
        const region = LICENSE_COUNTRY_REGION[+d.id];
        return region ? LICENSE_REGION_FILL[region] : 'var(--bg3)';
      })
      .on('click', function(event, d) {
        const region = LICENSE_COUNTRY_REGION[+d.id];
        if (region) highlightEnglishLicenseRegion(region);
      })
      .on('mouseover', function(event, d) {
        const region = LICENSE_COUNTRY_REGION[+d.id];
        if (region) d3.select(this).attr('fill', LICENSE_REGION_HOVER[region]);
      })
      .on('mouseout', function(event, d) {
        const region = LICENSE_COUNTRY_REGION[+d.id];
        if (region) d3.select(this).attr('fill', licenseCurrentRegion === region ? LICENSE_REGION_HOVER[region] : LICENSE_REGION_FILL[region]);
      });

    const labels = [
      { r:'americas', x:135, y:170, t:'North America', s:'MTL · BitLicense' },
      { r:'latam', x:200, y:315, t:'Latin America', s:'PSP · Pix' },
      { r:'europe', x:480, y:125, t:'Europe', s:'EMI · MiCA' },
      { r:'apac', x:730, y:195, t:'APAC', s:'MPI · VATP' },
      { r:'me', x:570, y:200, t:'Middle East', s:'VARA · FSRA' },
      { r:'africa', x:490, y:315, t:'Africa', s:'PSO · PSP' },
    ];
    labels.forEach(label => {
      const group = licenseMapSvg.append('g').style('cursor', 'pointer').on('click', () => highlightEnglishLicenseRegion(label.r));
      const hitWidth = label.t === 'Latin America' || label.t === 'Middle East' ? 96 : 82;
      group.append('rect').attr('x', label.x - hitWidth / 2).attr('y', label.y - 15).attr('width', hitWidth).attr('height', 34).attr('rx', 6).attr('fill', 'transparent').attr('pointer-events', 'all');
      group.append('text').attr('x', label.x).attr('y', label.y).attr('text-anchor', 'middle').attr('fill', LICENSE_REGION_HOVER[label.r]).attr('font-size', '11').attr('font-weight', '600').attr('font-family', 'Inter, sans-serif').text(label.t);
      group.append('text').attr('x', label.x).attr('y', label.y + 13).attr('text-anchor', 'middle').attr('fill', LICENSE_REGION_HOVER[label.r]).attr('font-size', '9').attr('opacity', '0.8').attr('font-family', 'SFMono-Regular, Consolas, ui-monospace, monospace').text(label.s);
    });

    document.querySelectorAll('.map-leg[data-region]').forEach(item => {
      item.addEventListener('click', () => highlightEnglishLicenseRegion(item.dataset.region));
    });
  } catch (error) {
    loading.textContent = 'Map data failed to load. Please check the network and refresh.';
    console.error(error);
  }
}

function highlightEnglishLicenseRegion(region) {
  licenseCurrentRegion = region;
  if (licenseMapSvg) {
    licenseMapSvg.selectAll('.country').attr('fill', d => {
      const countryRegion = LICENSE_COUNTRY_REGION[+d.id];
      if (!countryRegion) return 'var(--bg3)';
      return countryRegion === region ? LICENSE_REGION_HOVER[countryRegion] : LICENSE_REGION_FILL[countryRegion];
    });
  }
  document.querySelectorAll('.map-leg[data-region]').forEach(item => {
    item.classList.toggle('active', item.dataset.region === region);
  });
  const meta = LICENSE_REGION_META[region];
  if (!meta) return;
  const titleEl = document.getElementById('map-tip-title');
  const itemsEl = document.getElementById('map-tip-items');
  titleEl.textContent = meta.name;
  titleEl.style.color = meta.color;
  itemsEl.innerHTML = meta.items.map(item => `<div class="map-tip-item"><strong>${item.n}</strong> — ${item.d}</div>`).join('');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initEnglishLicenseMap);
} else {
  initEnglishLicenseMap();
}
</script>
"""


def build_html() -> str:
    css = extract_chinese_design_css()
    sections = extract_english_sections()
    nav = build_nav()
    script = build_script()
    license_map_script = build_license_map_script()
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
    <a class="header-logo-link" href="/en/" aria-label="AllScale home">
      <img class="header-logo" src="/articles/assets/allscale-logo.png" alt="AllScale">
    </a>
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
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>
{script}
{license_map_script}
</body>
</html>
"""


def main() -> None:
    EN_INDEX.write_text(build_html())
    print("Aligned English glossary layout with Chinese visual system")


if __name__ == "__main__":
    main()
