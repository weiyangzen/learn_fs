# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_pnfs.h

## Purpose
Declares XFS pNFS block-layout helper APIs.

## Main Contents
Under `CONFIG_EXPORTFS_BLOCK_OPS`, declares UUID export, map-blocks, commit-blocks, and layout-breaking functions. Without block export support, only `xfs_break_leased_layouts` remains as a no-op inline returning success.

## Dependencies
The header relies on VFS inode/superblock, iomap, and iattr types supplied by including kernel headers.
