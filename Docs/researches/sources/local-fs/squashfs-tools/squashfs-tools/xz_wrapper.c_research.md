# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xz_wrapper.c

Compressor plugin for Squashfs XZ/LZMA2 support using liblzma.

Key features:
- Supports optional BCJ filters: x86, PowerPC, IA64, ARM, ARM Thumb, SPARC, ARM64, and RISC-V.
- Provides fallback filter IDs for older liblzma headers missing ARM64 or RISC-V constants.
- Parses `-Xbcj` and `-Xdict-size` compressor options.
- Post-validates dictionary size after block size is known; it must be <= block size, >= 8192, and representable in XZ headers as `2^n` or `2^n + 2^(n+1)`.
- Dumps, extracts, and displays compressor options stored in the filesystem.
- Initializes one or more filter pipelines: plain LZMA2 and, for data blocks, one pipeline per selected BCJ filter.
- `xz_compress()` tries all configured pipelines and chooses the smallest successful compressed output.
- `xz_uncompress()` decodes with a fixed `MEMLIMIT` and verifies all input bytes were consumed.
- `xz_usage()` emits compressor-specific help.
- Exports `xz_comp_ops`, the `struct compressor` vtable used by the compressor registry.

Important liblzma usage:
- `lzma_lzma_preset()`
- `lzma_stream_buffer_encode()`
- `lzma_stream_buffer_decode()`
- `lzma_filter_encoder_is_supported()`
