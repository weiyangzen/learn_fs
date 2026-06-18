# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_subr.c

This file contains shared FFS support routines used by kernel code and filesystem tools: inode loading, buffer acquisition with COW, fragment accounting, block bitmap operations, and cluster summary accounting.

Key responsibilities:
- Load on-disk UFS1/UFS2 dinodes into in-core inode fields.
- Acquire buffers for filesystem blocks while integrating with filesystem COW.
- Maintain fragment summary counts.
- Test, clear, and set full-block availability bits in cylinder group bitmaps.
- Maintain contiguous cluster summary state.

Important functions:
- `ffs_load_inode`: Reads the correct dinode from an inode block, byte-swaps if needed, copies into `ip->i_din`, and mirrors common fields into generic inode members.
- `ffs_getblk`: Wraps `getblk`, optionally sets physical block number, clears the buffer, and runs `fscow_run` for mapped buffers.
- `ffs_fragacct`: Updates fragment-size summary counters using `fragtbl`, `around`, and `inside` tables, with optional endian-aware counter updates.
- `ffs_isblock`: Tests whether all fragments in a full filesystem block are free for the configured `fs_fragshift`.
- `ffs_isfreeblock`: Tests whether all fragments in a full filesystem block are allocated.
- `ffs_clrblock`: Marks a full block allocated in a bitmap.
- `ffs_setblock`: Marks a full block free in a bitmap.
- `ffs_clusteracct`: Updates cluster free bitmap and cluster length summary counters when allocating or freeing a full block, then updates `fs_maxcluster`.

Important interactions:
- `ffs_load_inode` is used by mount reload and vnode initialization.
- `ffs_getblk` is used by truncation, summary updates, superblock writes, and indirect block handling.
- Fragment and block bitmap helpers are used by allocation, free, WAPBL log placement, and snapshot accounting.
- Depends on lookup tables defined in `ffs_tables.c`.

Notable behavior and risks:
- Bitmap operations panic on unknown `fs_fragshift`; callers rely on validated superblocks.
- `ffs_clusteracct` assumes caller serialization around filesystem/cylinder group state.
- Userland builds define `FFS_EI` to include byte-swapped filesystem support.
