# File Research: sources/os/linux/linux/fs/xfs/xfs_pnfs.h

## Purpose

`xfs_pnfs.h` declares XFS pNFS block-layout interfaces and provides a stub for builds without block export operations.

## Public Interface

- `xfs_break_leased_layouts`: declared when `CONFIG_EXPORTFS_BLOCK_OPS` is enabled; otherwise an inline stub returns 0.
- `xfs_export_block_ops`: external exportfs block operations table.

## Dependencies

Includes `linux/exportfs_block.h`.
