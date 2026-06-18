<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-html.sh -->
# sources/test-tools/syzkaller/tools/check-html.sh

## Purpose

HTML formatting lint that rejects tracked HTML files mixing tabs and repeated spaces for formatting.

## Important APIs, Types, and Functions

Uses `find`, `grep`, `wc`, `git ls-files --error-unmatch`, and simple shell counters.

## Control Flow

Counts tab lines and double-space lines for every HTML file, ignores `Commit.Date` spacing and untracked files, reports files that contain both styles, and fails if any were found.

## State and Persistence Behavior

No writes; only `FILES` and `FAILED` shell state.

## Dependencies and Integration Points

Depends on bash, Git, find/grep/wc; integrated with repository style checks.

## Risks and Edge Cases

Heuristic can flag intentional content spacing and assumes current-directory scan scope.

## Test Signals

Fixtures with tabs only, spaces only, mixed whitespace, untracked files, and `Commit.Date` exemption.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-html.sh -->
