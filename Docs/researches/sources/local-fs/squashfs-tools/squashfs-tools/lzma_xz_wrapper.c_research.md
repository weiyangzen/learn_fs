# File Research: sources/local-fs/squashfs-tools/squashfs-tools/lzma_xz_wrapper.c

Alternative obsolete LZMA1 wrapper implemented with XZ Utils liblzma.

Behavior:
- Uses `lzma_alone_encoder()` with preset 5 and dictionary size equal to SquashFS block size.
- Rewrites the 8-byte uncompressed-size field in the LZMA-alone header.
- Uses `lzma_alone_decoder()` with a 32 MiB memory limit.
- During decompression, copies the input header, reads the expected uncompressed size, replaces the size field with unknown-size bytes, then decodes.
- Accepts stream-end success, and also accepts a case where `LZMA_OK` produced enough output and consumed input.
- Exposes no compressor options.
- Usage text marks it deprecated and notes no kernel support.

Key role: optional legacy LZMA1 support without requiring the standalone LZMA SDK.
