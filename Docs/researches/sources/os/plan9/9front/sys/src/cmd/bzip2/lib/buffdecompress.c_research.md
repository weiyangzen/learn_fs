# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/buffdecompress.c

This implements `BZ2_bzBuffToBuffDecompress`, a convenience API for decompressing one memory buffer into another.

Behavior:
- Validates destination/source pointers, `small` flag, and verbosity.
- Initializes a decompression `bz_stream`.
- Runs `BZ2_bzDecompress` once against the supplied buffers.
- On `BZ_STREAM_END`, updates `*destLen` to bytes written and returns `BZ_OK`.
- If decompression returns `BZ_OK`, distinguishes unexpected EOF from output-buffer exhaustion based on remaining output space.

Notable implementation details:
- Always finalizes decompression state after successful initialization.
- Uses caller-provided output buffer; no resizing is attempted.
