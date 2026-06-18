# File Research: sources/os/plan9/9front/sys/src/cmd/spred/spr.c

`spred/spr.c` implements sprite file objects, sprite file I/O, drawing, painting, scrolling, resizing, palette attachment, and key shortcuts.

Key responsibilities:
- Creates and destroys sprites with `newspr` and `putspr`, including palette reference cleanup.
- Reads sprite format with `readspr`: `sprite W H palettefile`, followed by `H` rows of `W` palette indices.
- Writes sprite format with `writespr`, clears dirty state, resets quit confirmation, and reports byte count.
- Initializes default sprite zoom with `sprinit`.
- Computes the drawn sprite rectangle centered in the window via `sprrect`.
- Draws scrollbars when the zoomed sprite exceeds the viewport with `scrollbars`.
- Draws sprites with `sprdraw`, using palette images for valid indices and `invcol` for invalid/missing palette values.
- Handles scrollbar clicks with `sprbars`.
- Paints with selected palette color while mouse button 1 is held in `sprclick`.
- Resizes sprite data with `sprsize`, preserving overlapping pixels.
- Attaches a palette from another selected palette window via `sprmenu`.
- Copies zoom/scroll state for zerox windows with `sprzerox`.
- Selects palette colors from keyboard shortcuts with `sprkey`.
- Defines sprite window behavior in `sprtab`.

Important interactions:
- Depends on palette refcounts and `filredraw` to update linked palette/sprite views.
- Uses `palfile` currently as a simple duplicate of palette name; no path relativization is implemented.
