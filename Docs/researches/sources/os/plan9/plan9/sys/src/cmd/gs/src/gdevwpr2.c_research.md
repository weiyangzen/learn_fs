# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevwpr2.c

Newer Ghostscript Microsoft Windows printer device `mswinpr2`. It uses the generic printer-device framework and sends rendered page rasters to a Windows printer DC as DIB slices.

Key responsibilities:
- Defines `gx_device_win_pr2` with printer `HDC`, cancellation dialog state, `UserSettings`, DEVMODE/DEVNAMES handles, duplex/tumble state, DPI limiting, and copy-device handle duplication.
- `win_pr2_open` obtains or creates the printer DC, starts a print document, derives physical size/margins/resolution, applies max-DPI scaling, chooses bits-per-pixel, and opens Ghostscript printer buffering.
- `win_pr2_print_page` copies Ghostscript scan lines into a BMP/DIB buffer, builds a palette for <=8 bpp, and outputs chunks through `SetDIBitsToDevice` or `StretchDIBits`.
- `win_pr2_set_bpp`, `win_pr2_map_rgb_color`, and `win_pr2_map_color_rgb` support 1, 4, 8, and 24-bit printer color modes.
- `win_pr2_get_params` / `win_pr2_put_params` expose `NoCancel`, `QueryUser`, `Tumble`, and nested `UserSettings`.
- `win_pr2_getdc` parses `\\spool\...` and `%printer%...`, queries Windows printer capabilities, matches PostScript page size to printer paper, updates DEVMODE, and creates the DC.
- `win_pr2_print_setup_interaction` drives Print/Print Setup/default-printer dialogs and stores user choices.
- `CancelDlgProc` and `AbortProc2` implement cancellation and interrupt polling.

Notable implementation details:
- Page size/resolution come primarily from the Windows printer, not `-g`/`-r`, though `PageSize` affects clipping and attempted paper selection.
- `MaxResolution` reduces effective device DPI by an integer ratio and scales output back up when printing.
- The driver copies `HGLOBAL` DEVMODE/DEVNAMES handles on `copydevice` to avoid shared mutable Windows handles.

Filesystem relevance:
- Minimal. It creates/deletes a scratch printer buffer filename through `gp_open_scratch_file` and `unlink`, but its real focus is Windows printer I/O and raster transfer.
