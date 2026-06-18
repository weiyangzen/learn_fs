# File Research: sources/virtualization/qemu/block/filter-compress.c

## Purpose
Implements the `compress` block filter driver. It forces writes through the child with `BDRV_REQ_WRITE_COMPRESSED`, allowing compression-capable underlying formats to receive compressed-write requests.

## Open Behavior
- Opens a single `file` child with `bdrv_open_file_child()`.
- Under graph read lock, checks that the child has a driver and that `block_driver_can_compress()` is true.
- Fails with `-ENOTSUP` if the underlying format does not support compression.
- Exposes supported write flags as `BDRV_REQ_WRITE_UNCHANGED` plus child FUA if available.
- Exposes supported zero flags as `BDRV_REQ_WRITE_UNCHANGED` plus child FUA, may-unmap, and no-fallback flags if available.

## I/O Behavior
- `compress_co_getlength()` forwards to child length.
- `compress_co_preadv_part()` forwards reads unchanged.
- `compress_co_pwritev_part()` forwards writes with `BDRV_REQ_WRITE_COMPRESSED` added.
- Zero writes and discards are forwarded unchanged.
- Eject and lock-medium operations are forwarded to the child.

## Limits
- `compress_refresh_limits()` asks the child for `BlockDriverInfo`; if it has a nonzero cluster size, it sets request alignment to that cluster size.

## Driver Registration
- Registers `bdrv_compress` with format name `compress`.
- Marks `.is_filter = true`.
