# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_extfree_item.h

## Purpose

Defines kernel-only structures and declarations for EFI/EFD extent-free log items.

## Main Contents

- `XFS_EFI_MAX_FAST_EXTENTS`
- `struct xfs_efi_log_item`
  - embedded log item
  - reference count
  - next extent index
  - logged EFI format
- `xfs_efi_log_item_sizeof`
- `struct xfs_efd_log_item`
  - embedded log item
  - pointer to EFI
  - next extent index
  - logged EFD format
- `xfs_efd_log_item_sizeof`
- `XFS_EFD_MAX_FAST_EXTENTS`
- EFI/EFD cache declarations.
- `xfs_extent_free_defer_add`
- `xfs_efi_log_space`
- `xfs_efd_log_space`

## Research Notes

The header documents the EFI/EFD two-reference lifetime model. That model is central because EFI and EFD log items can be committed, unpinned, inserted into the AIL, or aborted in different orders.
