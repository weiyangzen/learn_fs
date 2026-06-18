# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag.h

Declares XFS per-allocation-group structures, state flags, reference helpers, geometry helpers, and grow/shrink interfaces.

Key behavior:
- Defines `struct xfs_ag_resv` for per-AG metadata block reservations:
  - originally reserved.
  - currently reserved.
  - originally requested.
- Defines `struct xfs_perag`, the incore AG cache:
  - embedded `struct xfs_group`.
  - AGF-derived free-space btree levels, freelist count, free blocks, longest extent, btree blocks.
  - AGI-derived allocated/free inode counters.
  - inode allocation search hints.
  - refcount btree level.
  - metadata and rmapbt reservations.
  - precalculated min/max valid AG inode numbers.
  - kernel-only inode cache, reclaim, filestream, repair-height, and blockgc state.
- Provides `to_perag`, `pag_group`, `pag_mount`, and `pag_agno` conversion helpers.
- Defines atomic per-AG state bits:
  - AGF initialized.
  - AGI initialized.
  - prefers metadata.
  - allows inodes.
  - AGFL needs reset.
- Declares perag initialization, freeing, counter reconstruction, and last-AG-size update functions.
- Provides passive and active perag reference wrappers around `xfs_group`.
- Provides perag iteration helpers, including wrap-around iteration with explicit restart and stop bounds.
- Declares AG geometry verification:
  - AG block number/range checks.
  - AG inode number checks.
  - internal-log containment check.
- Defines `struct aghdr_init_data` used by growfs AG-header initialization.
- Declares AG header init, shrink, grow delta computation, extend, and geometry-reporting functions.
- Provides AG-relative conversion helpers to filesystem block, disk address, and inode number.

Important interactions:
- `xfs_alloc.c`, `xfs_ag.c`, inode allocation, scrub, repair, and growfs code rely on the cached perag counters and state bits.
- Perag reference helpers enforce lifecycle semantics for allocation scans and AG mutation paths.
