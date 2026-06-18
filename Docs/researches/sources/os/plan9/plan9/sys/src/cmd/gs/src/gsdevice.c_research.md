# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsdevice.c

## Role

`gsdevice.c` implements Ghostscript library device/page control: device finalization, cloning, opening/closing, current-device changes, raster sizing, page output, null devices, geometry updates, color parameter copying, and output filename parsing/opening.

## Main API

Implements public functions declared in `gsdevice.h`, including:

- `gs_flushpage`, `gs_copypage`, `gs_output_page`
- `gs_currentdevice`, `gs_devicename`, `gs_getdevice`
- `gs_copydevice`, `gs_copydevice2`
- `gs_opendevice`, `gs_closedevice`
- `gs_setdevice`, `gs_setdevice_no_erase`, `gs_setdevice_no_init`
- `gs_nulldevice`
- device raster/geometry helpers and output-file helpers

## Device Lifetime

`gx_device_finalize` calls optional device finalization, closes open devices, and frees dynamic structure descriptors. `gs_copydevice2` copies device prototypes/instances into immovable memory, building or copying a GC structure descriptor when needed. `keep_open` is supported but explicitly documented as dangerous.

## Graphics-State Integration

Setting a device may open it, set memory-device targets, install it into the graphics state, reset CTM/clip, clear cachedevice/charpath state, update color mapping procedures, invalidate device color, and reapply overprint.

## Output Files

`gx_parse_output_file_name` handles default IO devices, `%stdout`, `%pipe`, `-`, and one printf-style page-number format. `gx_device_open_output_file` expands page count formats and chooses IODevice or platform printer open paths.

## Risks

Device cloning is shallow and relies on `finish_copydevice` to reject unsafe copies. Output filename formatting uses `sprintf` after validation and size checks. Closing the old current device happens only when its reference count is 1, so errors can propagate but lifetime assumptions are subtle.
