# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/devdraw.c

## Role

`devdraw.c` implements a user-space Plan 9 `/dev/draw` device over `memdraw`/`memlayer` for the VNC server. It lets the private desktop command use normal Plan 9 draw protocol operations while dirty-screen tracking feeds the VNC update path.

## Device Model

- Exposes `#i/draw/new`, per-client directories, and per-client `ctl`, `data`, `refresh`, and `colormap` files.
- Tracks draw clients in `sdraw.client[]`.
- Tracks images as `DImage` hash chains per client.
- Tracks public/named images through `DName`.
- Tracks screens/windows through `DScreen` and per-client `CScreen` links.
- Keeps the real backing screen image in `screenimage` and installs it as image id 0 for new clients.

## Image And Screen Management

- `makescreenimage()` attaches to the VNC memory screen from `screen.c`, wraps it as a `Memimage`, names it, and creates the root `DImage`.
- `drawinstall()` and `drawuninstall()` add/remove client image ids.
- `drawinstallscreen()` creates or attaches to a `Memscreen`.
- `drawfreedimage()` and `drawfreedscreen()` handle references across images, named images, screen fill images, and window layers.
- `drawaddname()`, `drawlookupname()`, and `drawgoodname()` implement named-image lifetime validation.

## Dirty Tracking And Refresh

- `dstflush()` determines whether a draw destination affects the visible VNC screen and adds a dirty rectangle.
- `addflush()` forwards dirty regions to `flushmemscreen()` with VNC-oriented handling.
- `drawflush()` emits pending dirty rectangles.
- Layer refresh callbacks collect refresh rectangles for clients using refresh messages.
- `drawwakeall()` wakes clients blocked on refresh reads.

## Supported Draw Protocol Messages

`drawmesg()` supports the core Plan 9 draw data protocol, including:

- Allocate image (`b`) and screen (`A`).
- Affine warp (`a`).
- Repl/clip changes (`c`).
- Draw (`d`) with compositing operator state (`O`).
- Ellipse/arc (`e`/`E`), line (`L`), polygon/fill polygon (`p`/`P`), string/stringbg (`s`/`x`).
- Free image/screen (`f`/`F`).
- Font initialization and glyph load (`i`/`l`).
- Attach/name images (`n`/`N`).
- Window origin and stacking (`o`/`t`).
- Image read (`r`) and image load/compressed load (`y`/`Y`).
- Visibility flush (`v`) and debug no-op (`D`).

## Notable Limitations And Risk Areas

- This is a substantial in-process graphics server; reference-count correctness is central to avoiding stale images and leaked layers.
- Named images are invalidated by version checks, and old names produce `Eoldname`.
- Screen resizing is intentionally constrained once draw clients have existed.
- Many operations assume all callers hold `drawlock`; the code mixes blocking refresh waits with lock release/reacquire.
- Dirty rectangle handling is tuned for VNC and differs from a pure bounding-box flush strategy.
