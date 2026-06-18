# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_xattr.h

## Purpose

Declares XFS xattr change and handler interfaces.

## Main Responsibilities

- Forward-declares `enum xfs_attr_update`.
- Declares `xfs_attr_change`.
- Exposes `xfs_xattr_handlers`.

## Important Invariants

- Keeps VFS xattr registration separate from implementation details.

## Dependencies

Depends on XFS DA args and Linux xattr handler declarations.

## Research Notes

Small header used to connect XFS inode/VFS setup to the xattr implementation.
