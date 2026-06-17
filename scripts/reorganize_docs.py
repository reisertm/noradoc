#!/usr/bin/env python3
"""Reorganize documentation chapters and screenshots.

The script is intentionally data-driven so the repo reorganization can be
reproduced from docs/index.md plus the image rename map below.
"""

from pathlib import Path
import re
import subprocess
import posixpath


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = DOCS / "index.md"
CHAPTERS = DOCS / "chapters"
ASSETS = DOCS / "assets" / "images"


SECTION_SLUGS = {
    "Overview": "overview",
    "Viewer and Daily Use": "viewer-and-daily-use",
    "Annotation and Reading Tools": "annotation-and-reading-tools",
    "Advanced Visualization": "advanced-visualization",
    "Data Import": "data-import",
    "Processing and AI": "processing-and-ai",
    "Installation and Administration": "installation-and-administration",
}


IMAGE_RENAMES = {
    "docs/assets/images/gallery/intro/2026-05-22_12-02.png": "docs/assets/images/chapters/overview/introduction-nora-use-cases.png",
    "docs/assets/images/gallery/2020-10/image-1602062678837.png": "docs/assets/images/chapters/overview/what-is-nora-feature-overview.png",
    "docs/assets/images/gallery/2020-09/image-1600352050589.png": "docs/assets/images/chapters/overview/what-is-nora-viewer-example.png",
    "docs/assets/images/gallery/2020-10/image-1602508371722.png": "docs/assets/images/chapters/viewer-and-daily-use/first-steps-main-workspace.png",
    "docs/assets/images/gallery/2020-10/image-1601650455715.png": "docs/assets/images/chapters/viewer-and-daily-use/first-steps-viewer-toolbar.png",
    "docs/assets/images/gallery/2020-10/image-1601633873571.png": "docs/assets/images/chapters/viewer-and-daily-use/first-steps-study-browser.png",
    "docs/assets/images/gallery/2020-10/image-1601633656873.png": "docs/assets/images/chapters/viewer-and-daily-use/first-steps-series-selection.png",
    "docs/assets/images/gallery/2020-10/image-1602517651838.png": "docs/assets/images/chapters/viewer-and-daily-use/projects-subject-studies-overview.png",
    "docs/assets/images/gallery/autoloader/2026-05-19_15-00.png": "docs/assets/images/chapters/viewer-and-daily-use/autoloaders-menu.png",
    "docs/assets/images/gallery/autoloader/2026-05-19_15-32.png": "docs/assets/images/chapters/viewer-and-daily-use/autoloaders-settings-dialog.png",
    "docs/assets/images/gallery/autoloader/2026-05-19_15-13.png": "docs/assets/images/chapters/viewer-and-daily-use/autoloaders-viewer-example.png",
    "docs/assets/images/gallery/2025-06/daRimage.png": "docs/assets/images/chapters/viewer-and-daily-use/url-sharedlinks-copy-link.png",
    "docs/assets/images/gallery/2025-06/pYHimage.png": "docs/assets/images/chapters/viewer-and-daily-use/url-sharedlinks-open-link.png",
    "docs/assets/images/gallery/2020-09/image-1600354205749.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-roi-list-empty.png",
    "docs/assets/images/gallery/2020-09/image-1600354220857.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-roi-list-selected.png",
    "docs/assets/images/gallery/2020-09/image-1600354300543.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-create-roi-dialog.png",
    "docs/assets/images/gallery/2020-09/image-1600356837328.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-focus-position-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600356743419.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-current-roi-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600356769770.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-toggle-visibility-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600356803683.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-options-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600356868723.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-save-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600356897331.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-download-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600356924459.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-clear-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600356948798.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-delete-icon.png",
    "docs/assets/images/gallery/2020-10/image-1601631951727.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-display-settings.png",
    "docs/assets/images/gallery/2020-10/image-1601631990561.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-color-settings.png",
    "docs/assets/images/gallery/2020-09/image-1600428072743.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-pen-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600432433860.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-pen-example.png",
    "docs/assets/images/gallery/2020-09/image-1600428113719.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-eraser-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600432118373.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-eraser-example.png",
    "docs/assets/images/gallery/2020-09/image-1600428149703.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-polygon-icon.png",
    "docs/assets/images/gallery/2020-09/image-1600432170357.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-polygon-example.png",
    "docs/assets/images/gallery/2020-09/image-1600428181303.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-brush-size-icon.png",
    "docs/assets/images/gallery/2020-09/image-1601375047324.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-brush-size-small.png",
    "docs/assets/images/gallery/2020-09/image-1601374884021.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-brush-size-large.png",
    "docs/assets/images/gallery/2020-09/image-1600428224875.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-fill-icon.png",
    "docs/assets/images/gallery/2020-09/image-1601375520249.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-fill-before.png",
    "docs/assets/images/gallery/2020-09/image-1601375544409.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-fill-after.png",
    "docs/assets/images/gallery/2020-09/image-1600368649317.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-operation-dialog.png",
    "docs/assets/images/gallery/2020-09/image-1600368594193.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-operation-selection.png",
    "docs/assets/images/gallery/2020-09/image-1600368375832.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-operation-result.png",
    "docs/assets/images/gallery/2020-10/image-1601631478257.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-statistics-panel.png",
    "docs/assets/images/gallery/2020-10/image-1601631457986.png": "docs/assets/images/chapters/annotation-and-reading-tools/roi-tool-export-options.png",
    "docs/assets/images/gallery/2022-03/Marker-Tool-1.png": "docs/assets/images/chapters/annotation-and-reading-tools/marker-tool-viewer-example.png",
    "docs/assets/images/gallery/2022-03/Marker-Tool-2.png": "docs/assets/images/chapters/annotation-and-reading-tools/marker-tool-marker-list.png",
    "docs/assets/images/gallery/2022-03/Marker-Tool-3.png": "docs/assets/images/chapters/annotation-and-reading-tools/marker-tool-marker-details.png",
    "docs/assets/images/gallery/2022-03/Marker-Tool-4.png": "docs/assets/images/chapters/annotation-and-reading-tools/marker-tool-marker-placement.png",
    "docs/assets/images/gallery/2022-04/image-1650886820387.png": "docs/assets/images/chapters/annotation-and-reading-tools/navigation-tool-overview.png",
    "docs/assets/images/gallery/2022-04/image-1650891141188.png": "docs/assets/images/chapters/annotation-and-reading-tools/navigation-tool-alignment-options.png",
    "docs/assets/images/gallery/2022-04/image-1650891235110.png": "docs/assets/images/chapters/annotation-and-reading-tools/navigation-tool-deformation-options.png",
    "docs/assets/images/gallery/2022-04/image-1650905242339.png": "docs/assets/images/chapters/annotation-and-reading-tools/navigation-tool-result-view.png",
    "docs/assets/images/gallery/2025-10/a4cimage.png": "docs/assets/images/chapters/annotation-and-reading-tools/reading-tool-toolbar-entry.png",
    "docs/assets/images/gallery/2025-10/UMgimage.png": "docs/assets/images/chapters/annotation-and-reading-tools/reading-tool-case-list.png",
    "docs/assets/images/gallery/2025-10/sdhimage.png": "docs/assets/images/chapters/annotation-and-reading-tools/reading-tool-report-form.png",
    "docs/assets/images/gallery/2025-10/Qmlimage.png": "docs/assets/images/chapters/annotation-and-reading-tools/reading-tool-results-view.png",
    "docs/assets/images/gallery/2025-11/wlHimage.png": "docs/assets/images/chapters/annotation-and-reading-tools/segmentation-assistant-nninteractive-panel.png",
    "docs/assets/images/drawio/2020-09/Drawing-3-1600441543.png": "docs/assets/images/chapters/advanced-visualization/fiber-viewer-architecture-diagram.png",
    "docs/assets/images/gallery/tableviewer/2026-06-16_10-45.png": "docs/assets/images/chapters/advanced-visualization/table-viewer-create-table.png",
    "docs/assets/images/gallery/tableviewer/2026-06-16_10-45_1.png": "docs/assets/images/chapters/advanced-visualization/table-viewer-select-json-keys.png",
    "docs/assets/images/gallery/tableviewer/2026-06-16_10-46.png": "docs/assets/images/chapters/advanced-visualization/table-viewer-json-metadata-table.png",
    "docs/assets/images/gallery/tableviewer/2026-06-16_10-28.png": "docs/assets/images/chapters/advanced-visualization/table-viewer-import-columns.png",
    "docs/assets/images/gallery/2020-10/image-1602508887122.png": "docs/assets/images/chapters/data-import/manual-import-file-selection.png",
    "docs/assets/images/gallery/2020-10/image-1602509856787.png": "docs/assets/images/chapters/data-import/manual-import-upload-progress.png",
    "docs/assets/images/gallery/2025-06/image.png": "docs/assets/images/chapters/data-import/dicom-http-post-example.png",
    "docs/assets/images/gallery/2022-02/starting_pacs_query.png": "docs/assets/images/chapters/data-import/pacs-querier-start-query.png",
    "docs/assets/images/gallery/2022-02/query_gui.png": "docs/assets/images/chapters/data-import/pacs-querier-query-form.png",
    "docs/assets/images/gallery/2022-02/query_search.png": "docs/assets/images/chapters/data-import/pacs-querier-search-results.png",
    "docs/assets/images/gallery/2022-02/query_patient_highlight.png": "docs/assets/images/chapters/data-import/pacs-querier-highlight-patient.png",
    "docs/assets/images/gallery/2022-02/selection_patients_query.png": "docs/assets/images/chapters/data-import/pacs-querier-select-patients.png",
    "docs/assets/images/gallery/2022-02/view_query_import.png": "docs/assets/images/chapters/data-import/pacs-querier-import-view.png",
    "docs/assets/images/gallery/createproject/2026-06-15_11-42.png": "docs/assets/images/chapters/data-import/create-project-backend-folder-pattern.png",
    "docs/assets/images/gallery/2020-09/image-1600353714384.png": "docs/assets/images/chapters/processing-and-ai/general-processing-panel.png",
    "docs/assets/images/gallery/2020-09/image-1601205201699.png": "docs/assets/images/chapters/processing-and-ai/batchtool-overview.png",
    "docs/assets/images/gallery/image_batchtool_fig2.png": "docs/assets/images/chapters/processing-and-ai/batchtool-job-configuration.png",
    "docs/assets/images/gallery/2020-09/image-1601199202182.png": "docs/assets/images/chapters/processing-and-ai/batchtool-job-list.png",
    "docs/assets/images/gallery/2020-09/image-1601211881748.png": "docs/assets/images/chapters/processing-and-ai/batchtool-results-view.png",
    "docs/assets/images/gallery/2020-09/image-1601211287963.png": "docs/assets/images/chapters/processing-and-ai/jobs-overview.png",
    "docs/assets/images/gallery/2026-05/image.png": "docs/assets/images/chapters/processing-and-ai/jupyter-notebooks-launch-entry.png",
    "docs/assets/images/gallery/2026-05/YzIimage.png": "docs/assets/images/chapters/processing-and-ai/jupyter-notebooks-server-dialog.png",
    "docs/assets/images/gallery/2022-04/image-1649269648564.png": "docs/assets/images/chapters/processing-and-ai/jupyter-notebooks-notebook-list.png",
    "docs/assets/images/gallery/2022-04/image-1649269771467.png": "docs/assets/images/chapters/processing-and-ai/jupyter-notebooks-open-notebook.png",
    "docs/assets/images/gallery/openssh/2026-06-15_11-45.png": "docs/assets/images/chapters/processing-and-ai/jupyter-notebooks-openssh-launch-entry.png",
    "docs/assets/images/gallery/openssh/2026-06-15_11-46.png": "docs/assets/images/chapters/processing-and-ai/jupyter-notebooks-openssh-job-dialog.png",
    "docs/assets/images/gallery/openssh/2026-06-15_11-47.png": "docs/assets/images/chapters/processing-and-ai/jupyter-notebooks-openssh-connection-details.png",
    "docs/assets/images/gallery/2022-04/image-1649269997390.png": "docs/assets/images/chapters/processing-and-ai/jupyter-notebooks-terminal-view.png",
    "docs/assets/images/gallery/2025-11/vPSimage.png": "docs/assets/images/chapters/processing-and-ai/segmentation-deep-learning-overview.png",
    "docs/assets/images/gallery/2025-11/qiPimage.png": "docs/assets/images/chapters/processing-and-ai/segmentation-deep-learning-results.png",
    "docs/assets/images/gallery/2020-09/image-1601198758646.png": "docs/assets/images/unreferenced/legacy-batchtool-workflow-annotated.png",
    "docs/assets/images/gallery/2020-09/image-1600353314610.png": "docs/assets/images/unreferenced/legacy-database-schema-overview.png",
    "docs/assets/images/gallery/2020-09/image-1600352934446.png": "docs/assets/images/unreferenced/legacy-nora-system-architecture.png",
    "docs/assets/images/gallery/2020-09/image-1600353338398.png": "docs/assets/images/unreferenced/legacy-database-schema-studies-files.png",
    "docs/assets/images/gallery/2020-09/image-1600462098461.png": "docs/assets/images/unreferenced/legacy-pencil-tool-icon.png",
}


def git_mv(src, dst):
    src_path = ROOT / src
    dst_path = ROOT / dst
    if src_path == dst_path:
        return
    if dst_path.exists() and not src_path.exists():
        return
    if not src_path.exists():
        raise FileNotFoundError(src)
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", str(src_path), str(dst_path)], cwd=ROOT, check=True)


def parse_index():
    sections = {}
    current = None
    for line in INDEX.read_text().splitlines():
        heading = re.match(r"^##\s+(.+)$", line)
        if heading:
            title = heading.group(1)
            current = SECTION_SLUGS.get(title)
            if current:
                sections[current] = []
            continue
        link = re.match(r"^-\s+\[[^\]]+\]\((chapters/[^)]+\.md)\)", line)
        if current and link:
            sections[current].append(link.group(1))
    return sections


def move_chapters(sections):
    path_map = {}
    for section_slug, links in sections.items():
        for link in links:
            name = Path(link).name
            src = f"docs/chapters/{name}"
            dst = f"docs/chapters/{section_slug}/{name}"
            git_mv(src, dst)
            path_map[link] = f"chapters/{section_slug}/{name}"
    return path_map


def rewrite_index(path_map):
    text = INDEX.read_text()
    for old, new in path_map.items():
        text = text.replace(f"]({old})", f"]({new})")
    INDEX.write_text(text)


def rewrite_markdown_links(chapter_paths):
    src_to_dst = {f"../{src[len('docs/'):]}": f"../../{dst[len('docs/'):]}" for src, dst in IMAGE_RENAMES.items()}
    for path in chapter_paths:
        text = path.read_text()
        for old, new in src_to_dst.items():
            text = text.replace(old, new)
        path.write_text(text)


def rewrite_chapter_links():
    md_by_name = {path.name: path for path in CHAPTERS.rglob("*.md")}
    link_re = re.compile(r"\]\(([^)]+\.md(?:#[^)]+)?)\)")

    for source in CHAPTERS.rglob("*.md"):
        text = source.read_text()

        def replace_link(match):
            raw_target = match.group(1)
            if "://" in raw_target or raw_target.startswith("mailto:"):
                return match.group(0)
            target_path, separator, anchor = raw_target.partition("#")
            target_name = Path(target_path).name
            if target_name == "index.md":
                resolved = INDEX
            elif target_name in md_by_name:
                resolved = md_by_name[target_name]
            else:
                return match.group(0)

            new_target = posixpath.relpath(resolved, source.parent)
            if separator:
                new_target = f"{new_target}#{anchor}"
            return match.group(0).replace(raw_target, new_target)

        rewritten = link_re.sub(replace_link, text)
        if rewritten != text:
            source.write_text(rewritten)


def move_images():
    for src, dst in IMAGE_RENAMES.items():
        git_mv(src, dst)


def main():
    sections = parse_index()
    path_map = move_chapters(sections)
    rewrite_index(path_map)
    move_images()
    rewrite_markdown_links((CHAPTERS / slug / Path(link).name for slug, links in sections.items() for link in links))
    rewrite_chapter_links()


if __name__ == "__main__":
    main()
