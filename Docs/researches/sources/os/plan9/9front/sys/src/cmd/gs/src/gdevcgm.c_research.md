# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcgm.c

Ghostscript Computer Graphics Metafile output device. It wraps the local CGM writer library and exposes three devices: `cgmmono`, `cgm8`, and `cgm24`.

Key behavior:
- Defines `gx_device_cgm`, storing output filename, file handle, `cgm_state`, and picture state.
- `cgm_open` opens `OutputFile`, initializes the CGM writer with Ghostscript memory callbacks, begins the metafile, and writes core metafile properties.
- `cgm_begin_picture` starts a picture lazily on first drawing operation, sets scaling, color selection mode, VDC extent, VDC precision, edge width, and indexed color table for <=8-bit devices.
- `cgm_output_page` ends an active picture and finishes the Ghostscript page.
- `cgm_close` ends any active picture, writes `END_METAFILE`, terminates the CGM writer, and closes the file.
- Drawing support covers rectangle fills, monochrome bitmap copy, and color bitmap copy, primarily via CGM rectangles and cell arrays.

Notable dependencies:
- CGM API from `gdevcgml.h`.
- Ghostscript device, parameter, and platform file APIs.
- `gdevpccm.h` for 8-bit palette color mapping.

Research notes:
- `OutputFile` is a device parameter and respects `LockSafetyParams`.
- The bitmap fallback paths are intentionally inefficient.
- In `cgm_copy_mono`, the slow per-pixel rectangle path appears suspicious: it computes each pixel color but uses `cgm_set_rect(points, x, y, 1, 1)` rather than offsetting by `ix`/`iy`, and it does not visibly emit `cgm_FILL_COLOR` for each chosen color before the rectangle. That path likely does not render arbitrary transparent/two-color masks correctly.
