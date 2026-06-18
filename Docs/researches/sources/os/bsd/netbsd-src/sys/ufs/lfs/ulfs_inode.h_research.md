# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_inode.h

Read completely: 232 lines.

Defines ULFS inode-facing macros, resource thresholds, file-handle structures, dinode accessors, indirect block addressing constants, and vnode/inode conversion helpers.

Directory-operation and LFS resource control:
- `MARK_VNODE()` and `UNMARK_VNODE()` map to LFS directory-operation vnode marking.
- Declares `lfs_set_dirop()` and `lfs_unset_dirop()`.
- Defines resource thresholds for buffers, bytes, pages, and directory operations: `LFS_MAX_*`, `LFS_WAIT_*`, `LFS_MAX_FSDIROP()`, and `LFS_STARVED_FOR_SEGS()`.
- Defines reserved-memory block types and counts for segment-writing paths: summaries, superblocks, inode blocks, clusters, clean blocks, and block I/O vectors.

Buffer and vnode helpers:
- `IS_IFILE()` identifies buffers belonging to the LFS ifile.
- `VPISEMPTY()` and `WRITEINPROG()` inspect vnode dirty/write state with LFS-specific fields.
- `VTOI()` and `ITOV()` convert between vnodes and inodes.

File handles:
- `struct ulfs_ufid` overlays NetBSD `fid` style data with inode and generation.
- `struct lfid` adds an LFS identifier for exported LFS file handles.

Dinode abstraction:
- `DIP()`, `DIP_ASSIGN()`, and `DIP_ADD()` read/update fields from either ULFS1 32-bit dinodes or ULFS2 64-bit dinodes.
- `SHORTLINK()` chooses the inline symlink storage area for the active dinode format.

Block addressing:
- `S_INDIR()`, `D_INDIR()`, and `T_INDIR()` define logical block positions for single, double, and triple indirect metadata.
- `struct indir` describes logical block paths used by `ulfs_getlbns()` and bmap/truncate code.

Risks and notes:
- Several macros depend on `ip->i_ump->um_fstype` matching the dinode union layout.
- Resource thresholds are heuristic and tied to global buffer/page/vnode pressure.
- `ufid_ino` is explicitly noted as 32-bit despite inode numbers logically being wider.
