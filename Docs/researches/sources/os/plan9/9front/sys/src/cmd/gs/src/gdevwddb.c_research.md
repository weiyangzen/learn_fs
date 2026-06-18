# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevwddb.c

## Purpose
Microsoft Windows Ghostscript display driver using a device-dependent bitmap (DDB) backing store.

## Main Concepts
- Defines `gx_device_win_ddb`, extending Windows common device state with a backing bitmap/DC, palette, pens, brushes, and a small monochrome staging bitmap.
- Registers the `mswin` device.
- Uses Windows GDI operations for fills, blits, palette management, repainting, and clipboard export.

## Key Functions
- `win_ddb_open`: opens the common Windows device, rejects >8 bpp, allocates backing bitmap, creates mono staging DC/bitmap, creates palette/tools, and routes text drawing to the bitmap DC.
- `win_ddb_close`: deletes tools, DCs, bitmap, palette, and palette memory, then closes common Windows state.
- `win_ddb_map_rgb_color`: extends the bitmap palette when the window palette gets a new color.
- `win_ddb_fill_rectangle`: fills with `PatBlt`.
- `win_ddb_tile_rectangle`: optimizes small monochrome tile blits through the staging bitmap.
- `win_ddb_copy_mono`: chunks mono copies into the staging bitmap and `BitBlt`s with appropriate raster ops.
- `win_ddb_copy_color`: draws 8-bit or 4-bit color pixel maps with `SetPixel`, or delegates mono cases to `copy_mono`.
- `win_ddb_copy_to_clipboard`: copies the backing bitmap and palette to the Windows clipboard.
- `win_ddb_repaint`: blits from backing DC to the window DC.
- `win_ddb_alloc_bitmap`, `win_ddb_free_bitmap`: allocate/free backing bitmap/DC, halving resolution after repeated allocation failures.
- `win_maketools`, `win_destroytools`, `win_addtool`: manage palette-indexed pens and brushes.

## Notable Risks
- `win_maketools` allocation failure is not propagated to `win_ddb_open`; later code assumes tool arrays exist.
- Some GDI calls are unchecked.
- `win_ddb_alloc_bitmap` silently halves resolution on allocation failure, changing output dimensions.
- DDB output is palette/device dependent and limited to <=8 bpp.

## Filesystem Relevance
No filesystem logic. This is a Windows display/clipboard backend.
