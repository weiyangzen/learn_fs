# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scrollbar.c

Implements horizontal and vertical scrollbar panels.

Key behavior:
- Orientation is inferred from pack side.
- Draws scrollbar trough and thumb via `pl_scrollupd`.
- Mouse buttons map to relative up/page, absolute, and relative down/page scroll semantics.
- Calls the linked scrollee’s `scroll` method with direction, button, position, and length.
- Converts scrollee natural coordinates into screen-coordinate thumb positions.

Important dependencies: `plscroll` linkage, draw helpers, panel priority.

Notable risks:
- For vertical/horizontal conversion, scrollbar geometry must match current packed rectangle.
- `USERFL` changes out-of-rect handling for mouse capture.
