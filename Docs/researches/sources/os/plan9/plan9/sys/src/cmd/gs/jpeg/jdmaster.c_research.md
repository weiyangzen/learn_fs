# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmaster.c

Purpose: master decompression controller that selects modules and coordinates output passes.

Key structures and routines:
- `my_decomp_master` extends `jpeg_decomp_master` with pass count, merged-upsample flag, and saved quantizer pointers.
- `use_merged_upsample()` determines whether `jdmerge.c` can replace separate upsampling and color conversion.
- `jpeg_calc_output_dimensions()` computes output dimensions, IDCT scaling choices, component downsampled dimensions, output component count, and recommended output buffer height.
- `prepare_range_limit_table()` builds the shared table used for clamping and post-IDCT signed-to-unsigned conversion.
- `master_selection()` initializes all selected decompression modules.
- `prepare_for_output_pass()` starts the modules needed for each output pass and handles two-pass quantization dummy/final passes.
- `finish_output_pass()` completes quantization and increments pass count.
- `jpeg_new_colormap()` switches external colormaps in buffered-image mode.
- `jinit_master_decompress()` allocates the master controller and performs module selection.

Important behavior:
- Supports IDCT scaling to 1/8, 1/4, 1/2, or full output where compiled.
- Chooses merged upsampling only for YCbCr to RGB, 2h1v/2h2v sampling, no fancy upsampling, no CCIR601, and compatible scaling.
- Arithmetic-coded JPEG is explicitly rejected as not implemented.
- Initializes full coefficient buffering when needed for multiple scans or buffered-image mode.
- Range-limit table includes a masked region to keep corrupt IDCT output from indexing out of bounds.

Dependencies:
- Initializes color converter, upsampler/merged upsampler, post controller, IDCT manager, entropy decoder, coefficient controller, main controller, and memory virtual arrays.

Notes:
- This file is the decompression pipeline assembly point.
