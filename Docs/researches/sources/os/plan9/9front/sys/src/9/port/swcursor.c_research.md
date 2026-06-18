# File Research: sources/os/plan9/9front/sys/src/9/port/swcursor.c

Software cursor drawing support for framebuffer-backed screens.

Key responsibilities:
- Maintains backing store for the screen rectangle underneath the cursor.
- Maintains cursor image and mask images in GREY8 and GREY1 forms.
- Hides the cursor by restoring saved screen contents and optionally flushing the affected rectangle.
- Avoids drawing overlap with arbitrary rectangles by hiding and scheduling a mouse redraw.
- Draws the cursor by saving the destination pixels, drawing the masked cursor, and flushing the combined old/new rectangle.
- Converts Plan 9 `Cursor` `set`/`clr` bitmaps into image/mask planes.
- Initializes or reinitializes cursor backing images for the current `gscreen`.

Dependencies:
- Uses draw/memdraw kernel interfaces, `gscreen`, `flushmemscreen`, and `mouseredraw`.

Notable behavior:
- Comments acknowledge that kernel prints can call cursor routines without the usual draw lock; the code relies on reentrant `memimagedraw`, accepting possible cursor artifacts.
- Cursor image allocation failure prints but leaves nil checks in draw/hide paths.
