# File Research: sources/os/plan9/plan9/sys/src/cmd/troff2html/chars.h

Read fully: 196 lines, 3957 bytes. SHA-256 prefix: `8d91abd68a233f57`.

This header supplies character mapping tables for `troff2html.c`.

It defines:
- `htmlchars[]`: UTF-8 characters mapped to HTML entities or ASCII approximations. `troff2html.c` computes each entry’s Unicode value at startup and sorts by that value for binary lookup.
- `troffchars[]`: unsorted troff special-character names mapped to HTML strings or ASCII approximations, covering ligatures, dashes, fractions, copyright/registered marks, math operators, arrows, brackets, and line-drawing fallbacks.

Integration: included directly after `Htmlchar` and `Troffchar` type declarations in `troff2html.c`.

Risk notes: `htmlchars[]` is source-sorted by Unicode value but still re-sorted at startup. `troffchars[]` is linear-searched and returns `"??"` for unknown names.
