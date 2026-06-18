# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/moveto.c

Implements selection movement, terminal dot/origin notification, and double-click selection logic.

Key functions:
- `moveto` updates file dot and sends `Hmoveto` when the file has a terminal rasp.
- `telldot` sends `Hsetdot` only when the host dot differs from terminal-known `tdot`.
- `tellpat` pushes the last search pattern with `Hsetpat`.
- `lookorigin` chooses a nearby display origin around a requested position, bounded by line count and `CHARSHIFT`.
- `alnum`, `clickmatch`, `strrune`, and `doubleclick` implement word, quote, bracket, and newline expansion for double-click selections.

Behavior notes:
- Double-click uses `left[]`/`right[]` delimiter tables from `plan9.c`.
- `lookorigin` walks backward from a requested point to find a stable terminal origin without scanning unbounded text.
