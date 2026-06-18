# File Research: sources/local-fs/squashfs-tools/squashfs-tools/gzip_wrapper.c

Implements gzip/zlib compressor support for the SquashFS compressor interface.

Supported options:
- `-Xcompression-level <1..9>`
- `-Xwindow-size <8..15>`
- `-Xstrategy <comma-separated strategies>`

Strategies:
- default
- filtered
- huffman_only
- run_length_encoded
- fixed

Behavior:
- Maintains process-global compressor option state.
- Suppresses stored compressor options when all gzip defaults are used, preserving legacy compatibility.
- Serializes non-default options into `struct gzip_comp_opts`.
- Extracts stored options for append mode, resetting to defaults when option size is zero.
- Displays stored compressor options.
- Initializes a zlib stream and, for data blocks with multiple strategies, tries each selected strategy and keeps the smallest result.
- Uses zlib `uncompress()` for decompression.

Key compressor vtable:
- `gzip_comp_ops` supports init, compress, uncompress, options, post-options, dump/extract/display options, usage, and option-arity detection.

Notable quirks:
- Error messages say ranges such as `1 >= n <= 9`, which is mathematically reversed wording but intended as `1 <= n <= 9`.
- Multiple strategy mode allocates extra temporary buffers for all but the first strategy.
