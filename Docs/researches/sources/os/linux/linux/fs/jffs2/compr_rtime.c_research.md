# File Research: sources/os/linux/linux/fs/jffs2/compr_rtime.c

This file implements the simple RTIME byte-oriented compressor. The algorithm keeps a 256-entry table of last positions for each byte value. Compression writes each literal byte followed by a run length indicating how many subsequent bytes matched the previous occurrence stream.

`jffs2_rtime_compress()` refuses tiny destination buffers, initializes the positions table, emits byte/run pairs while source and output space remain, and fails if the encoded output is not smaller than consumed input. On success it updates `*sourcelen` to bytes consumed and `*dstlen` to encoded bytes.

`jffs2_rtime_decompress()` mirrors the table process, copying the literal byte, reading the repeat count, then copying repeated bytes either with an overlap-safe loop or `memcpy()` when ranges do not overlap. It detects output overflow and returns nonzero failure.

The compressor descriptor registers as `JFFS2_COMPR_RTIME`, priority `JFFS2_RTIME_PRIORITY`, with optional disabled state if `JFFS2_RTIME_DISABLED` is defined. Init and exit only register/unregister.

Key dependencies: `compr.h`, JFFS2 compression IDs, and the generic registry.
