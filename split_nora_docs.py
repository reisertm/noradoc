#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "nora-documentation.md"
DOCS_DIR = ROOT / "docs"
CHAPTERS_DIR = DOCS_DIR / "chapters"
ASSETS_DIR = DOCS_DIR / "assets" / "images"
INDEX_PATH = DOCS_DIR / "index.md"
REPORT_PATH = DOCS_DIR / "migration-report.md"


BOOKSTACK_PAGE_ALIASES = {
    "subjectstudies-table": "projects-and-subject-studies",
    "roi-tool": "roi-tool",
}


UPLOAD_RE = re.compile(
    r"^https?://(?:www\.)?nora-imaging\.org/doc/uploads/images/(?P<kind>gallery|drawio)/"
    r"(?P<bucket>\d{4}-\d{2})/(?:(?:scaled-\d+-)/)?(?P<name>[^?#)]+)$",
    re.IGNORECASE,
)
LINKED_IMAGE_RE = re.compile(
    r"\[!\[(?P<alt>[^\]]*)\]\((?P<thumb>https?://[^)\s]+)\)(?P<trailing>[^\]]*)\]\((?P<full>https?://[^)\s]+)\)"
)
BROKEN_LINKED_IMAGE_RE = re.compile(
    r"\[\s*\n(?P<indent>\s*)!\[(?P<alt>[^\]]*)\]\((?P<thumb>https?://[^)\s]+)\)\]\((?P<full>https?://[^)\s]+)\)"
)
INLINE_IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<url>https?://[^)\s]+)\)")
IMG_SRC_RE = re.compile(r'(?P<prefix><img\b[^>]*\bsrc=")(?P<url>https?://[^"]+)(?P<suffix>"[^>]*>)')
BOOKSTACK_LINK_RE = re.compile(
    r"\[(?P<label>[^\]]+)\]\((?P<url>https?://(?:www\.)?nora-imaging\.org/doc/books/nora-documentation/page/(?P<page>[^)\s\"#]+)(?:\s+\"(?P<title>[^\"]*)\")?)\)"
)
LOCAL_IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>\.\./assets/images/[^)]+)\)")


def slugify(text: str) -> str:
    value = html.unescape(text)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("&", " and ")
    value = re.sub(r"[^A-Za-z0-9]+", "-", value)
    value = value.strip("-").lower()
    return value or "chapter"


def clean_heading(text: str) -> str:
    value = html.unescape(text)
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("&amp;", "&")
    value = re.sub(r"\s+", " ", value)
    value = value.strip()
    return value or "Untitled"


def normalize_heading_line(line: str) -> str:
    match = re.match(r"^(#{1,6})\s+(.*)$", line)
    if not match:
        return line
    hashes, title = match.groups()
    cleaned = html.unescape(title)
    cleaned = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = cleaned.replace("&amp;", "&")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return ""
    return f"{hashes} {cleaned}"


def chapter_asset_path(url: str, used_paths: Dict[str, str]) -> Path:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    bucket = "misc"
    kind = "external"
    match = UPLOAD_RE.match(url)
    if match:
        kind = match.group("kind").lower()
        bucket = match.group("bucket")
        name = match.group("name")
    rel = Path(kind) / bucket / name
    rel_key = rel.as_posix()
    if rel_key in used_paths and used_paths[rel_key] != url:
        stem = rel.stem
        suffix = rel.suffix
        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
        rel = rel.with_name(f"{stem}-{digest}{suffix}")
        rel_key = rel.as_posix()
    used_paths[rel_key] = url
    return rel


def download_bytes(url: str) -> bytes:
    with urlopen(url, timeout=60) as response:
        return response.read()


def split_source(text: str) -> List[Tuple[str, List[str]]]:
    chapters: List[Tuple[str, List[str]]] = []
    current_title = None
    current_lines: List[str] = []

    for line in text.splitlines():
        heading = re.match(r"^#\s+(.*)$", line)
        if heading:
            title = clean_heading(heading.group(1))
            if title == "NORA Documentation":
                current_title = None
                current_lines = []
                continue
            if current_title is not None:
                chapters.append((current_title, current_lines))
            current_title = title
            current_lines = [f"# {title}"]
            continue
        if current_title is not None:
            current_lines.append(normalize_heading_line(line))

    if current_title is not None:
        chapters.append((current_title, current_lines))
    return chapters


def build_chapter_map(chapters: Iterable[Tuple[str, List[str]]]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for title, _ in chapters:
        slug = slugify(title)
        mapping[slug] = f"{slug}.md"
    mapping.update({alias: f"{target}.md" for alias, target in BOOKSTACK_PAGE_ALIASES.items()})
    return mapping


def rewrite_bookstack_links(
    text: str,
    chapter_map: Dict[str, str],
    unresolved: List[Tuple[str, str]],
) -> str:
    def repl(match: re.Match[str]) -> str:
        label = match.group("label")
        page = match.group("page")
        page_slug = slugify(page.replace("_", "-"))
        target = chapter_map.get(page_slug)
        if target is None:
            unresolved.append((label, match.group("url")))
            return f"{label} (unresolved BookStack link: {match.group('url')})"
        return f"[{label}]({target})"

    return BOOKSTACK_LINK_RE.sub(repl, text)


def rewrite_images(
    text: str,
    asset_urls: Dict[str, Path],
) -> str:
    def relative(url: str) -> str:
        asset_rel = asset_urls[url]
        return Path("..") / "assets" / "images" / asset_rel

    def linked_repl(match: re.Match[str]) -> str:
        full = match.group("full")
        if full in asset_urls:
            alt = (match.group("alt") + match.group("trailing")).strip()
            return f"![{alt}]({relative(full).as_posix()})"
        return match.group(0)

    def broken_linked_repl(match: re.Match[str]) -> str:
        full = match.group("full")
        if full in asset_urls:
            indent = match.group("indent")
            alt = match.group("alt").strip()
            return f"\n{indent}![{alt}]({relative(full).as_posix()})"
        return match.group(0)

    def inline_repl(match: re.Match[str]) -> str:
        url = match.group("url")
        if url in asset_urls:
            return f"![{match.group('alt')}]({relative(url).as_posix()})"
        return match.group(0)

    def img_repl(match: re.Match[str]) -> str:
        url = match.group("url")
        if url in asset_urls:
            return f"{match.group('prefix')}{relative(url).as_posix()}{match.group('suffix')}"
        return match.group(0)

    text = LINKED_IMAGE_RE.sub(linked_repl, text)
    text = BROKEN_LINKED_IMAGE_RE.sub(broken_linked_repl, text)
    text = INLINE_IMAGE_RE.sub(inline_repl, text)
    text = IMG_SRC_RE.sub(img_repl, text)
    return text


def convert_table_markdown_images(text: str) -> str:
    lines = text.splitlines()
    converted: List[str] = []
    in_table = False

    def img_to_html(match: re.Match[str]) -> str:
        alt = html.escape(match.group("alt"), quote=True)
        path = html.escape(match.group("path"), quote=True)
        return f'<img src="{path}" alt="{alt}" />'

    for line in lines:
        if "<table" in line:
            in_table = True
        if in_table:
            line = LOCAL_IMAGE_RE.sub(img_to_html, line)
        converted.append(line)
        if "</table>" in line:
            in_table = False

    return "\n".join(converted)


def collect_asset_urls(text: str) -> List[str]:
    urls = set()
    linked_ranges: List[Tuple[int, int]] = []

    for match in LINKED_IMAGE_RE.finditer(text):
        full = match.group("full")
        thumb = match.group("thumb")
        urls.add(full if UPLOAD_RE.match(full) else thumb)
        linked_ranges.append(match.span())

    for match in BROKEN_LINKED_IMAGE_RE.finditer(text):
        full = match.group("full")
        thumb = match.group("thumb")
        urls.add(full if UPLOAD_RE.match(full) else thumb)
        linked_ranges.append(match.span())

    scrubbed = text
    for start, end in reversed(linked_ranges):
        scrubbed = scrubbed[:start] + (" " * (end - start)) + scrubbed[end:]

    for match in INLINE_IMAGE_RE.finditer(scrubbed):
        urls.add(match.group("url"))

    for match in IMG_SRC_RE.finditer(text):
        urls.add(match.group("url"))

    collected = []
    for url in sorted(urls):
        if UPLOAD_RE.match(url):
            collected.append(url)
    return collected


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_index(chapters: List[Tuple[str, str]]) -> str:
    lines = [
        "# NORA Documentation",
        "",
        "Normalized from a BookStack export into repo-friendly markdown chapters.",
        "",
        "## Chapters",
        "",
    ]
    for title, filename in chapters:
        lines.append(f"- [{title}](chapters/{filename})")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Original export is preserved in `../nora-documentation.md`.",
            "- Local images live under `assets/images/`.",
            "- Migration details and unresolved links are listed in `migration-report.md`.",
        ]
    )
    return "\n".join(lines)


def build_report(
    chapters: List[Tuple[str, str]],
    asset_urls: Dict[str, Path],
    unresolved: List[Tuple[str, str]],
    failures: List[Tuple[str, str]],
) -> str:
    lines = [
        "# Migration Report",
        "",
        f"- Chapters created: {len(chapters)}",
        f"- Localized image assets referenced: {len(asset_urls)}",
        f"- Unresolved BookStack links: {len(unresolved)}",
        f"- Asset download failures: {len(failures)}",
        "",
    ]

    if unresolved:
        lines.extend(["## Unresolved BookStack Links", ""])
        for label, url in unresolved:
            lines.append(f"- `{label}` -> {url}")
        lines.append("")

    if failures:
        lines.extend(["## Asset Download Failures", ""])
        for url, error in failures:
            lines.append(f"- `{url}`: {error}")
        lines.append("")

    if not unresolved and not failures:
        lines.extend(["No unresolved internal links or download failures were detected.", ""])

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Split BookStack markdown export into repo-friendly docs.")
    parser.add_argument("--skip-downloads", action="store_true", help="Rewrite files without downloading image assets.")
    args = parser.parse_args()

    if not SOURCE.exists():
        print(f"Missing source file: {SOURCE}", file=sys.stderr)
        return 1

    source_text = SOURCE.read_text(encoding="utf-8")
    raw_chapters = split_source(source_text)
    chapter_map = build_chapter_map(raw_chapters)

    used_paths: Dict[str, str] = {}
    asset_urls: Dict[str, Path] = {}
    for url in collect_asset_urls(source_text):
        asset_urls[url] = chapter_asset_path(url, used_paths)

    unresolved: List[Tuple[str, str]] = []
    failures: List[Tuple[str, str]] = []
    written_chapters: List[Tuple[str, str]] = []

    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    for title, lines in raw_chapters:
        slug = slugify(title)
        filename = f"{slug}.md"
        chapter_path = CHAPTERS_DIR / filename
        content = "\n".join(lines)
        content = rewrite_bookstack_links(content, chapter_map, unresolved)
        content = rewrite_images(content, asset_urls)
        content = convert_table_markdown_images(content)
        write_text(chapter_path, content)
        written_chapters.append((title, filename))

    if not args.skip_downloads:
        for url, rel_path in asset_urls.items():
            target = ASSETS_DIR / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                continue
            try:
                target.write_bytes(download_bytes(url))
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                failures.append((url, str(exc)))

    write_text(INDEX_PATH, build_index(written_chapters))
    write_text(REPORT_PATH, build_report(written_chapters, asset_urls, unresolved, failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
