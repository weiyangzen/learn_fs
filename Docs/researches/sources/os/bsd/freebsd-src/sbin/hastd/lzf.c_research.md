# File Research: sources/os/bsd/freebsd-src/sbin/hastd/lzf.c

Read completely: 408 lines.

This is the bundled liblzf compression/decompression implementation used by HAST when LZF compression is configured.

Key responsibilities:
- Implements `lzf_compress()` using a hash table of recent byte sequences and LZ-style literal/back-reference encoding.
- Implements `lzf_decompress()` for the compressed format documented in the source comments.
- Supports compile-time tuning through macros from `lzf.h`: hash size, fast modes, strict alignment, state passing, errno behavior, and input checking.
- Uses little fixed-format control bytes for literal runs, short backrefs, and long backrefs.
- Returns `0` on compression failure or decompression error, with decompression setting `errno` unless `AVOID_ERRNO` is enabled.

Important interactions:
- Included as a local compression primitive for HAST protocol data paths outside this file.
- The public ABI is declared in `lzf.h`.

Reliability and security notes:
- Decompression checks output bounds and, with `CHECK_INPUT`, input buffer bounds; it also rejects backrefs before the output base.
- Compression requires non-overlapping input/output buffers and returns failure when output would not fit.
- Some fast paths use unaligned 16-bit loads when permitted by platform macros.
