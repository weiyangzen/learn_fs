# File Research: sources/os/plan9/plan9/sys/src/cmd/mug.c

Interactive face/icon crop and tone-adjustment tool.

Purpose:
- Reads an image, lets the user select a square region, downsample it to a 48x48 grayscale face, adjust black/white/gamma/depth, save slots, undo, and write output.

Major data:
- `State` stores black/white/stretch/gamma/depth/gamma table/selection rectangle.
- `Face` stores saved thumbnails and their state.
- Global images for original, ramp, current small face, temp GREY8, colors, and saved faces.
- `rdata` stores gamma-corrected source luminance.

Key functions:
- `geometry()` lays out ramp, original image, current thumbnail, and saved face slots.
- `initramp()`, `initclamp()`, `initval2cmap()`, `setgtab()` prepare tone controls.
- `process()` box-filters a selected square into 48x48, applies black/white/gamma mapping, and dithers to target grayscale depth.
- `drawscreen()`, `drawface()`, `drawrampbar()`, `moveframe()` update UI.
- `move()` resizes/moves the square selection while preserving square shape.
- `dragface()` supports dragging thumbnails between slots.
- `saveface()`, `mark()`, `undo()`, `writeface()` manage state history, saved slots, and output.
- `main()` initializes draw/event systems and runs mouse/menu event loop.

UI:
- Button 3 menu: Reset, Depth, Undo, Write, Exit.
- Button 1 drags selection handles, tone ramp controls, and thumbnails.
- Custom cursors indicate selection region/handle.

Output:
- GREY1/GREY2 output is custom hex rows.
- GREY4/GREY8 output uses Plan 9 `writeimage()`.
