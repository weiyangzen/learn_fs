# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdmainct.c

Purpose: main decompression buffer controller between coefficient decoding and postprocessing.

Key structures and routines:
- `my_main_controller` extends `jpeg_d_main_controller` with per-component work buffers and optional context-row pointer machinery.
- `alloc_funny_pointers()`, `make_funny_pointers()`, `set_wraparound_pointers()`, and `set_bottom_pointers()` build pointer lists that provide above/below context rows without copying sample rows.
- `start_pass_main()` selects simple, context-row, or post-crank processing mode.
- `process_data_simple_main()` handles the normal no-context path, fetching one iMCU row and feeding row groups to postprocessing.
- `process_data_context_main()` handles fancy upsamplers that require vertical context rows.
- `process_data_crank_post()` runs the postprocessor alone for the final two-pass quantization pass.
- `jinit_d_main_controller()` allocates row-group buffers and optional context pointer lists.

Important behavior:
- Raw-data output bypasses this controller.
- Context mode needs `min_DCT_scaled_size >= 2`; otherwise it errors with `JERR_NOTIMPL`.
- Uses row groups as the unit passed to postprocessing.
- Bottom edge handling duplicates the last real sample row by pointer aliasing.
- Does not support full-image main buffers; those live in coefficient or post controllers.

Dependencies:
- Coefficient controller `decompress_data`, postprocessor `post_process_data`, upsampler `need_context_rows`, JPEG memory manager.

Notes:
- The “funny pointer” design is an optimization to avoid copying retained context rows.
