# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/textwin.c

Implements fixed-font editable text-window mechanics used by the edit panel.

Key behavior:
- Maintains Rune text, visible top/bottom indices, selection, and absolute screen locations for visible runes.
- Maps points to rune indices, computes rune positions with wrapping, draws text, highlights selections, and clears trailing areas.
- Supports mouse selection, text replacement, scrolling to a top line, reshape redraws, construction/free, and moving absolute locations.
- Replacement inserts/deletes text and redraws the visible region.

Important dependencies: libpanel draw helpers, font metrics, `Mouse`.

Notable risks:
- Comments note linear search should be binary search and optimized replacement below visible text is incomplete (`if(1 || ...)` path).
- Location coordinates are absolute, requiring `twmove()` on panel movement.
