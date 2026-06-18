# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdps1.c

Implements Level 2 / Display PostScript graphics-state object and rectangle operators.

Key behavior:
- Extends `copy` for gstate objects.
- Provides `setstrokeadjust`, `currentstrokeadjust`, `gstate`, `currentgstate`, `setgstate`, rectangle append/clip/fill/stroke operators, and `setbbox`.
- `zgstate` allocates an `igstate_obj`, copies the current `gs_state`, marks contained refs new, and saves the embedded ref for restore tracking.
- `zcopy_gstate` and `zcurrentgstate` unshare saved gstates, perform VM-space checks, save old refs, and copy graphics-state contents.
- Rectangle operators accept either four numeric operands or packed numeric arrays/strings, using a small local rectangle buffer before heap allocation.

Dependencies:
- Uses gstate internals, save/restore store machinery, path rectangle APIs, numeric-array helpers, and char/userpath support.

Research notes:
- Comments document a known workaround: global gstate writes are disallowed during nonzero save levels because non-ref members are not fully space-checked.
