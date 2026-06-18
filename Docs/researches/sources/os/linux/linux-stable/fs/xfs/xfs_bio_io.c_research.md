# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bio_io.c

## Purpose

Provides a small helper for synchronous block-device reads and writes from virtually addressed memory.

## Main API

- `xfs_rw_bdev`

## Behavior

- Adds `REQ_META | REQ_SYNC` to the operation.
- Uses `bdev_rw_virt` for non-vmalloc memory.
- For vmalloc memory, builds one or more bios with `bio_add_vmalloc_chunk`.
- Chains bios when the current bio cannot accept more vmalloc-backed data.
- Submits the final bio synchronously with `submit_bio_wait`.
- Invalidates the vmalloc range after reads.

## Research Notes

This helper exists for metadata-like synchronous block I/O where the source/destination buffer may be vmalloc-backed.
