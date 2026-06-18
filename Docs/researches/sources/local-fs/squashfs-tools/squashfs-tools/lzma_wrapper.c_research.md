# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lzma_wrapper.c

Implements obsolete LZMA1 compressor support using the LZMA SDK.

Behavior:
- Compresses with `LzmaCompress()` into an LZMA-alone style header plus payload.
- Writes an 8-byte little-endian uncompressed-size field after the LZMA properties.
- Treats `SZ_ERROR_OUTPUT_EOF` as output-buffer overflow and returns 0.
- Decompresses by reading the size from the LZMA header, validating it fits the requested output size, then calling `LzmaUncompress()`.
- Exposes no compressor options.
- Usage text marks it deprecated and notes no kernel support.

Key role: optional legacy compressor wrapper retained for compatibility.
