# File Research: sources/virtualization/libguestfs/daemon/zero.c

## Role
Implements zeroing, wipefs, zero-detection, free-space zeroing, and pre-mkfs signature wiping.

## Main Operations
- `do_zero()` zeroes the first 32 blocks of a device, skipping writes for already-zero blocks.
- `do_wipefs()` runs `wipefs -a`, adding `--force` when supported.
- `do_zero_device()` writes zeroes across the entire block device, checking existing data first.
- `do_is_zero()` and `do_is_zero_device()` scan a file or device for nonzero bytes.
- `do_zero_free_space()` creates a randomly named file filled with zeroes until `ENOSPC`, syncs, reports progress from `statvfs`, and unlinks the file.
- `wipe_device_before_mkfs()` internally invokes `wipefs -a` before mkfs-style operations.

## Behavior Notes
`wipefs_has_force_option()` caches whether the installed `wipefs` supports `--force`. `do_zero_free_space()` is intentionally described as open to future sparse/discard implementations but currently fills free space with a temporary file.

## Filesystem/Storage Relevance
This file is used for disk signature removal, whole-device zeroing, sparse-image preparation, and free-space scrubbing before image conversion or compression.
