# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/fsck.h

This is the central internal header for `fsck_ffs`. It defines shared data structures, global checker state, repair state constants, buffer cache metadata, inode state tracking, and function prototypes.

Key definitions:
- `DIP()` and `DIP_SET()` abstract UFS1 vs UFS2 dinode fields.
- `struct inostat` records inode state, type, descriptor type, and remaining link count.
- Inode states include `USTATE`, `FSTATE`, `FZLINK`, `DSTATE`, `DZLINK`, `DFOUND`, `DCLEAR`, and `FCLEAR`.
- `struct bufarea` represents cached filesystem blocks, with block number, size, errors, dirty flag, type, refcount, index, and typed union accessors.
- Buffer types distinguish superblock, cylinder group, indirect levels, external attributes, inode blocks, directory data, and user data.
- `struct inodesc` is the generic traversal descriptor used by inode and directory scanners.
- `struct dups` stores duplicate block lists.
- `struct inoinfo` caches directory parentage, `..`, depth, flags, size, and direct/indirect block addresses.

Global state:
- Device and mode flags: `cdevname`, `preen`, `nflag`, `yflag`, `bkgrdflag`, `ckclean`, `skipclean`, `surrender`, `wantrestart`.
- Filesystem descriptors and metadata: `fsreadfd`, `fswritefd`, `sblk`, `sblock`, `blockmap`, `maxino`, `maxfsblock`.
- Repair accounting: `n_blks`, `n_files`, `duplist`, `muldup`, `inostathead`, `inphash`, `inpsort`.
- Background fsck sysctl MIBs for link counts, block counts, sizes, maps, and summaries.
- Snapshot state: `snapcnt`, `snaplist`, `cursnapshot`, `copybuf`.

Important interactions:
- Provides prototypes for all phase functions, setup, inode traversal, directory repair, buffer I/O, snapshot COW, gjournal and SUJ entry points.
- Inline `Malloc`, `Balloc`, and `Calloc` retry after flushing cylinder-group cache entries.
