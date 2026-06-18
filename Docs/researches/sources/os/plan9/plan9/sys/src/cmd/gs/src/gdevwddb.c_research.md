# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwddb.c

Implements the `mswin` Microsoft Windows 3.x display device using a device-dependent bitmap (DDB) backing store.

Key behavior:
- Defines a Windows display device with bitmap/DC handles, dynamic pens/brushes, a palette, and a small monochrome staging bitmap/DC used for `copy_mono`.
- `win_ddb_open` delegates common window setup to `win_open`, rejects depths above 8 bits per pixel, allocates the backing bitmap, creates the mono staging bitmap, builds the palette, creates pens/brushes, and routes text drawing to the bitmap DC.
- `win_ddb_close` destroys tools, DCs, bitmaps, palette resources, palette memory, and then closes the common window device.
- `win_ddb_map_rgb_color` delegates to common Windows palette mapping and mirrors newly added colors into the DDB palette and tool set.
- `win_ddb_fill_rectangle` uses `PatBlt`, special-casing black and otherwise selecting a cached brush.
- `win_ddb_tile_rectangle` pre-clears fully opaque tiles and has a fast path for small 1-bit tiles that fit the staging bitmap with zero phase.
- `win_ddb_copy_mono` clips, chunks transfers to the 32x32 staging bitmap, handles transparent/opaque colors through Windows raster ops, caches bitmap IDs, packs source rows, and blits to the backing DC.
- `win_ddb_copy_color` draws 8-bit or 4-bit indexed pixels with `SetPixel`, or delegates monochrome color maps to `copy_mono`.
- `win_ddb_copy_to_clipboard` copies the backing bitmap and palette to the Windows clipboard.
- `win_ddb_repaint` blits from the backing DC to the requested screen DC.
- `win_ddb_alloc_bitmap` creates a compatible bitmap/DC, halving resolution up to four times if bitmap allocation fails.
- Internal helpers create/delete per-palette pens and brushes.

Dependencies:
- Uses `gdevmswn.h`, Ghostscript Windows common device helpers, Windows GDI handles/APIs, palette helpers, and Ghostscript memory allocation.

Research notes:
- This driver is limited to 8-bit-and-below indexed/palette display modes.
- The resolution-halving fallback changes device dimensions when the backing bitmap cannot be allocated.
