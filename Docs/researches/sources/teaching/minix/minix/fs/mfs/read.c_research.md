# File Research: sources/teaching/minix/minix/fs/mfs/read.c

`read.c` implements file reads, writes, peeks, logical-to-physical block mapping, read-ahead, indirect block reading, block-map buffer lookup, and directory enumeration.

`fs_readwrite` finds the already-open inode, checks write permission against read-only superblocks, enforces maximum file size, clears the old EOF zone when a write creates a hole, splits I/O into block-bounded chunks, and calls `rw_chunk`. On successful writes it extends file size for regular files/directories and marks ctime/mtime; reads mark atime. Device-node I/O on read-only filesystems is allowed without updating inode timestamps.

`rw_chunk` maps the file position with `read_map`, returns zeroes for holes on reads, reports zero blocks to VM on peeks, allocates missing blocks on writes with `new_block`, uses read-ahead for reads, and uses `lmfs_get_block_ino` for VM-cache-aware buffer lookup. It copies data through `fsdriver_copyout`/`copyin` and dirties written buffers.

`read_map` resolves direct, single-indirect, and double-indirect zone pointers into physical block numbers, returning `NO_BLOCK` for holes or opportunistic metadata misses. `rd_indir` reads and validates indirect zone numbers. `get_block_map` maps a position and returns the corresponding cached block buffer.

`rahead` performs cache probing and prefetch queue construction, including nearby first-indirect-block prefetch and minimum read-ahead after sequential access. `fs_getdents` validates directory offsets, walks directory entries, computes name lengths, fetches target inode modes to provide directory-entry types, adds entries through `fsdriver_dentry_*`, updates the next position, and marks directory atime.
