# File Research: sources/os/linux/linux/fs/jfs/resize.c

JFS online filesystem extension implementation.

Key responsibilities:
- Implements `jfs_extendfs()` to grow a mounted JFS volume without shrinking existing filesystem space.
- Validates the requested logical-volume size against the block device or by probing the last block.
- Computes new inline-log, fsck workspace, and filesystem data-region sizes.
- Quiesces transactions before changing log and allocation-map state.
- Moves/reformats the inline log when needed and records `FM_EXTENDFS` transition state in the superblock.
- Extends the block allocation map with `dbExtendFS()`, grows the bmap file with append-mode xtree allocation, and finalizes the bmap.
- Extends inode allocation metadata with `diExtendFS()` when allocation-group sizing changes.
- Synchronizes the primary and secondary bmap inodes and updates primary/secondary superblocks.
- Resumes transactions after either success or error.

Important interactions:
- Uses `txQuiesce()` and `txResume()` to block live filesystem transactions.
- Uses log manager operations `lmLogShutdown()`, `lmLogFormat()`, and `lmLogInit()`.
- Uses superblock helpers `readSuper()`, direct buffer writes, and `updateSuper()`-compatible state flags.
- Uses bmap helpers `dbMapFileSizeToMapSize()`, `dbExtendFS()`, `dbFinalizeBmap()`, and `dbSync()`.
- Uses `xtAppend()` to grow the special block-map file in a sequential, replay-safe manner.
- Uses inode-map helpers `diExtendFS()`, `diSync()`, `diReadSpecial()`, `diWriteSpecial()`, and `diFreeSpecial()`.

Invariants and risks:
- Extension refuses read-only filesystems and refuses sizes smaller than the current map size.
- Crash recovery relies on the superblock transition flag and descriptors being written in the expected order.
- Inline-log movement is especially sensitive: the old log is shut down, the new one formatted, and the log serial recorded.
- The bmap file may need iterative growth when a huge extension consumes part of the newly mapped region for map pages.
- Errors after quiesce call `jfs_error()` and still resume transactions.
