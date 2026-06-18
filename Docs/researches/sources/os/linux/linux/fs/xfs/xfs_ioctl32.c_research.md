# File Research: sources/os/linux/linux/fs/xfs/xfs_ioctl32.c

## Role
Implements 32-bit compat handling for XFS ioctls whose argument layouts, pointer sizes, time fields, or x86 alignment differ from native 64-bit layout.

## Main Structures and Entry Points
- `xfs_file_compat_ioctl` dispatches compat commands and falls back to native dispatch when safe.
- `xfs_compat_ioc_fsbulkstat` handles compat legacy bulkstat and inumbers requests.
- `xfs_fsbulkstat_one_fmt_compat` and `xfs_fsinumbers_fmt_compat` serialize native internal results into compat output structures.
- `xfs_ioctl32_bstat_copyin` and timestamp helpers translate compat `xfs_bstat` input for swapext.
- `xfs_compat_handlereq_copyin` translates handle request structures.
- `xfs_compat_attrlist_by_handle` and `xfs_compat_attrmulti_by_handle` implement handle-based xattr compat ioctls.
- x86 alignment-only helpers handle geometry v1 and growfs structures under `BROKEN_X86_ALIGNMENT`.

## Behavior
Compat bulkstat follows the native legacy cursor semantics, but translates 32-bit user pointers through `compat_ptr`, enforces `CAP_SYS_ADMIN`, validates counts and buffers, and selects native output formatters for x32 syscalls where pointer arguments are compat but data structures use native 64-bit layout.

Compat handle operations copy in 32-bit pointer fields and call the shared handle helpers. Attribute list and multi operations resolve handles to dentries and call native xattr helpers, copying compat operation arrays back to userspace with per-operation error fields.

The compat dispatcher maps 32-bit ioctl numbers to native behavior where possible, wraps mutating operations with `mnt_want_write_file`, and delegates unsupported or native-layout-compatible requests to `xfs_file_ioctl`.

## Interactions
Depends on `xfs_ioctl32.h` for compat structs/ioctl numbers, `xfs_ioctl.h` for native helpers, `xfs_itable` for bulk walking, and `xfs_handle`/`xfs_attr` for handle-based attribute operations.

## Invariants and Error Handling
- Compat pointer values are never used directly; they are converted with `compat_ptr`.
- Administrative bulk and handle-attribute operations require `CAP_SYS_ADMIN`.
- Attribute multi operation arrays are bounded against integer overflow and capped at `16 * PAGE_SIZE`.
- `XFS_IOC_GETVERSION_32` is remapped to native ioctl encoding with `long` size.
- Swapext compat copies the fixed prefix and translates the embedded bstat field separately.
