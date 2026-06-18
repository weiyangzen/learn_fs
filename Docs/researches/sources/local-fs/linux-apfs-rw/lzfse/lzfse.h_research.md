# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse.h

## Purpose
Public BSD-licensed LZFSE decode API header bundled for APFS compressed-file support.

## API
- `lzfse_decode_scratch_size()`: returns required scratch size.
- `lzfse_decode_buffer()`: decompresses an LZFSE buffer into a caller-provided destination buffer with optional scratch storage.

## Dependencies
Uses Linux `stddef` and `types` headers instead of userspace libc headers.

## Notes
The comments retain upstream Apple wording about malloc/free behavior, while this kernel port’s implementation uses `kmalloc()`/`kfree()` when scratch space is not supplied.
