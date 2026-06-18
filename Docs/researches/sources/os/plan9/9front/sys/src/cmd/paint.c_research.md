# File Research: sources/os/plan9/9front/sys/src/cmd/paint.c

## Role

Implements a small graphical bitmap editor.

## Drawing Model

The editor maintains a possibly unbounded canvas image, current screen/canvas origin, zoom factor, ink/background images, a 16-color palette initialized to a C64-style palette, brush size, and circular undo buffer.

Strokes draw lines with disc endpoints; the largest brush slot is a flood-fill tool. Canvas expansion preserves existing pixels and fills new areas with the background.

## Display

`zoomdraw` renders source image pixels at integer zoom, handling alpha/background and avoiding overwriting toolbar/palette regions. Coordinate helpers convert between screen and canvas coordinates. `drawpal` draws the palette and brush selector at the bottom of the window.

## Editing

Mouse left draws with ink, middle draws with background, right pans the canvas. Palette clicks select ink, set background, or edit a palette color by hex value. Keyboard controls include zoom, clear, undo, fill brush, numeric brush selection, and command prompt.

The flood-fill implementation builds a GREY1 mask by recursively scanning same-colored runs and then draws the fill color through that mask.

## File And Filter Commands

The command prompt supports read/write, shell input/output filters, and pipe-through-image-filter operations. Images are read/written with Plan 9 `readimage`/`writeimage`.
