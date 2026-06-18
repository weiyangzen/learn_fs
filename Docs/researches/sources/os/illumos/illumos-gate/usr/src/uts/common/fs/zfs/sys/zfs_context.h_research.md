# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_context.h

Provides the illumos kernel context umbrella for ZFS code. It centralizes common kernel headers, prediction macros, CPU sequence access, and AVL/tree comparison helpers.

Key elements:
- Includes kernel primitives for locks, atomics, memory allocation, taskqs, buffers, random data, byte order, lists, uio, zones, sysevents, FMA, DDI, cyclics, and callbacks.
- Defines `_zfs_expect`, `likely`, and `unlikely`.
- Defines `CPU_SEQID` as `CPU->cpu_seqid`.
- Defines `TREE_ISIGN`, `TREE_CMP`, and `TREE_PCMP`.

Main dependencies and interactions:
- Included by many ZFS headers and C files to normalize kernel API availability.
- `TREE_CMP` is used by local AVL comparators such as `unique_compare()`.

Implementation notes:
- The AVL comparison macros are intentionally scoped to ZFS rather than globally modifying illumos `sys/avl.h`.
