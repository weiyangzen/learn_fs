# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lzo_wrapper.c

Implements LZO compressor support.

Supported options:
- `-Xalgorithm <algorithm>`
- `-Xcompression-level <1..9>` for `lzo1x_999`

Algorithms:
- `lzo1x_1`
- `lzo1x_1_11`
- `lzo1x_1_12`
- `lzo1x_1_15`
- `lzo1x_999`

Behavior:
- Default algorithm is `lzo1x_999`; default compression level is 8.
- Postprocessing ensures compression level is used only with `lzo1x_999`.
- Suppresses stored compressor options when defaults match legacy behavior.
- Serializes non-default algorithm/level into `struct lzo_comp_opts`.
- Extracts stored options for append mode and validates algorithm/level combinations.
- Allocates LZO workspace and an expansion-sized temporary buffer in `squashfs_lzo_init()`.
- Compresses into the temporary buffer because LZO’s API does not take an output-size limit, checks against block size, optimizes, then copies to destination.
- Decompresses with `lzo1x_decompress_safe()`.

Key compressor vtable:
- `lzo_comp_ops` supports init, compress, uncompress, options, post-options, dump/extract/display options, usage, and option-arity detection.
