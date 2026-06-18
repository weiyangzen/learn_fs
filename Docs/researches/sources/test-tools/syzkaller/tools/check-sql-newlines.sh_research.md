<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-sql-newlines.sh -->
# sources/test-tools/syzkaller/tools/check-sql-newlines.sh

## Purpose

SQL newline-at-EOF guard.

## Important APIs, Types, and Functions

Uses `find . -name '*.sql'`, `test -s`, `tail -c 1`, and a shell failure flag.

## Control Flow

Scans SQL files, checks non-empty files for a final newline byte, reports missing-newline diagnostics, and exits 1 on failures.

## State and Persistence Behavior

No writes; only local shell variables.

## Dependencies and Integration Points

Requires bash/coreutils and intended scan-root execution.

## Risks and Edge Cases

Scans untracked SQL files too, so local scratch files can fail CI-like runs.

## Test Signals

Empty, newline-terminated, and unterminated SQL fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-sql-newlines.sh -->
