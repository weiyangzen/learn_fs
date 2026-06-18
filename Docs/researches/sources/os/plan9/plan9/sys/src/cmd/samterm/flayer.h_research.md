# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/flayer.h

Defines the `Flayer` abstraction for terminal text windows.

Key contents:
- `Vis` enum: `None`, `Some`, `All`.
- `Clicktime` is one second for multi-click timing.
- `Flayer` embeds a `Frame` and tracks text origin, selection endpoints, click time, text fetch callback, user fields, full rectangle, scrollbar rectangle, last scrollbar mark, and visibility.
- Declares flayer lifecycle, drawing, selection, refresh, resize, and lookup functions.
- Defines layout constants `FLMARGIN`, `FLSCROLLWID`, and `FLGAP`.
- Externs shared command/file color arrays `maincols` and `cmdcols`.
