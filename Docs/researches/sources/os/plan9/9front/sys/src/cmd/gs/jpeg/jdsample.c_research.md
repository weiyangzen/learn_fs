# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jdsample.c

Separate upsampling controller and per-component upsampling kernels.

Key points:
- Upsampling operates on row groups and then calls the color deconverter to emit interleaved output rows.
- `sep_upsample` fills a conversion buffer for one upsampled row group, color-converts available rows, and advances input row-group counters only after buffered rows are consumed.
- Full-size components avoid copying by pointing `color_buf` directly at input data.
- Unneeded components use a no-op method and are not allocated buffers.
- Generic integer-ratio upsampling replicates samples horizontally and vertically.
- Fast box-filter kernels handle common 2h1v and 2h2v cases.
- Fancy 2h1v and 2h2v kernels use triangle-filter interpolation; 2h2v requests context rows from `jdmainct.c`.
- `jinit_upsampler` validates sample ratios, rejects CCIR601 sampling and fractional ratios, selects methods, saves expansion factors, and allocates per-component color buffers only when needed.

Dependencies and interactions:
- Called by `jdpostct.c` unless `jdmerge.c` is selected.
- Depends on `jdmainct.c` to provide context rows for fancy 2h2v upsampling.
- Uses `jdcolor.c` for final colorspace conversion.

Risk notes:
- Fractional sampling ratios and CCIR601 alignment are not implemented.
- Fancy upsampling is disabled when `min_DCT_scaled_size == 1` because the main controller cannot provide context rows then.
- Generic integer upsampling uses simple replication, which is fast but visually weaker for uncommon high ratios.
