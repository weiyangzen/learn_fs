#!/usr/bin/env python3
"""Count source-like lines across learn_fs source checkouts.

This is an approximate physical line counter for study inventory. It counts
tracked files when a source tree is a git repository and falls back to walking
the directory for non-git source snapshots. Build outputs, binary fixtures, and
common generated/vendor path classes are excluded.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import subprocess
import sys
from dataclasses import asdict, dataclass


ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests" / "sources.tsv"
EXCLUDE_FILE = ROOT / "manifests" / "exclude.generated-vendor.txt"
FOCUS_FILE = ROOT / "manifests" / "focus_paths.tsv"
TARGETS_FILE = ROOT / "manifests" / "research_targets.tsv"

CODE_EXTENSIONS = {
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".hxx",
    ".m", ".mm", ".rs", ".go", ".py", ".sh", ".bash", ".zsh", ".fish",
    ".pl", ".pm", ".rb", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".java", ".kt", ".kts", ".scala", ".groovy", ".cs", ".swift",
    ".vala", ".vapi", ".lua", ".php", ".asm", ".s", ".S", ".inc",
    ".qml", ".qbs", ".ui", ".glsl", ".vert", ".frag", ".comp", ".geom",
    ".tesc", ".tese", ".proto", ".capnp", ".thrift", ".idl", ".y",
    ".yy", ".l", ".ll", ".awk", ".sed", ".meson", ".cmake", ".mk",
    ".mak", ".am", ".ac", ".in", ".service", ".socket", ".timer",
    ".rules", ".policy", ".desktop", ".xml", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".conf", ".cfg", ".gradle", ".bzl", ".bazel",
    ".BUILD", ".rs.in", ".go.in",
}

CODE_NAMES = {
    "Makefile", "makefile", "GNUmakefile", "Kbuild", "Kconfig",
    "meson.build", "meson_options.txt", "CMakeLists.txt", "configure.ac",
    "configure", "autogen.sh", "PKGBUILD", "Dockerfile", "Containerfile",
    "BUILD", "WORKSPACE", "MODULE.bazel",
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".icns", ".pdf",
    ".zip", ".gz", ".xz", ".bz2", ".zst", ".7z", ".tar", ".jar",
    ".war", ".class", ".o", ".a", ".so", ".dylib", ".dll", ".exe",
    ".bin", ".dat", ".ttf", ".otf", ".woff", ".woff2", ".mp3", ".mp4",
    ".mov", ".avi", ".wav", ".flac", ".fw", ".ucode", ".rom", ".fd",
    ".dtb", ".dtbo", ".qsb", ".spv", ".qcow2", ".raw", ".img", ".iso",
}


@dataclass
class Repo:
    tier: str
    category: str
    repo_id: str
    path: str
    url: str
    recurse: str
    default_count: str
    notes: str


@dataclass
class Row:
    tier: str
    category: str
    repo_id: str
    path: str
    url: str
    head: str
    files: int
    text_files: int
    text_lines: int
    code_files: int
    code_lines: int
    binary_skipped: int
    missing: bool


def load_excluded_parts() -> set[str]:
    if not EXCLUDE_FILE.exists():
        return set()
    return {
        line.strip()
        for line in EXCLUDE_FILE.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    }


def load_manifest() -> list[Repo]:
    rows: list[Repo] = []
    with MANIFEST.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            rows.append(
                Repo(
                    tier=row["tier"],
                    category=row["category"],
                    repo_id=row["id"],
                    path=row["path"],
                    url=row["url"],
                    recurse=row["recurse"],
                    default_count=row["default_count"],
                    notes=row["notes"],
                )
            )
    return rows


def load_focus_paths() -> dict[str, list[str]]:
    if not FOCUS_FILE.exists():
        return {}
    focus: dict[str, list[str]] = {}
    with FOCUS_FILE.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            repo_id = row["id"]
            focus_path = row["focus_path"]
            focus.setdefault(repo_id, []).append(focus_path)
    return focus


def load_optimized_ids() -> set[str]:
    if not TARGETS_FILE.exists():
        raise FileNotFoundError(f"missing optimized target manifest: {TARGETS_FILE}")
    with TARGETS_FILE.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return {
            row["source_id"]
            for row in reader
            if row.get("optimized_count") == "yes"
        }


def include_tier(row_tier: str, requested: str) -> bool:
    if requested == "required":
        return row_tier == "required"
    if requested == "important":
        return row_tier in {"required", "important"}
    if requested in {"adjacent", "all"}:
        return row_tier in {"required", "important", "adjacent"}
    raise ValueError(f"invalid tier: {requested}")


def run(args: list[str], cwd: pathlib.Path) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.DEVNULL)


def repo_head(path: pathlib.Path) -> str:
    try:
        return run(["git", "rev-parse", "HEAD"], path).strip()
    except Exception:
        return ""


def listed_files(path: pathlib.Path) -> list[pathlib.Path]:
    if (path / ".git").exists():
        try:
            raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=path, stderr=subprocess.DEVNULL)
            rels = [item.decode("utf-8", "surrogateescape") for item in raw.split(b"\0") if item]
            return [path / rel for rel in rels]
        except Exception:
            pass
    return [p for p in path.rglob("*") if p.is_file()]


def focused_files(path: pathlib.Path, focus_paths: list[str]) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()
    for focus in focus_paths:
        focus = focus.strip()
        if not focus:
            continue
        candidates: list[pathlib.Path] = []
        if "*" in focus:
            candidates = list(path.glob(focus))
        else:
            candidates = [path / focus]
        for candidate in candidates:
            if candidate.is_file():
                if candidate not in seen:
                    files.append(candidate)
                    seen.add(candidate)
            elif candidate.is_dir():
                for nested in candidate.rglob("*"):
                    if nested.is_file() and nested not in seen:
                        files.append(nested)
                        seen.add(nested)
    return files


def is_text(path: pathlib.Path) -> bool:
    try:
        data = path.read_bytes()[:8192]
    except OSError:
        return False
    if b"\0" in data:
        return False
    for encoding in ("utf-8", "latin-1"):
        try:
            data.decode(encoding)
            return True
        except UnicodeDecodeError:
            continue
    return False


def count_lines(path: pathlib.Path) -> int:
    try:
        with path.open("rb") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def should_skip(path: pathlib.Path, root: pathlib.Path, excluded_parts: set[str]) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = path.parts
    if any(part in excluded_parts for part in rel_parts):
        return True
    return path.suffix.lower() in BINARY_EXTENSIONS


def is_code_like(path: pathlib.Path) -> bool:
    if path.suffix in CODE_EXTENSIONS or path.name in CODE_NAMES:
        return True
    if path.suffix:
        return False
    if path.name.isdigit() or path.name in {"rc", "config", "filter", "group"}:
        return True
    try:
        return path.read_bytes()[:2] == b"#!"
    except OSError:
        return False


def count_repo(repo: Repo, excluded_parts: set[str], scope: str, focus_map: dict[str, list[str]]) -> Row:
    path = ROOT / repo.path
    if not path.exists():
        return Row(repo.tier, repo.category, repo.repo_id, repo.path, repo.url, "", 0, 0, 0, 0, 0, 0, True)

    files = text_files = text_lines = code_files = code_lines = binary_skipped = 0
    paths = listed_files(path)
    if scope == "focus-paths":
        paths = focused_files(path, focus_map.get(repo.repo_id, []))

    for file_path in paths:
        files += 1
        if should_skip(file_path, path, excluded_parts):
            binary_skipped += 1
            continue
        if not file_path.exists() or not file_path.is_file():
            continue
        if not is_text(file_path):
            binary_skipped += 1
            continue

        lines = count_lines(file_path)
        text_files += 1
        text_lines += lines
        if is_code_like(file_path):
            code_files += 1
            code_lines += lines

    return Row(
        repo.tier,
        repo.category,
        repo.repo_id,
        repo.path,
        repo.url,
        repo_head(path),
        files,
        text_files,
        text_lines,
        code_files,
        code_lines,
        binary_skipped,
        False,
    )


def write_outputs(rows: list[Row], csv_path: pathlib.Path, json_path: pathlib.Path, markdown_path: pathlib.Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()) if rows else list(Row.__dataclass_fields__))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))

    json_path.write_text(json.dumps([asdict(row) for row in rows], indent=2) + "\n")

    total = {
        "repos": len(rows),
        "cloned": sum(1 for row in rows if not row.missing),
        "files": sum(row.files for row in rows),
        "text_files": sum(row.text_files for row in rows),
        "text_lines": sum(row.text_lines for row in rows),
        "code_files": sum(row.code_files for row in rows),
        "code_lines": sum(row.code_lines for row in rows),
        "binary_skipped": sum(row.binary_skipped for row in rows),
    }

    lines = [
        "# Local Source Inventory",
        "",
        "Generated by `scripts/source_inventory.py`.",
        "",
        "## Current Totals",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Manifest rows counted | {total['repos']} |",
        f"| Local checkouts present | {total['cloned']} |",
        f"| Tracked/walked files | {total['files']} |",
        f"| Text files | {total['text_files']} |",
        f"| Text lines | {total['text_lines']} |",
        f"| Code-like files | {total['code_files']} |",
        f"| Code-like lines | {total['code_lines']} |",
        f"| Binary/generated skipped | {total['binary_skipped']} |",
        "",
        "## By Repository",
        "",
        "| Tier | Category | Repository | Code-like lines | Text lines | Missing |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in sorted(rows, key=lambda item: item.code_lines, reverse=True):
        missing = "yes" if row.missing else ""
        lines.append(
            f"| {row.tier} | {row.category} | `{row.path}` | {row.code_lines} | {row.text_lines} | {missing} |"
        )
    markdown_path.write_text("\n".join(lines) + "\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", default="required", choices=["required", "important", "adjacent", "all"])
    parser.add_argument("--scope", default="focus-paths", choices=["focus-paths", "full-repo"])
    parser.add_argument("--target-set", default="default-count", choices=["default-count", "optimized"])
    parser.add_argument("--assert-range", action="store_true")
    parser.add_argument("--min-lines", type=int, default=20_000_000)
    parser.add_argument("--max-lines", type=int, default=200_000_000)
    parser.add_argument("--csv", type=pathlib.Path, default=ROOT / "metrics" / "loc" / "focus-paths" / "by-repo.csv")
    parser.add_argument("--json", type=pathlib.Path, default=ROOT / "metrics" / "loc" / "focus-paths" / "by-repo.json")
    parser.add_argument("--markdown", type=pathlib.Path, default=ROOT / "Docs" / "local-source-inventory.md")
    args = parser.parse_args(argv)

    excluded_parts = load_excluded_parts()
    focus_map = load_focus_paths()
    optimized_ids = load_optimized_ids() if args.target_set == "optimized" else set()
    repos = [
        repo
        for repo in load_manifest()
        if include_tier(repo.tier, args.tier)
        and (
            (args.target_set == "default-count" and repo.default_count == "yes")
            or (args.target_set == "optimized" and repo.repo_id in optimized_ids)
        )
    ]
    rows = [count_repo(repo, excluded_parts, args.scope, focus_map) for repo in repos]
    if not rows:
        print("No repositories selected.", file=sys.stderr)
        return 1

    write_outputs(rows, args.csv, args.json, args.markdown)
    total = sum(row.code_lines for row in rows)
    print(total)

    if args.assert_range and not (args.min_lines <= total <= args.max_lines):
        print(
            f"code-like line count {total} outside range {args.min_lines}..{args.max_lines}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
