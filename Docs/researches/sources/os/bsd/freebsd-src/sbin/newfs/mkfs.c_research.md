# File Research: sources/os/bsd/freebsd-src/sbin/newfs/mkfs.c

Implements the low-level UFS/FFS filesystem builder used by `newfs.c`. `mkfs()` computes and validates superblock geometry, block/fragment sizes, cylinder-group layout, inode density, summary areas, feature flags, metadata check hashes, soft updates, gjournal, multilabel, TRIM, and volume label state before writing the initial filesystem image.

Key behaviors:
- Converts frontend globals from `newfs.h` into `struct fs` and `struct uufsd` disk state.
- Supports UFS1 and UFS2 paths, including UFS1 legacy fields and UFS2 recovery metadata.
- Writes backup superblocks, cylinder-group maps, initialized inode blocks, root directory, and optional `.snap` directory.
- Uses `Nflag` dry-run mode, `Rflag` deterministic timestamps/randoms for regression testing, and `Xflag` failure injection exits.
- Contains bitmap helpers for fragment availability (`isblock`, `setblock`, `clrblock`) and first-cylinder-group allocation helpers for root bootstrap objects.

Important dependencies:
- FreeBSD UFS/FFS headers: `ufs/ufs/dinode.h`, `ufs/ufs/dir.h`, `ufs/ffs/fs.h`.
- `libufs` disk operations exposed through `struct uufsd`, `bread`, `bwrite`, `sbwrite`, `cgwrite`, `getinode`, and `putinode`.
- Frontend global options declared in `newfs.h`.

Research notes:
- This is the core on-disk UFS layout constructor; bugs here affect superblock validity, fsck recovery, snapshot support, and first mount behavior.
- The `part_ofs` offset workaround means direct `bread()`/`bwrite()` calls must consistently account for file-backed partition offsets.
- The cylinder-group sizing logic is intentionally conservative because `CGSIZEFUDGE` preserves compatibility with older validators.
