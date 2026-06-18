# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/magic

This is a small rc pipeline for finding likely magic numbers in source.

Key behavior:
- Uses `g`, `grep -v`, and `sed` to print source lines containing numeric literals.
- Filters out headers, includes, common diagnostic prints, and simple `return 0/1/-1` cases.

Important details:
- It is heuristic and tuned for quick source cleanup/review.
- It assumes Plan 9 command availability and syntax.

Filesystem relevance:
- Indirect: source-maintenance helper only.
