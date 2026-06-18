# File Research: sources/os/linux/linux/fs/xfs/xfs_ioctl32.h

## Role
Defines compat XFS ioctl structures and ioctl command numbers for 32-bit userspace on 64-bit kernels, including x86-specific packed layouts for historical alignment differences.

## Main Declarations
- `XFS_IOC_GETVERSION_32` and compat bulkstat/inumbers ioctl numbers.
- `compat_xfs_bstime`, `compat_xfs_bstat`, and `compat_xfs_fsop_bulkreq`.
- Compat handle request, swapext, attrlist-by-handle, and attrmulti-by-handle structures.
- Under `BROKEN_X86_ALIGNMENT`, packed compat geometry v1, inogrp, and growfs data/realtime structures plus associated ioctl numbers.

## Behavior Encoded by Types
The definitions preserve 32-bit pointer fields as `compat_uptr_t`, old 32-bit timestamps as `old_time32_t`, and packed layouts when x86_64 native alignment would otherwise mismatch historical userspace ABI.

## Interactions
Consumed by `xfs_ioctl32.c` to copy fields to/from userspace and to dispatch compat command numbers. The header also documents which native APIs require translation rather than direct fallback.

## Invariants
The ABI structures intentionally mirror 32-bit userspace layout; fields and packing are compatibility contracts and must not be casually rearranged.
