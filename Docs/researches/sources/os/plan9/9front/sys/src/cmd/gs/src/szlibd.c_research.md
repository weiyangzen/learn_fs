# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/szlibd.c

zlib decoding/decompression filter stream.

Key behavior:
- `s_zlibD_init` allocates dynamic state and calls `inflateInit2`, using negative `windowBits` when `no_wrapper` is set.
- Sets `st->min_left = 1` for decoding read-ahead.
- `s_zlibD_reset` calls `inflateReset`.
- `s_zlibD_process` maps stream cursors into `z_stream`, avoids `Z_BUF_ERROR` on empty input/full output, and calls `inflate(Z_PARTIAL_FLUSH)`.
- Special-cases a known JAWS PDF generator empty-stream byte sequence and returns `EOFC`.
- Returns stream statuses from zlib results: `Z_OK`, `Z_STREAM_END`, or error.
- `s_zlibD_release` calls `inflateEnd` and frees dynamic state.
- Exports `s_zlibD_template`.

Dependencies and interactions:
- Uses `szlibxx.h` and Ghostscript stream template conventions.
- Consumed as the Flate/zlib decode filter implementation.

Research relevance:
- Decompression filter with Ghostscript stream status mapping and PDF compatibility workaround.
