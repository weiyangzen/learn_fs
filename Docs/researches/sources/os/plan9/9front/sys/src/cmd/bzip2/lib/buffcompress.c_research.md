# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/buffcompress.c

This implements `BZ2_bzBuffToBuffCompress`, a convenience API for compressing one memory buffer into another.

Behavior:
- Validates parameters: destination pointers, source pointer, block size 1-9, verbosity 0-4, work factor 0-250.
- Defaults work factor 0 to 30.
- Initializes a `bz_stream`, points it at the input/output buffers, and runs one `BZ_FINISH` compression.
- On success, updates `*destLen` to bytes written.
- Returns `BZ_OUTBUFF_FULL` if the destination buffer is insufficient.

Notable implementation details:
- Uses default allocators by leaving `bzalloc`/`bzfree` NULL.
- Always calls `BZ2_bzCompressEnd` before returning after initialization succeeds.

Relationship:
- This file is functionally identical to `bzbuffcompress.c` in this group.
