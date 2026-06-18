<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check_links.py -->
# sources/test-tools/syzkaller/tools/check_links.py

## Purpose

Markdown local-link checker and same-repo GitHub absolute-link detector.

## Important APIs, Types, and Functions

Python regex `link_re`, helpers `filter_link`, `fix_link`, `check_link`, `os.path.exists`, and CLI `<root_dir> <doc_files>...`.

## Control Flow

Extracts inline Markdown links, flags absolute GitHub master links to syzkaller, ignores HTTP/anchor/mailto links for existence checks, strips query/fragment suffixes, resolves root-relative and doc-relative local paths, and reports missing targets.

## State and Persistence Behavior

Keeps link/error lists in memory; no writes.

## Dependencies and Integration Points

Requires Python and docs filesystem access; used by docs CI.

## Risks and Edge Cases

Regex misses reference-style links and nested parentheses; anchor existence inside local files is not checked.

## Test Signals

Docs fixtures with valid/broken local links, root-relative paths, HTTP/mailto/anchor links, and GitHub master links.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check_links.py -->
