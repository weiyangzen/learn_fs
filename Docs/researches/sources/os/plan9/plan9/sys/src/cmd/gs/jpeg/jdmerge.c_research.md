# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmerge.c

Purpose: optimized merged upsampling and YCbCr-to-RGB conversion.

Key structures and routines:
- `my_upsampler` extends `jpeg_upsampler` with an `upmethod`, YCbCr conversion tables, spare row buffer, row width, and rows remaining.
- `build_ycc_rgb_table()` duplicates the fixed-point table logic from `jdcolor.c`.
- `start_pass_merged_upsample()` resets spare-row and row-count state.
- `merged_2v_upsample()` handles 2:1 vertical sampling, including spare-row buffering when caller provides only one output row.
- `merged_1v_upsample()` handles 1:1 vertical sampling.
- `h2v1_merged_upsample()` converts one row group for 2h1v sampling.
- `h2v2_merged_upsample()` converts two output rows for 2h2v sampling.
- `jinit_merged_upsampler()` allocates state, selects 1v/2v method, allocates spare row if needed, and builds conversion tables.

Important behavior:
- Only supports YCbCr to RGB.
- Only supports 2:1 horizontal chroma expansion with 1:1 or 2:1 vertical expansion.
- Assumes `jdmaster.c` has already verified all preconditions.
- Computes chroma contribution once per pair or quartet of output pixels, reducing conversion work.
- Handles odd output widths with a separate final-column path.

Dependencies:
- Depends on `jdmaster.c` capability selection, RGB layout macros, sample range-limit table, JPEG memory manager.

Notes:
- This is a fast path; unsupported cases fall back to `jdsample.c` plus `jdcolor.c`.
