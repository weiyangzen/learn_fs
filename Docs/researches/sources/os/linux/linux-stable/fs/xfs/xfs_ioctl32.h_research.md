# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_ioctl32.h

This header defines 32-bit compat XFS ioctl ABI structures and ioctl numbers.

Contents:
- Includes `<linux/compat.h>`.
- Defines `XFS_IOC_GETVERSION_32`.
- Defines `BROKEN_X86_ALIGNMENT` and `__compat_packed` for x86_64 alignment differences.
- Declares compat versions of:
  - `xfs_bstime`
  - `xfs_bstat`
  - `xfs_fsop_bulkreq`
  - handle request structures
  - `xfs_swapext`
  - attrlist-by-handle and attrmulti-by-handle request structures
  - attr multiop structures
  - x86 alignment-sensitive geometry, inogrp, growfs data, and growfs realtime structures.
- Defines compat ioctl numbers for bulkstat, inumbers, handle operations, swapext, attrlist, attrmulti, geometry v1, and growfs variants.

Role:
- Encodes the ABI contract needed by `xfs_ioctl32.c`.
- Isolates architecture layout differences so the compat dispatcher can translate to native internal structures.

Risk notes:
- These definitions are ABI-sensitive; field sizes, packing, and ioctl numbers must remain stable.
- Pointer fields use `compat_uptr_t` and must always be converted before use.
