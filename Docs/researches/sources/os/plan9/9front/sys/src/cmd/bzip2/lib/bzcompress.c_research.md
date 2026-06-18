# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzcompress.c

This is the low-level streaming compression state machine for libbzip2.

Major responsibilities:
- `BZ2_bzCompressInit`: validates configuration, allocates `EState`, work arrays, and initializes run-length/block state.
- Input RLE: tracks repeated input bytes and writes bzip2 RLE representation into the current block.
- `BZ2_bzCompress`: handles `BZ_RUN`, `BZ_FLUSH`, and `BZ_FINISH` modes.
- `BZ2_bzCompressEnd`: frees compression state and work buffers.

State model:
- Modes: running, flushing, finishing, idle.
- States: input and output.
- `handle_compress` copies input into blocks, calls `BZ2_compressBlock`, and drains generated compressed bytes.

Notable implementation details:
- Block capacity is `100000 * blockSize100k - 19`.
- Work arrays are `arr1`, `arr2`, and `ftab`.
- RSC-added checks return `BZ_SEQUENCE_ERROR` if flush/finish makes no progress.

Risks and caveats:
- Correct usage requires stable `avail_in` during flush/finish; mismatches are sequence errors.
- The compressor is sensitive to caller-managed input/output buffer progress.
