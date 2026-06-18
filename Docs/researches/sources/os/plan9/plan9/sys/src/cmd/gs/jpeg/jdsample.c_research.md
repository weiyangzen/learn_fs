# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jdsample.c

Purpose: separate upsampling routines for decompression.

Key structures and routines:
- `my_upsampler` extends `jpeg_upsampler` with per-component color buffers, method pointers, row counters, rowgroup heights, and integer expansion factors.
- `start_pass_upsample()` resets row buffer and image-height state.
- `sep_upsample()` fills per-component upsampled buffers and calls color conversion.
- `fullsize_upsample()` aliases input data for full-size components.
- `noop_upsample()` handles components not needed downstream.
- `int_upsample()` implements generic integral-ratio replication.
- `h2v1_upsample()` and `h2v2_upsample()` implement fast box-filter replication for common 2:1 ratios.
- `h2v1_fancy_upsample()` and `h2v2_fancy_upsample()` implement triangle-filter interpolation for better visual quality.
- `jinit_upsampler()` validates sampling ratios, selects per-component methods, requests context rows where needed, and allocates buffers.

Important behavior:
- Upsampling input is counted in row groups.
- CCIR601 sampling is rejected as not implemented.
- Fancy 2h2v upsampling needs context rows from `jdmainct.c`.
- Fancy upsampling is disabled when `min_DCT_scaled_size == 1` because main controller cannot provide context rows there.
- Fractional sampling ratios are rejected with `JERR_FRACT_SAMPLE_NOTIMPL`.

Dependencies:
- Color converter, main controller context-row support, JPEG memory manager, component sampling geometry.

Notes:
- Merged fast-path cases may use `jdmerge.c` instead of this file.
