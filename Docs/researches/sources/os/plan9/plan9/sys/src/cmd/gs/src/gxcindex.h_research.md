# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcindex.h

Device color-index type and scan-line accumulation macros. It sets `GX_DEVICE_COLOR_MAX_COMPONENTS` to 16 and defines `gx_color_index_data`/`gx_color_index`, normally as an unsigned long-like opaque pixel value but with disabled pointer/struct test modes for portability analysis. `gx_no_color_index` is the transparent/undefined color sentinel.

The header also provides macros for accumulating packed scan lines at 1, 2, 4, or byte-multiple bits per pixel using `sample_store` helpers. `DECLARE_LINE_ACCUM`, `LINE_ACCUM`, `LINE_ACCUM_SKIP`, and `LINE_ACCUM_STORE` are for building a line buffer; the `_COPY` variants additionally copy accumulated spans to a device with `copy_color`. These macros are used by image/color rendering code that must pack device-specific color indices efficiently.
