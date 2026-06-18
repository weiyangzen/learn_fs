# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_aops.h

## Purpose

Declares the XFS address-space operations and key I/O completion helpers.

## Key Contents

- `xfs_address_space_operations`
- `xfs_dax_aops`
- `xfs_setfilesize`
- `xfs_end_bio`

## Research Notes

This header exposes the aops tables to inode setup code and the bio completion hook to iomap-backed I/O.
