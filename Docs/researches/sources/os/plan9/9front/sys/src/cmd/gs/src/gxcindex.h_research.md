# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcindex.h

Defines the internal device color index type and scan-line accumulation macros.

Key behavior:
- Sets `GX_DEVICE_COLOR_MAX_COMPONENTS` to 16, bounded by the available bits in `gx_color_index`.
- Defines `gx_color_index_data` from `GX_COLOR_INDEX_TYPE` or `ulong`, with disabled test variants for pointer or struct color indices.
- Defines `gx_color_index`, `arch_sizeof_color_index`, and the transparent/undefined `gx_no_color_index` value.
- Provides `DECLARE_LINE_ACCUM`, `LINE_ACCUM`, `LINE_ACCUM_SKIP`, and `LINE_ACCUM_STORE` wrappers over sample-store macros for packing colored image pixels into a scan line.
- Provides `DECLARE_LINE_ACCUM_COPY` and `LINE_ACCUM_COPY` to flush accumulated pixels to a device's `copy_color` procedure.

Dependencies:
- Includes `gsbitops.h` for sample-store helpers.
- Depends on device procedure macros when using the copy macros.

Research notes:
- The file preserves old experimental alternate representations, but the active build uses a scalar color-index value.
- The scan-line macros assume a local block scope because they declare helper variables.
