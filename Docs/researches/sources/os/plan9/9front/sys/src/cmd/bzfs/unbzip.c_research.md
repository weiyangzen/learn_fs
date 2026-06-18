# File Research: sources/os/plan9/9front/sys/src/cmd/bzfs/unbzip.c

This is a bzfs-local, modified bzip2 decompressor. It embeds enough libbzip2 code to inflate a stream and expose it as a Plan 9 pipe.

Major responsibilities:
- `unbzip` forks a decompressor process and returns the read end of a pipe.
- `_unbzip` inflates fd input to fd output.
- Local `bunzip` streams data through `BZ2_bzDecompress`.
- Provides Plan 9 platform glue and allocation functions.
- Embeds bzip2 decompression machinery from `decompress.c`, including bit reading, Huffman table use, selector MTF decoding, block CRC handling, and BWT inverse setup.

Notable implementation details:
- Uses `sbrk` allocator with no-op free for decompression state.
- Small decompression path is disabled by `if (0 && s->smallDecompress)`, so fast `tt` table is always used.
- State machine saves local decode variables so decompression can resume when more input is needed.

Risks and caveats:
- This file is explicitly not identical to upstream bzip2.
- Error handling is minimal and often aborts/exits.
- Pipe child shares memory (`RFMEM`) and closes inherited descriptors to form a streaming stage.
