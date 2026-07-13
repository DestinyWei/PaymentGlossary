#!/usr/bin/env python3
"""Import the English AllScale article collection PDF."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ARTICLES = [
    {
        "slug": "checkout",
        "title": "You've clicked 'Pay Now' a thousand times. Do you actually know what Checkout is?",
        "summary": "Start with the checkout page and separate the visible payment entry point from the payment machinery behind it.",
        "start": 2,
    },
    {
        "slug": "invoicing",
        "title": "The invoice arrives before the money does — what is Invoicing really solving?",
        "summary": "Understand invoices, payment terms, remitters, beneficiaries, and why cross-border B2B collection gets messy.",
        "start": 6,
    },
    {
        "slug": "chargeback",
        "title": "The one word every merchant fears: Chargeback",
        "summary": "Separate voids, refunds, and chargebacks, then compare card reversals with stablecoin finality.",
        "start": 10,
    },
    {
        "slug": "payment-roles",
        "title": 'Why does "payment failed" happen? Understand these four roles and it clicks',
        "summary": "Trace failed card payments through the cardholder, issuer, card scheme, acquirer, and merchant.",
        "start": 15,
    },
    {
        "slug": "auth-capture-settlement",
        "title": "Auth, Capture, Settlement: The full journey before the money lands in the pocket",
        "summary": "Follow a card transaction through authorization, capture, clearing, settlement, and final merchant payout.",
        "start": 19,
    },
    {
        "slug": "card-vs-stablecoin-fees",
        "title": "A 100-yuan cup of coffee: card vs stablecoin, how much less does the merchant actually get?",
        "summary": "Use a concrete purchase to unpack MDR, interchange, network fees, acquirer markup, and stablecoin network costs.",
        "start": 23,
    },
    {
        "slug": "cross-border-card-payment",
        "title": "The real journey of a cross-border card payment: 5 players, 6 days, 12 dollars lost",
        "summary": "Walk through a cross-border card order and see where time, fees, FX spread, and reserves enter the journey.",
        "start": 27,
    },
    {
        "slug": "fx-spread",
        "title": "Mid-market rate vs. what you actually get: the hidden spread",
        "summary": "Learn the difference between the mid-market rate and the quoted rate that determines your real FX cost.",
        "start": 32,
    },
    {
        "slug": "swift-correspondent-banking",
        "title": "SWIFT, correspondent banks, intermediary banks: what cross-border money goes through",
        "summary": "Understand SWIFT messages, correspondent banking, Nostro/Vostro accounts, and why wires take time.",
        "start": 36,
    },
    {
        "slug": "stablecoins",
        "title": 'What exactly is a stablecoin? And how does it stay "stable" at $1?',
        "summary": "Explain stablecoin reserves, issuance, redemption, peg stability, and the risks behind the promise.",
        "start": 40,
    },
    {
        "slug": "on-ramp-off-ramp",
        "title": "On-ramp and off-ramp: the two doors in and out of the crypto world",
        "summary": "Map how fiat enters crypto, how stablecoins return to bank money, and where CEXs, DEXs, and OTC desks fit.",
        "start": 44,
    },
    {
        "slug": "custodial-vs-non-custodial",
        "title": "Custodial vs Non-custodial: who actually controls your stablecoins?",
        "summary": "Use private keys and asset control to compare custodial wallets with self-custody.",
        "start": 48,
    },
    {
        "slug": "stablecoin-cross-border-payment",
        "title": "Same cross-border business, 6 days to 6 minutes: the stablecoin version of the trip",
        "summary": "Replace a traditional cross-border path with stablecoins and compare speed, cost, and control.",
        "start": 52,
    },
    {
        "slug": "kyc-kyb-aml",
        "title": "KYC, KYB, AML: what are these compliance words actually trying to do?",
        "summary": "Separate customer identity checks, business verification, and anti-money-laundering monitoring.",
        "start": 56,
    },
    {
        "slug": "vasp-travel-rule",
        "title": "VASP and the Travel Rule: the one compliance rule crypto can't route around",
        "summary": "Define virtual asset service providers and why transaction sender/receiver information travels with funds.",
        "start": 60,
    },
    {
        "slug": "payment-licenses",
        "title": 'Why there\'s no "one license that works everywhere" for payments',
        "summary": "Compare territorial payment regulation across the US, EU, Hong Kong, Singapore, and Dubai.",
        "start": 64,
    },
]

FOOTER = "This collection was authored by AllScale and may not be used for any commercial purpose without permission."
ORDERED_RE = re.compile(r"^\d+[.]\s+")
SECTION_HEADING_RE = re.compile(r"^\d+[.]\s+")


def clean_page(text: str, page_number: int) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line.strip())
        if not line:
            lines.append("")
            continue
        if line == FOOTER or line == f"Page {page_number}":
            continue
        lines.append(line)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def canonical(text: str) -> str:
    return re.sub(r"\s+", "", text)


def remove_title(lines: list[str], title: str) -> list[str]:
    target = canonical(title)
    combined = ""
    for index, line in enumerate(lines):
        if not line:
            continue
        combined += canonical(line)
        if combined == target:
            return lines[index + 1 :]
        if not target.startswith(combined):
            break
    raise ValueError(f"Could not match article title: {title}")


def join_wrapped(left: str, right: str) -> str:
    if not left:
        return right
    if left.endswith("-"):
        return left[:-1] + right
    if left.endswith(("→", "/", "—")):
        return left + " " + right
    return left + " " + right


def is_section_heading(chunk: str) -> bool:
    if not SECTION_HEADING_RE.match(chunk):
        return False
    body = ORDERED_RE.sub("", chunk)
    if body.startswith(("Embedded checkout:", "Payment link:", "QR code:")):
        return False
    if len(body) > 105:
        return False
    if body.startswith(("Pick ", "Connect ", "Confirm ", "Done ")):
        return False
    return True


def parse_blocks(lines: list[str]) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []

    def append_paragraph(text: str) -> None:
        if text:
            blocks.append({"type": "p", "text": text})

    paragraph = ""
    for raw in lines:
        line = raw.strip()
        if not line:
            append_paragraph(paragraph)
            paragraph = ""
            continue

        lower = line.lower()
        heading = is_section_heading(line) or lower in {"wrap-up", "wrapup", "wrap up"}
        bullet = line.startswith("•")
        ordered = ORDERED_RE.match(line) and not heading

        if heading:
            append_paragraph(paragraph)
            paragraph = ""
            blocks.append({"type": "h2", "text": line})
            continue

        if bullet:
            append_paragraph(paragraph)
            paragraph = ""
            item = line[1:].strip()
            if blocks and blocks[-1]["type"] == "ul":
                blocks[-1]["items"].append(item)
            else:
                blocks.append({"type": "ul", "items": [item]})
            continue

        if ordered:
            append_paragraph(paragraph)
            paragraph = ""
            item = ORDERED_RE.sub("", line)
            if blocks and blocks[-1]["type"] == "ol":
                blocks[-1]["items"].append(item)
            else:
                blocks.append({"type": "ol", "items": [item]})
            continue

        if (
            blocks
            and blocks[-1]["type"] in {"ul", "ol"}
            and paragraph == ""
            and not re.search(r"[.!?)]$", blocks[-1]["items"][-1])
        ):
            blocks[-1]["items"][-1] = join_wrapped(blocks[-1]["items"][-1], line)
            continue

        if paragraph and re.search(r"[.!?:)]$", paragraph) and re.match(r"[A-Z(]", line):
            append_paragraph(paragraph)
            paragraph = line
        else:
            paragraph = join_wrapped(paragraph, line)

    append_paragraph(paragraph)
    return blocks


def render_assets(pdf_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    binary = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)

        def render(page: int, name: str) -> Path:
            prefix = temp / name
            subprocess.run(
                [str(binary), "-png", "-f", str(page), "-l", str(page), "-r", "144", str(pdf_path), str(prefix)],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            return next(temp.glob(f"{name}-*.png"))

        cover = Image.open(render(1, "en-cover")).convert("RGB")
        cover.thumbnail((760, 1080), Image.Resampling.LANCZOS)
        cover.save(output_dir / "en-series-cover.webp", "WEBP", quality=88, method=6)

        for article in ARTICLES:
            page = Image.open(render(article["start"], "en-" + article["slug"])).convert("RGB")
            width, height = page.size
            crop = page.crop((int(width * 0.10), int(height * 0.045), int(width * 0.90), int(height * 0.31)))
            crop.thumbnail((1200, 520), Image.Resampling.LANCZOS)
            crop.save(output_dir / f"en-{article['slug']}.webp", "WEBP", quality=86, method=6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, default=Path("articles/content.en.json"))
    parser.add_argument("--assets", type=Path, default=Path("articles/assets"))
    args = parser.parse_args()

    reader = PdfReader(str(args.pdf))
    output = []
    for index, metadata in enumerate(ARTICLES):
        end = ARTICLES[index + 1]["start"] - 1 if index + 1 < len(ARTICLES) else len(reader.pages)
        lines: list[str] = []
        for page_number in range(metadata["start"], end + 1):
            page = reader.pages[page_number - 1]
            page_lines = clean_page(page.extract_text() or "", page_number)
            if page_number == metadata["start"]:
                page_lines = remove_title(page_lines, metadata["title"])
            if index == len(ARTICLES) - 1 and page_number == end:
                for marker in ("About AllScale", "About AllScale "):
                    try:
                        page_lines = page_lines[: next(i for i, line in enumerate(page_lines) if line.strip() == marker)]
                    except StopIteration:
                        pass
            lines.extend(page_lines)
            lines.append("")

        output.append(
            {
                "order": index + 1,
                "slug": metadata["slug"],
                "title": metadata["title"],
                "summary": metadata["summary"],
                "image": f"/articles/assets/en-{metadata['slug']}.webp",
                "blocks": parse_blocks(lines),
            }
        )

    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_assets(args.pdf, args.assets)
    print(f"Imported {len(output)} English articles into {args.output}")


if __name__ == "__main__":
    main()
