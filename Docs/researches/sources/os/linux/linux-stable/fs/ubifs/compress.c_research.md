# File Research: sources/os/linux/linux-stable/fs/ubifs/compress.c

UBIFS compression gateway for buffers and folios. It centralizes compressor registration and wraps the kernel async compression API.

Key responsibilities:
- Defines compressor descriptors for `none`, `lzo`, `zlib`, and `zstd`, with `capi_name` present only when the matching Kconfig option is enabled.
- Exposes `ubifs_compress()` and `ubifs_compress_folio()` through a shared `ubifs_compress_common()`.
- Exposes `ubifs_decompress()` and `ubifs_decompress_folio()` through `ubifs_decompress_common()`.
- Initializes and tears down crypto API compressor handles via `ubifs_compressors_init()` / `ubifs_compressors_exit()`.

Important behavior:
- Compression is skipped for `UBIFS_COMPR_NONE`, small inputs under `UBIFS_MIN_COMPR_LEN`, failed compression, or insufficient savings. The original bytes are copied and the compression type is changed to `UBIFS_COMPR_NONE`.
- Output length is capped to `in_len - UBIFS_MIN_COMPRESS_DIFF` before compression, enforcing a minimum benefit threshold.
- The code uses `ACOMP_REQUEST_ON_STACK`; when `crypto_acomp_*()` returns `-EAGAIN`, it clones the request with `GFP_NOFS | __GFP_NOWARN` and waits through `crypto_wait_req()`.
- Decompression validates the compression type and compiled-in availability before dispatching. Unsupported on-flash compression types return `-EINVAL`.
- Folio paths use `memcpy_from_folio()`, `memcpy_to_folio()`, and `acomp_request_set_*_folio()` to avoid temporary mappings.

Cross-file links:
- `file.c` calls decompression while reading data nodes and calls compression indirectly through journal write paths.
- `crypto.c` can wrap compressed payloads with fscrypt, so decompression length and encrypted compressed-size fields must remain consistent.
- Compressor descriptors are declared against types and constants from `ubifs.h`.

Invariants and risks:
- The global `ubifs_compressors[]` must be initialized before any data-node compression/decompression.
- On-flash compressed nodes using a compressor not compiled into this kernel cannot be read.
- Error handling intentionally degrades compression to uncompressed writes, but decompression errors are fatal to the read path.
