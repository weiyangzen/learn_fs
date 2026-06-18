# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxwts.c

Ghostscript Well Tempered Screening renderer and device color implementation.

Key behavior:
- Defines `gx_dc_type_wts`, a device color type with save, halftone lookup, load, fill-rectangle, equality, serialization, deserialization, and nonzero-component procedures.
- `mul_shr_16` performs fixed-style multiply/shift using `double`; the integer implementation is marked TODO.
- `wts_get_samples_j` maps device coordinates into Screen J threshold sample cells using fixed coefficients and determines how many contiguous samples remain valid.
- `wts_get_samples_h` maps coordinates for Screen H using `wts_screen_h_offset`, which currently uses a linear search.
- `wts_get_samples` dispatches by WTS screen type.
- `wts_draw` renders a 1-bit tile by comparing a shade level against WTS samples over a rectangle.
- `gx_dc_wts_fill_rectangle_1` draws a one-component WTS halftone by building a temporary mono tile and calling `copy_mono`.
- `gx_dc_wts_fill_rectangle_4` draws up to four components by building per-plane mono tiles, repacking them into chunky 4-bit pixels with `wts_repack_tile_4`, and calling `copy_color`.
- `gx_dc_wts_fill_rectangle` dispatches to one-component or <=4-component implementations.
- `gx_dc_wts_equal` compares type, phase, component count, and levels.
- `gx_dc_wts_get_nonzero_comps` reports which WTS component levels are nonzero.

Notable dependencies:
- Halftone and WTS types: `gsht.h`, `gxdht.h`, `gxwts.h`.
- Device color APIs: `gxdcolor.h`, `gxdevcli.h`.
- Graphics state API: `gxstate.h`.

Research notes:
- Serialization/deserialization (`gx_dc_wts_write` and `gx_dc_wts_read`) are not implemented and return `gs_error_unknownerror`.
- Temporary tile buffers are allocated with C `malloc`/`free`, not Ghostscript memory APIs.
- The code does not check `malloc` results before drawing into buffers, so allocation failure would lead to null dereference.
- More than four components are unsupported and return `-1`.
