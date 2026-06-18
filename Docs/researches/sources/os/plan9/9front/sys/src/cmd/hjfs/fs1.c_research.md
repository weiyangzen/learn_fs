# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/fs1.c

Implements core `hjfs` filesystem storage operations: reference counts, free block allocation, root creation, filesystem reaming, location tracking, copy-on-write block lookup, truncation, directory entry search, deletion, and directory-entry allocation.

Key points:
- `chref`, `getfree`, and `putfree` manage block reference counts in reference blocks and maintain a small free-block channel cache.
- `ream` initializes a fresh filesystem: writes the superblock, initializes reference blocks, reserves metadata blocks, creates root/dump-root dentries, syncs, and later writes the default user database.
- `initfs` loads the superblock, initializes root `Loc` objects for normal and dump views, creates the free-list channel, and loads `/adm/users`.
- `getloc`, `cloneloc`, `putloc`, and `haveloc` maintain an in-memory location tree with references, child links, global links, and delayed deletion for `LGONE` entries.
- `dumpblk` copies shared blocks for snapshots/copy-on-write and increments child block references for indirect and directory-entry blocks.
- `getblk` resolves direct and multi-level indirect file blocks, optionally allocating or copy-on-writing blocks for write/create/overwrite modes.
- `trunc`, `delindir`, and `delindirpart` release file block trees while respecting shared reference counts.
- `findentry`, `newentry`, `delete`, and `deltraverse` implement directory scans, free-slot allocation, duplicate-name detection, recursive directory deletion, and qid/location validation.
- `modified` updates timestamps, mutating user id, and qid version.

Dependencies and interactions:
- Uses `dat.h`/`fns.h` types such as `Fs`, `Dev`, `Buf`, `Dentry`, `FLoc`, `Loc`, and block constants.
- Calls buffer-cache functions (`getbuf`, `putbuf`), channel/file operations (`chanattach`, `chanwalk`, `chancreat`, `chanopen`), user database functions (`userssave`, `usersload`), and permission-sensitive mutation hooks (`willmodify`, `sync`).
- Provides lower-level services used by `fs2.c` channel operations.

Research relevance:
- This is the main on-disk metadata engine for `hjfs`, including allocator correctness, snapshot/copy-on-write behavior, and directory lifecycle semantics.
