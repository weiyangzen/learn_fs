# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_syscalls.c

## Scope

Implements the legacy LFS cleaner system calls and their kernel helpers: block address mapping, live-block marking, segment cleaning, segment wait, cleaner-oriented vnode lookup, and fake cleaner buffers.

## APIs And Behavior

- `sys_lfs_markv()` copies user `BLOCK_INFO` arrays, including compatibility conversion when needed, and calls `lfs_markv()`.
- `lfs_markv()` authorizes cleaner access, validates inode bounds, references all target vnodes, takes cleaner and segment locks, verifies each block is still live at the supplied disk address/size, copies cleaner data into real or fake buffers, writes those blocks into a clean checkpoint, and returns `EAGAIN` when userland should retry.
- `sys_lfs_bmapv()` and `lfs_bmapv()` fill current disk addresses and block sizes for cleaner-supplied inode/lbn pairs, using Ifile entries and `VOP_BMAP`.
- `sys_lfs_segclean()` and `lfs_do_segclean()` mark an empty dirty inactive segment clean.
- `lfs_markclean()` updates superblock availability, cleaner info, segment flags, metadata counters, and statistics for a reclaimed segment.
- `lfs_segwait()` and `sys___lfs_segwait50()` sleep until segment activity occurs, optionally for all LFS mounts.
- `lfs_fastvget()` passes cleaner hints into vnode loading; `lfs_fakebuf()` builds cleaner data buffers from user memory for segment writing.

## State And Dependencies

The file bridges userland `cleanerd` and kernel LFS state. It depends on authorization hooks, VFS mount lookup/busying, Ifile entries, `VOP_BMAP`, LFS segment writer/checkpoint code, buffer cache primitives, and compatibility `BLOCK_INFO` layouts.

## Risks And Invariants

Cleaner input is explicitly distrusted enough to bounds-check inode numbers and block counts, but valid cleaning still depends on segment-create and current-map checks. `lfs_markv()` must not clean VU_DIROP directories and must write with `SEGM_CKP|SEGM_SYNC` so recovery never points at overwritten cleaner data. A failed `copyin()` while constructing buffers is treated as serious because cleaner-provided block contents cannot be trusted afterward.
