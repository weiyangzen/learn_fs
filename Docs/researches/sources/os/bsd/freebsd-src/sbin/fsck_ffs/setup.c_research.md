# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/setup.c

This file opens the target filesystem, reads/validates the superblock, allocates core maps, loads snapshot metadata, and handles UFS2 recovery information.

Key behavior:
- `setup()` verifies an already-open read fd and loaded superblock, opens write fd when allowed, handles superblock check-hash correction, skips clean filesystems, validates basic superblock fields, and allocates block/inode/directory caches.
- Rejects very old UFS1 inode formats requiring pre-2002 conversion tooling.
- Offers to save UFS2 recovery data when no recovery information exists.
- Sets `usedsoftdep` from superblock flags.
- Loads valid active snapshot inodes from `fs_snapinum[]`, removing invalid entries from the snapshot list.
- Allocates `copybuf` when snapshots are active.

Snapshot validation:
- `checksnapinfo()` verifies that a snapshot block list contains required copied metadata blocks: superblock, cylinder groups, and summary blocks.
- `getlbnblkno()` finds the data block containing the snapshot block list.

Device/superblock handling:
- `openfilesys()` accepts character/block devices; in background mode also accepts snapshot files and records `cursnapshot`.
- `readsb()` reads an explicit alternate superblock when `-b` is used, otherwise tries standard superblock, then standard with hash failure ignored, then exhaustive alternate search.
- On successful superblock read, copies it into `sblock`, computes `dev_bsize`, records actual superblock location, and updates legacy UFS1 widened fields when needed.
- `sblock_init()` initializes descriptor state and allocates the superblock buffer.

Recovery handling:
- `chkrecovery()` checks whether UFS2 recovery material already exists before the UFS2 superblock area.
- `saverecovery()` writes `struct fsrecovery` data into the last bytes of the boot block region.

Important interactions:
- Provides the initialized `blockmap`, `inostathead`, `inphash`, and `inpsort` required by all passes.
- Snapshot loading is required by `inode.c` copy-on-write code.
- Calls `ckfini(0)` on allocation/setup failure after partial initialization.
