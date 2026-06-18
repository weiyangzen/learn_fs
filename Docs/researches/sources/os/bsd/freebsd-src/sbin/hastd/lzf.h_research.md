# File Research: sources/os/bsd/freebsd-src/sbin/hastd/lzf.h

Read completely: 217 lines.

This is the public and configuration header for the bundled liblzf implementation.

Key responsibilities:
- Declares `lzf_compress()` and `lzf_decompress()`.
- Documents compression/decompression contracts, buffer requirements, and errno behavior.
- Defines `LZF_VERSION`.
- Provides compile-time tuning defaults for `HLOG`, `VERY_FAST`, `ULTRA_FAST`, `STRICT_ALIGN`, `INIT_HTAB`, `AVOID_ERRNO`, `LZF_STATE_ARG`, and `CHECK_INPUT`.
- Defines internal byte/hash-table types used by `lzf.c`.

Important interactions:
- `LZF_STATE_ARG` can intentionally change the effective function prototype, so users must compile consistently.
- `STRICT_ALIGN` defaults differ by architecture and affect generated compression code.

Reliability notes:
- Header comments explicitly state compressed output can be larger than input and callers should keep uncompressed fallback logic.
- `CHECK_INPUT` is enabled by default, improving decompressor robustness against truncated or malformed streams.
