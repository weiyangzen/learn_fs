# File Research: sources/local-fs/btrfs-linux/fs/btrfs/fiemap.h

## Scope

This small header declares the Btrfs FIEMAP entry point implemented in `fiemap.c`.

## Public API Surface

- `btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo, u64 start, u64 len)` reports file extent layout to the generic FIEMAP infrastructure.

## Dependencies And Consumers

The header includes `<linux/fiemap.h>` and is consumed by Btrfs inode/file operation code that wires FIEMAP into VFS ioctls.

## Risks And Invariants

- Callers rely on `btrfs_fiemap()` to perform FIEMAP preparation, optional sync handling, inode locking, and Btrfs-specific extent reporting. The header intentionally exposes no internal cache or scan helpers.
