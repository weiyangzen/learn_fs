# File Research: sources/local-fs/xfsprogs/db/info.c

## Purpose
Provides xfs_db informational commands for filesystem geometry and metadata reservation sizing.

## Main Interfaces
- `info_init()` registers `info`, `agresv`, and `rgresv`.
- `info` prints geometry in the same style as `mkfs.xfs` / `xfs_info`.
- `agresv` prints per-AG free space and reservation demand.
- `rgresv` prints realtime-group reservation demand.

## Control Flow
`info_f()` derives geometry with `libxfs_fs_geometry` and reports it with `xfs_report_geom`. `agresv_f()` either iterates requested AG numbers or all perags, and `print_agresv_info()` combines refcount, finobt, and rmap reserve calculations with AGF free-space counts. `rgresv_f()` similarly iterates rtgroups; `print_rgresv_info()` loads rtgroup rmap/refcount inodes in an empty transaction and compares requested reserves to free data blocks.

## Dependencies
Uses libfrog geometry/logging helpers, libxfs perag/rtgroup iteration, reservation calculators, AGF reads, realtime metadata inode loading, and global device names from `struct libxfs_init x`.

## Risks And Invariants
- Error paths print diagnostics and generally continue to the next AG/rtgroup.
- `rgresv` depends on realtime metadata directory and rtgroup inode availability.
- The AG reserve warning compares unfilled reserve demand (`ask - used`) to currently free blocks.
