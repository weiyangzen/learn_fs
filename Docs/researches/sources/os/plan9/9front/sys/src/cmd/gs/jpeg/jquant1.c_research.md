# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jquant1.c

Purpose: one-pass color quantizer for fast mapping to a preselected, equally spaced colormap, with optional ordered or Floyd-Steinberg dithering.

Key contents:
- Compiled only when `QUANT_1PASS_SUPPORTED` is enabled.
- Defines ordered dithering constants and a 16x16 Bayer base dither matrix.
- Defines Floyd-Steinberg error types and per-component error arrays.
- `my_cquantizer` stores the public quantizer vtable, saved colormap, precomputed `colorindex`, component color counts, ordered dither tables, and F-S state.
- Policy helpers: `select_ncolors()`, `output_value()`, and `largest_input_value()`.
- Setup helpers: `create_colormap()`, `create_colorindex()`, `make_odither_array()`, `create_odither_tables()`, `alloc_fs_workspace()`.
- Quantization routines: `color_quantize()`, `color_quantize3()`, `quantize_ord_dither()`, `quantize3_ord_dither()`, and `quantize_fs_dither()`.
- Public init entry: `jinit_1pass_quantizer()`.

Important behavior:
- Builds an orthogonal colormap using the product of per-component color counts, keeping total colors at or below `desired_number_of_colors`.
- For RGB output, allocation favors green, then red, then blue.
- `colorindex[component][sample]` stores premultiplied colormap-index contributions so pixel mapping is a sum of component lookups.
- Ordered dithering pads `colorindex` in both directions so dithered sample values can be indexed without explicit range checks.
- Components with the same number of representative values share ordered-dither tables.
- Floyd-Steinberg dithering alternates scan direction by row and propagates 7/16, 3/16, 5/16, and 1/16 errors using per-component FAR-memory arrays.
- `start_pass_1_quant()` selects the active quantization method based on `dither_mode`.
- External colormap changes are rejected via `JERR_MODE_CHANGE`.

Dependencies:
- `jinclude.h`, `jpeglib.h`, IJG memory manager, `jzero_far()`, error macros, sample range-limit tables.
