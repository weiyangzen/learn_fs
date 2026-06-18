# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/zerotrunc.c

Filter that copies stdin to stdout until the first zero byte.

Key behavior:
- Reads up to 4096-byte chunks.
- Uses `memchr` to find NUL.
- Writes bytes before the first NUL, then stops.
- If no NUL appears, streams all input until EOF.

Use:
- Useful for truncating NUL-padded data or strings embedded in fixed-size binary fields.

Filesystem relevance:
- Indirect utility for stream/file content processing.
