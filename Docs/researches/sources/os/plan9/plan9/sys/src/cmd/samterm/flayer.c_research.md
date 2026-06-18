# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/flayer.c

Implements `samterm` layered text windows backed by Plan 9 `Frame`.

Key responsibilities:
- Maintains front-to-back layer list `llist`.
- Initializes color palettes for command and file text layers in `flstart`.
- Creates, initializes, closes, raises, resizes, and redraws `Flayer` instances.
- Bridges frame operations with text loading via `textfn`.
- Computes visibility of overlapped layers and refreshes partially covered windows.

Key functions:
- `flnew`, `flinit`, `flclose`, `flborder`, `flwhich`, `flupfront`.
- `flinsert`, `fldelete`, `flselect`, `flsetselect`, `flfp0p1`.
- `flresize`, `flprepare`, `visibility`, and `flrefresh`.

Behavior notes:
- `flprepare` lazily builds a frame image for visible layers and loads text through `textfn`.
- Selection and scrolling coordinates are adjusted by `origin`.
- Visibility can be `None`, `Some`, or `All`; partially visible layers refresh through recursive clipping against layers above them.
