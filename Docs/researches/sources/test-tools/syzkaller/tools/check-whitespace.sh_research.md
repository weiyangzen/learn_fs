<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-whitespace.sh -->
# sources/test-tools/syzkaller/tools/check-whitespace.sh

## Purpose

Whitespace lint for tracked repository files.

## Important APIs, Types, and Functions

Uses `git ls-files`, extension/path filters, line scanning, grep/tail style checks, counters, and a failure flag.

## Control Flow

Scans candidate files for trailing whitespace, disallowed tabs in text formats, and missing final newlines, printing file/line diagnostics and failing on any violation.

## State and Persistence Behavior

Reads tracked files only and writes nothing.

## Dependencies and Integration Points

Requires bash, Git, and coreutils; used by lint/presubmit.

## Risks and Edge Cases

Filters must exclude generated/binary-like files correctly; filename whitespace remains fragile.

## Test Signals

Fixtures covering trailing spaces, tabs where allowed/disallowed, final newline, generated exclusions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-whitespace.sh -->
