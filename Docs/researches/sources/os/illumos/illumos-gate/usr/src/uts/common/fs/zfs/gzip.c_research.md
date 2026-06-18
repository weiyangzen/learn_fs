# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/gzip.c

## Role

Small wrapper around ZFS zmod compression APIs for gzip compression and decompression.

## Compression

`gzip_compress()` calls `z_compress_level()` with the requested compression level. It asserts destination length is no larger than source length, matching ZFS’s “compression must save space” calling convention.

If compression fails:

- When destination is smaller than source, it returns `s_len` to signal no useful compression.
- When destination equals source, it copies input to output and returns `s_len`.

On success it returns compressed byte count.

## Decompression

`gzip_decompress()` calls `z_uncompress()` and returns `0` on success or `-1` on failure. It asserts the destination length can hold at least the source length.

## Dependencies

Uses `sys/zmod.h`; includes kernel or userland string/system headers depending on `_KERNEL`.
