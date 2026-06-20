#!/usr/bin/env python3
"""Import the AllScale article collection PDF into structured site content."""

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
        "title": "你点过上千次“立即支付”，但真的懂 Checkout 吗？",
        "summary": "从收银台的三种常见形态出发，理解 Checkout 与真正资金处理之间的区别。",
        "start": 2,
    },
    {
        "slug": "invoicing",
        "title": "钱还没到，账单先到——Invoicing 到底在解决什么？",
        "summary": "从 Invoice、账期和对账入手，看懂 B2B 与跨境业务为什么需要开票收款。",
        "start": 6,
    },
    {
        "slug": "chargeback",
        "title": "商户最怕的一个词：Chargeback",
        "summary": "分清撤销、退款与拒付，以及卡支付和稳定币在交易终局性上的根本差异。",
        "start": 10,
    },
    {
        "slug": "payment-roles",
        "title": "为什么有时候会「支付失败」？看懂这四个角色就明白了",
        "summary": "拆解持卡人、发卡行、卡组织、收单行和商户，找到支付失败发生的位置。",
        "start": 14,
    },
    {
        "slug": "auth-capture-settlement",
        "title": "Auth、Capture、Settlement：钱落袋之前的完整旅程",
        "summary": "沿着授权、请款、清算和结算四个节点，理解一笔卡支付真正完成的全过程。",
        "start": 18,
    },
    {
        "slug": "card-vs-stablecoin-fees",
        "title": "一杯 100 块的咖啡：刷卡和稳定币，商户到手差多少？",
        "summary": "用一笔具体交易拆解 MDR、交换费、网络费与稳定币链上成本。",
        "start": 22,
    },
    {
        "slug": "cross-border-card-payment",
        "title": "一笔跨境卡支付的真实旅程：5 个角色、6 天、少了 12 美元",
        "summary": "跟随一笔跨境订单，看看资金经过授权、清算和银行接力后还剩多少。",
        "start": 26,
    },
    {
        "slug": "fx-spread",
        "title": "中间汇率 vs 你拿到的汇率：那道藏起来的点差",
        "summary": "看懂 Mid-market rate 与 Spread，识别“零手续费”背后的真实换汇成本。",
        "start": 30,
    },
    {
        "slug": "swift-correspondent-banking",
        "title": "SWIFT、代理行、中转行：跨境的钱在路上经历了什么？",
        "summary": "理解 SWIFT 报文、Nostro/Vostro 账户、代理行和在途资金如何共同运作。",
        "start": 33,
    },
    {
        "slug": "stablecoins",
        "title": "稳定币到底是什么？凭什么能「稳」在 1 美元？",
        "summary": "从储备、铸造与销毁机制出发，理解稳定币的锚定逻辑与风险来源。",
        "start": 37,
    },
    {
        "slug": "on-ramp-off-ramp",
        "title": "On-ramp 和 Off-ramp：进出加密世界的两道门",
        "summary": "梳理法币与稳定币之间的转换路径，以及 CEX、DEX、OTC 的角色差异。",
        "start": 40,
    },
    {
        "slug": "custodial-vs-non-custodial",
        "title": "Custodial vs Non-custodial：你的稳定币到底归谁管？",
        "summary": "从私钥和资产控制权出发，理解托管钱包与自托管钱包的收益和代价。",
        "start": 43,
    },
    {
        "slug": "stablecoin-cross-border-payment",
        "title": "同一笔跨境生意，从 6 天到 6 分钟：稳定币版的旅程",
        "summary": "把传统跨境链路替换成稳定币路径，比较时间、费用与责任边界的变化。",
        "start": 47,
    },
    {
        "slug": "kyc-kyb-aml",
        "title": "KYC、KYB、AML：合规这些词，到底在管什么？",
        "summary": "分清个人身份识别、企业尽调与反洗钱监控分别解决什么问题。",
        "start": 50,
    },
    {
        "slug": "vasp-travel-rule",
        "title": "VASP 和 Travel Rule：加密世界绕不开的一条合规规则",
        "summary": "理解虚拟资产服务商的身份，以及资金转移信息为什么需要随交易同行。",
        "start": 54,
    },
    {
        "slug": "payment-licenses",
        "title": "为什么没有「一张通全球」的支付牌照？",
        "summary": "从属地监管出发，快速认识美国、欧盟、香港、新加坡和迪拜的牌照体系。",
        "start": 57,
    },
]

FOOTER = "本合集由 AllScale 官方撰写，未经允许不得用于任何商业用途"
HEADING_RE = re.compile(r"^[一二三四五六七八九十]+、")
ORDERED_RE = re.compile(r"^\d+[.、]\s*")


def canonical(text: str) -> str:
    return re.sub(r"\s+", "", text)


def join_wrapped(left: str, right: str) -> str:
    if not left:
        return right
    if left.endswith("-"):
        return left + right
    if re.search(r"[A-Za-z0-9)]$", left) and re.match(r"[A-Za-z0-9(]", right):
        return left + " " + right
    return left + right


def normalize_mixed_spacing(text: str) -> str:
    text = re.sub(r"([\u4e00-\u9fff])([A-Za-z0-9])", r"\1 \2", text)
    text = re.sub(r"([A-Za-z0-9])([\u4e00-\u9fff])", r"\1 \2", text)
    return text


def clean_page(text: str, page_number: int) -> list[str]:
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line.strip())
        compact = canonical(line)
        if compact in {"第页", str(page_number), f"第{page_number}页", canonical(FOOTER)}:
            continue
        lines.append(line)
    while lines and not lines[-1]:
        lines.pop()
    return lines


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


def truncate_at(lines: list[str], marker: str) -> list[str]:
    marker_key = canonical(marker)
    for index, line in enumerate(lines):
        if canonical(line) == marker_key:
            return lines[:index]
    return lines


def split_chunks(lines: list[str]) -> list[str]:
    chunks: list[str] = []
    current = ""
    for line in lines:
        if not line:
            if current:
                chunks.append(current)
                current = ""
            continue
        current = join_wrapped(current, line)
    if current:
        chunks.append(current)
    return chunks


def recover_source_spacing(chunks: list[str], source_lines: list[str]) -> list[str]:
    source = "\n".join(source_lines)
    compact_chars = []
    positions = []
    for index, char in enumerate(source):
        if not char.isspace():
            compact_chars.append(char)
            positions.append(index)

    compact_source = "".join(compact_chars)
    cursor = 0
    recovered = []
    for chunk in chunks:
        key = canonical(chunk)
        start = compact_source.find(key, cursor)
        if start < 0:
            recovered.append(normalize_mixed_spacing(chunk))
            continue
        raw = source[positions[start] : positions[start + len(key) - 1] + 1]
        clean_lines = [re.sub(r"\s+", " ", line.strip()) for line in raw.splitlines() if line.strip()]
        text = ""
        for line in clean_lines:
            text = join_wrapped(text, line)
        recovered.append(normalize_mixed_spacing(text))
        cursor = start + len(key)
    return recovered


def parse_blocks(layout_lines: list[str], source_lines: list[str]) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    chunks = recover_source_spacing(split_chunks(layout_lines), source_lines)

    for chunk in chunks:
        if HEADING_RE.match(chunk) or chunk == "小结":
            blocks.append({"type": "h2", "text": chunk})
        elif chunk.startswith("•"):
            item = chunk[1:].strip()
            if blocks and blocks[-1]["type"] == "ul":
                blocks[-1]["items"].append(item)
            else:
                blocks.append({"type": "ul", "items": [item]})
        elif ORDERED_RE.match(chunk):
            item = ORDERED_RE.sub("", chunk)
            if blocks and blocks[-1]["type"] == "ol":
                blocks[-1]["items"].append(item)
            else:
                blocks.append({"type": "ol", "items": [item]})
        else:
            blocks.append({"type": "p", "text": chunk})
    return blocks


def render_assets(pdf_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    bundled = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pdftoppm"
    binary = bundled if bundled.exists() else Path("pdftoppm")

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

        cover = Image.open(render(1, "cover")).convert("RGB")
        cover.thumbnail((760, 1080), Image.Resampling.LANCZOS)
        cover.save(output_dir / "series-cover.webp", "WEBP", quality=88, method=6)

        for article in ARTICLES:
            page = Image.open(render(article["start"], article["slug"])).convert("RGB")
            width, height = page.size
            crop = page.crop((int(width * 0.11), int(height * 0.045), int(width * 0.89), int(height * 0.31)))
            crop.thumbnail((1200, 520), Image.Resampling.LANCZOS)
            crop.save(output_dir / f"{article['slug']}.webp", "WEBP", quality=86, method=6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, default=Path("articles/content.json"))
    parser.add_argument("--assets", type=Path, default=Path("articles/assets"))
    args = parser.parse_args()

    reader = PdfReader(str(args.pdf))
    output = []
    for index, metadata in enumerate(ARTICLES):
        end = ARTICLES[index + 1]["start"] - 1 if index + 1 < len(ARTICLES) else 60
        layout_lines: list[str] = []
        source_lines: list[str] = []
        for page_number in range(metadata["start"], end + 1):
            page = reader.pages[page_number - 1]
            layout_page = clean_page(page.extract_text(extraction_mode="layout") or "", page_number)
            source_page = clean_page(page.extract_text() or "", page_number)
            if page_number == metadata["start"]:
                layout_page = remove_title(layout_page, metadata["title"])
                source_page = remove_title(source_page, metadata["title"])
            if index == len(ARTICLES) - 1 and page_number == 60:
                layout_page = truncate_at(layout_page, "关于 AllScale")
                source_page = truncate_at(source_page, "关于 AllScale")
            layout_lines.extend(layout_page)
            layout_lines.append("")
            source_lines.extend(source_page)
            source_lines.append("")

        output.append(
            {
                "order": index + 1,
                "slug": metadata["slug"],
                "title": metadata["title"],
                "summary": metadata["summary"],
                "image": f"/articles/assets/{metadata['slug']}.webp",
                "blocks": parse_blocks(layout_lines, source_lines),
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_assets(args.pdf, args.assets)
    print(f"Imported {len(output)} articles into {args.output}")


if __name__ == "__main__":
    main()
