# File Research: sources/os/linux/linux/fs/xfs/xfs_itable.h

## Role
Defines the internal bulk inode query request structure, flags, formatter callback types, and exported bulkstat/inumbers APIs.

## Main Declarations
- `struct xfs_ibulk` carries mount/idmap, user output buffer, start cursor, input/output counts, request flags, and iwalk flags.
- Flags `XFS_IBULK_NREXT64` and `XFS_IBULK_METADIR` request 64-bit extent counts and metadata directory visibility.
- `xfs_ibulk_advance` moves the userspace output pointer, increments output count, and returns `-ECANCELED` when full.
- Formatter typedefs `bulkstat_one_fmt_pf` and `inumbers_fmt_pf`.
- Bulk APIs and conversion helpers for v5 and legacy structs.

## Interactions
Used by ioctl native/compat code and implemented by `xfs_itable.c`. Its callback design keeps inode walking independent from ABI-specific userspace copyout layouts.

## Invariants
`xfs_ibulk_advance` defines the shared buffer-full sentinel behavior: reaching `icount` returns `-ECANCELED`, which callers translate into successful partial completion as appropriate.
