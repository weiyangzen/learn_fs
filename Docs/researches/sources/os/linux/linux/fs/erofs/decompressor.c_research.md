# File Research: sources/os/linux/linux/fs/erofs/decompressor.c

Implements core EROFS decompression support, including LZ4, plain transforms, stream buffer management, algorithm config parsing, and decompressor lifecycle.

Key behavior:
- Loads LZ4 configuration from compression config records or legacy superblock fields.
- Tracks LZ4 pcluster and sliding-distance requirements and grows global buffers accordingly.
- Prepares sparse output page arrays by allocating short-lived bounce pages where needed.
- Handles LZ4 input/output overlap, including in-place decompression, vmapped input, and per-CPU bounce buffers.
- `z_erofs_fixup_insize()` skips zero padding to determine exact compressed payload start.
- Provides optimized single-page LZ4 and general multi-page LZ4 decode paths.
- Implements shifted/interlaced plain transforms for non-compressing encoded layouts.
- `z_erofs_stream_switch_bufs()` coordinates multi-call streaming decoders, maps new input/output pages, allocates gap pages, and avoids input/output overlap by bouncing.
- Defines the runtime decompressor table for shifted, interlaced, LZ4, and optional LZMA/DEFLATE/ZSTD.
- Parses compression config records from metadata and calls each algorithm’s config hook.
- Initializes/exits all enabled decompressor backends.

Important interactions:
- Used by compressed read paths outside this group.
- Algorithm availability is checked against on-disk `available_compr_algs`.
- Short-lived pages are returned through the EROFS pagepool.
