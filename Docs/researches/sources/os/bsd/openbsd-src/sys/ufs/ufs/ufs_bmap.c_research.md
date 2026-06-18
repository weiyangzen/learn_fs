# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_bmap.c

Read completely: 308 lines.

Implements logical-to-physical block mapping and indirect-block path generation for UFS/FFS files.

Core behavior:
- `ufs_bmap()` returns the underlying device vnode when requested and maps a logical block through `ufs_bmaparray()`.
- `ufs_bmaparray()` handles direct blocks from dinode direct pointers, indirect blocks through negative logical block numbers, cached or on-disk indirect block reads, UFS1/UFS2 pointer width selection, and optional sequential run-length detection for clustered I/O.
- Missing data or indirect mappings are reported as `-1`.
- `ufs_getlbns()` computes the chain of indirect blocks and offsets needed for a data block or metadata block, supporting single, double, and triple indirection, and rejects too-large logical blocks with `EFBIG`.

Integration and risks:
- Indirect metadata logical block numbering is negative and must match truncate/allocation code.
- Cached dirty indirect blocks can satisfy mapping before disk writeback.
- UFS1 and UFS2 pointer sizes are selected at runtime through mount type.
