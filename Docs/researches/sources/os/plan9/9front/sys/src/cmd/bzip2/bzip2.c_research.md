# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/bzip2.c

This is the Plan 9 `bzip2` command wrapper around libbzip2 compression.

Behavior:
- Supports `-v`, `-c`, `-n`, `-D`, and compression levels `-1` through `-9`.
- With no files, compresses stdin to stdout.
- With files, rejects directories and writes `.bz2` output; `.tar` inputs become `.tbz`.
- `-n` suppresses use of input mtime, though the current compressed stream wrapper does not actually store file metadata.

Streaming model:
- Uses `Biobuf` and `bz_stream`.
- Calls `BZ2_bzCompress` with `BZ_RUN` until input EOF, then `BZ_FINISH`.
- Writes output in `IOUNIT` chunks and finalizes with `BZ2_bzCompressEnd`.

Risks and caveats:
- Mutates the input path string when replacing `.tar` with NUL before building `.tbz`.
- Output file is removed on write/compress failure.
