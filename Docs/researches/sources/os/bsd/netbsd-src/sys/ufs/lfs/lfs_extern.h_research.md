# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_extern.h

Read completely: 349 lines.

Declares the LFS cross-file public/internal API, global variables, pools, sysctl numeric identifiers, and vnode/VFS operation entry points.

Public definitions:
- Defines `IS_LFS_VNODE()` using vnode tag `VT_LFS`.
- Defines LFS sysctl identifiers for write-indirect behavior, clean vnode list placement, stats, max pages, page trip threshold, stats retrieval, roll-forward writes, debug, lazy sync behavior, and roll-forward limit.
- Declares forward types used across LFS without requiring all implementation headers.

Kernel globals:
- Declares condition variables, memory pools, global locked-buffer counters, debug/cleaner settings, global lock, writing condition variable, and roll-forward limits.
- Declares `M_SEGMENT` malloc type.

Function declarations:
- Allocation: inode allocation/free, fixed allocation, free-list ordering, ifile extension, orphan handling, orphan freeing, and DEBUG free-list checking.
- Block allocation/I/O: `lfs_balloc`, block register/deregister helpers, availability wait, bwrite, fits, flush, pressure checks, buffer allocation/free, reservation, and resource thresholds.
- Debug: DEBUG-only write logging, dumps, segment summary/buffer checks, and subsystem logging.
- Inode/segment: update, truncate, ifile lookup, segment-use finalization, segment write/gather/update/invalidate/rewrite, superblock writes, finfo acquisition, and async completion helpers.
- Cleaner/roll-forward/syscalls: clean control, cleaner thread, rewrite file/segments, roll-forward parsing, segment clean/check, bmapv/markv, segwait, and cleaner control.
- VFS/vnode operations: mount operation prototypes, vnode initialization, resize/reset availability, vnode operation entry points, buffered read/write, and vnodeop tables.

Checksum declarations:
- `cksum()`, `lfs_cksum_part()`, `lfs_sb_cksum()`, and identity `lfs_cksum_fold()` are exposed outside `_KERNEL` as well.

Risks and notes:
- This header is the dependency hub for LFS implementation files; declaration drift can break many compilation units.
- Some declarations expose legacy or currently non-operable surfaces, including quota2 placeholders and disabled rewrite prototypes.
