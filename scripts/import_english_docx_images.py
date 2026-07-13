#!/usr/bin/env python3
"""Import original English article illustrations from the AllScale DOCX collection."""

from __future__ import annotations

import argparse
import json
import re
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from PIL import Image


def canonical(text: str) -> str:
    return re.sub(r"\s+", "", text)


def paragraph_images(document: Document, paragraph) -> list[tuple[str, bytes]]:
    images = []
    for blip in paragraph._p.xpath(".//a:blip"):
        relationship_id = blip.get(qn("r:embed"))
        relationship = document.part.rels[relationship_id]
        images.append((relationship.target_ref, relationship.target_part.blob))
    return images


def map_images(document: Document, articles: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    title_map = {canonical(article["title"]): article for article in articles}
    mapped = {article["slug"]: {"hero": None, "sections": []} for article in articles}
    pending: list[tuple[str, bytes]] = []
    current_article = None

    for paragraph in document.paragraphs:
        pending.extend(paragraph_images(document, paragraph))
        text = paragraph.text.strip()
        if not text:
            continue

        article = title_map.get(canonical(text))
        if article:
            current_article = article
            if not pending:
                raise ValueError(f"Missing hero image before article: {text}")
            mapped[article["slug"]]["hero"] = pending[-1]
            pending.clear()
            continue

        if current_article and pending:
            for image in pending:
                mapped[current_article["slug"]]["sections"].append({"anchor": text, "image": image})
            pending.clear()
        elif pending:
            pending.clear()

    for article in articles:
        result = mapped[article["slug"]]
        count = (1 if result["hero"] else 0) + len(result["sections"])
        if count != 5:
            raise ValueError(f"Expected 5 images for {article['slug']}, found {count}")
    return mapped


def save_webp(blob: bytes, output_path: Path) -> None:
    with Image.open(BytesIO(blob)) as image:
        image.load()
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        image.thumbnail((1600, 1000), Image.Resampling.LANCZOS)
        image.save(output_path, "WEBP", quality=88, method=6)


def insert_section_image(article: dict[str, object], anchor: str, src: str) -> None:
    anchor_key = canonical(anchor)
    blocks = article["blocks"]
    for index, block in enumerate(blocks):
        if block["type"] in {"h2", "p"} and canonical(block["text"]) == anchor_key:
            blocks.insert(
                index,
                {
                    "type": "image",
                    "src": src,
                    "alt": f"{article['title']}: {anchor}",
                },
            )
            return

    for index, block in enumerate(blocks):
        if block["type"] not in {"h2", "p"}:
            continue
        block_key = canonical(block["text"])
        if anchor_key.startswith(block_key) or block_key.startswith(anchor_key):
            blocks.insert(
                index,
                {
                    "type": "image",
                    "src": src,
                    "alt": f"{article['title']}: {anchor}",
                },
            )
            return

    raise ValueError(f"Could not find section '{anchor}' in {article['slug']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--content", type=Path, default=Path("articles/content.en.json"))
    parser.add_argument("--assets", type=Path, default=Path("articles/assets"))
    args = parser.parse_args()

    articles = json.loads(args.content.read_text(encoding="utf-8"))
    for article in articles:
        article["blocks"] = [block for block in article["blocks"] if block["type"] != "image"]

    document = Document(str(args.docx))
    mapped = map_images(document, articles)
    args.assets.mkdir(parents=True, exist_ok=True)

    for article in articles:
        article_images = mapped[article["slug"]]
        hero_path = args.assets / f"en-{article['slug']}.webp"
        save_webp(article_images["hero"][1], hero_path)
        article["image"] = f"/articles/assets/{hero_path.name}"

        for number, section in enumerate(article_images["sections"], start=2):
            image_path = args.assets / f"en-{article['slug']}-{number:02d}.webp"
            save_webp(section["image"][1], image_path)
            insert_section_image(article, section["anchor"], f"/articles/assets/{image_path.name}")

    args.content.write_text(json.dumps(articles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported 80 English illustrations across {len(articles)} articles")


if __name__ == "__main__":
    main()
