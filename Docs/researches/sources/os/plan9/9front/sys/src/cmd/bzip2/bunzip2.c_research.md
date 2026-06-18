# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/bunzip2.c

This is the Plan 9 `bunzip2` command wrapper around libbzip2.

Behavior:
- Supports `-c`, `-v`, and `-D`.
- With no files, decompresses stdin to stdout.
- With files, verifies `BZh` magic, derives output names, and writes decompressed output.
- `.bz2` suffix is stripped; `.tbz`/`.tbz2` become `.tar`.
- Avoids overwriting if output name would equal input name.

Streaming model:
- Uses `Biobuf` input/output and `bz_stream`.
- Refills an `IOUNIT` input buffer, preserves unconsumed bytes, and flushes an `IOUNIT` output buffer.
- Calls `BZ2_bzDecompressEnd` after `BZ_STREAM_END`.

Risks and caveats:
- Output name buffer is only 64 bytes.
- Failure removes the partially created output file via `delfile`.
