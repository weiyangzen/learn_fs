# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/sub.c

This file contains central KFS support logic for fid allocation, path references, permissions, locks, block allocation, formatting, and filesystem initialization helpers.

Key behavior:
- `fsstr` resolves filesystem names.
- `fileinit` clears all fids on a channel, handles remove-on-close, and releases locks/paths.
- `filep`, `newfp`, and `freefp` manage locked fid structures from a global free list.
- `newwp`, `getwp`, `freewp`, and `putwp` manage shared parent walk paths with reference counts.
- `iaccess` implements owner/group/other permission checks plus special handling for group 9999 and directory execute.
- `tlocked` implements `DLOCK` exclusive lock allocation/renewal over `Tlock`.
- `newqid` and `qidpathgen` increment the superblock qid generator.
- `checkname` validates fixed-length names.
- `bfree`, `balloc`, and `addfree` manage block free lists and tag initialization.
- Formatting helpers register `%C`, `%D`, `%A`, `%G`, `%T`, and `%O`.
- `rootream`, `superream`, and `superok` initialize and mark filesystem metadata.
- `prime` and `hexdump` are utility helpers.

Dependencies:
- Core partner files are `iobuf.c`, `dentry.c`, `uid.c`, `dat.c`, and `portdat.h`.

Notable details:
- File and path structures are allocated in chunks with hard caps (`Fmax`, `Wmax`).
- `bfree` recursively frees indirect blocks, cancels dirty cached copies, and returns blocks to the superblock freelist.
- `balloc` pulls blocks from the superblock freelist and tags newly allocated blocks immediately.
