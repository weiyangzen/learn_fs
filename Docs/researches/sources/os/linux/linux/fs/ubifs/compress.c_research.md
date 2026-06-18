# File Research: sources/os/linux/linux/fs/ubifs/compress.c

Read completely: 369 lines.

This file centralizes UBIFS compression and decompression. It defines the UBIFS compressor registry for `none`, LZO, zlib/deflate, and zstd, backed by the kernel async compression API when the corresponding `CONFIG_UBIFS_FS_*` option is enabled.

Main entry points: `ubifs_compress`, `ubifs_compress_folio`, `ubifs_decompress`, `ubifs_decompress_folio`, `ubifs_compressors_init`, and `ubifs_compressors_exit`.

Key behavior: compression is skipped for `UBIFS_COMPR_NONE`, too-small inputs, compressor errors, or outputs that fail to save at least `UBIFS_MIN_COMPRESS_DIFF` bytes. In those cases the input is copied verbatim and the returned compression type is changed to `UBIFS_COMPR_NONE`. Folio and linear-buffer paths share common helpers, with folio-aware source/destination setup.

Decompression validates the compression type, rejects algorithms not compiled in, copies `none` data directly, and reports decompression failures through `ubifs_err`.

Important interactions: data write/read paths in `file.c` and journal data-node code rely on this file to preserve `compr_type` and output length semantics. `crypto.c` can further encrypt compressed data after compression and decrypt before decompression.

Reliability notes: the async compression path retries `-EAGAIN` with a cloned request and `crypto_wait_req`. Unsupported on-flash compression types or disabled compressors return `-EINVAL`, which turns read-side corruption or feature mismatch into an explicit failure.
