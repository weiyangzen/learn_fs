# File Research: sources/os/plan9/plan9/sys/src/cmd/tweak.c

Read fully: 2048 lines, 39188 bytes. SHA-256 prefix: `d3f6e8c1e7bffdd7`.

`tweak` is an interactive bitmap, cursor, face-file, and subfont editor built on Plan 9 draw/event APIs. It opens images/subfonts, displays them with optional magnification, edits pixels, edits metadata fields, copies regions, writes files, reloads files, and opens subfont character slices as child edit panes.

Core model:
- `Thing` represents an opened image/subfont or child edit view, with image, subfont, filename, regions, selected character, parent, modified flag, magnification, and subfont offset.
- Global UI regions divide control, edit, and text/status areas.
- `values[]` and `greyvalues[]` cache one-pixel images for color drawing.

Important routines:
- `tget()` detects normal image, cursor, and face-file formats and loads them.
- `drawthing()`, `redraw()`, `drawall()`, `text()`, and message helpers render the UI.
- `textedit()` edits filename, depth, rectangle, subfont metrics, character metrics, offset, count, and image width.
- `openedit()`, `twiddle()`, `twidpix()`, and `ckinfo()` implement character/region editing and update subfont top/bottom bounds.
- `twrite()`, `tread()`, `tclose()`, `tchar()`, `copy()`, `tpixels()`, and `menu()` implement user commands.

Risk notes: it assumes Plan 9 GUI/event semantics and mutates parent/child image state manually; many updates require careful redraw and ownership handling.
