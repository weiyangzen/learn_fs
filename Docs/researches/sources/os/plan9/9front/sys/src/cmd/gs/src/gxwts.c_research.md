# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxwts.c

Implements rendering support for Well Tempered Screening device colors.

Key behavior:
- Defines the WTS `gx_device_color_type_t` method table outside unit-test builds.
- `wts_get_samples` dispatches to Screen J or Screen H sample-location logic.
- Screen J sample lookup applies rational affine-like offsets from screen parameters and clamps the run length before screen discontinuities.
- Screen H sample lookup uses a linear search helper to map coordinates into unequal cell partitions.
- `wts_draw` generates a 1-bit halftone tile for a rectangle by comparing shade levels against screen samples.
- `gx_dc_wts_fill_rectangle_1` handles one-component WTS colors by drawing a mono tile and sending it through `copy_mono`.
- `wts_repack_tile_4` combines up to four 1-bit component tiles into chunky 4-bit/nibble color data.
- `gx_dc_wts_fill_rectangle_4` draws per-component tiles, repacks them, and sends them through `copy_color`.
- `gx_dc_wts_fill_rectangle` dispatches between one-component and up-to-four-component paths.
- `gx_dc_wts_equal` compares type, phase, component count, and levels.
- `gx_dc_wts_get_nonzero_comps` reports which WTS levels are nonzero.

Dependencies:
- Device color and halftone internals from `gxdcolor.h`, `gxdht.h`, and `gxwts.h`.
- Device-client APIs from `gxdevcli.h`.
- Imager state and halftone headers.
- Uses C `malloc`/`free` directly for temporary tile buffers.

Research notes:
- `gx_dc_wts_write` and `gx_dc_wts_read` are not implemented and return `unknownerror`.
- Temporary tile allocations are not checked for `NULL` before use, so large rectangles or allocation failure can lead to unsafe behavior.
- Only one-component and up-to-four-component WTS device colors are supported; larger component counts return `-1`.
