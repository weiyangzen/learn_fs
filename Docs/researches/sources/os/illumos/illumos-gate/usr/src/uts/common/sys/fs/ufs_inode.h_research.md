# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_inode.h

## Role

Defines the UFS on-disk inode, in-core inode, per-mount UFS state, inode flags, directory operation support, queues, vnode conversions, and kernel function prototypes for UFS inode, directory, allocation, quota, lockfs, ACL, direct I/O, and xattr operations.

## Key Structures

- `struct icommon` is the persistent inode payload: mode, link count, short/long UID/GID, size, timestamps, direct/indirect block arrays, flags, block count, generation, shadow inode, and extended-attribute directory inode.
- `struct inode` wraps `icommon` with hash/free links, vnode/dev/vfs pointers, quota pointer, locks, read-ahead state, mapping and delayed-write fields, ACL pointer, directory-cache anchor, writer thread, and disk offset.
- `struct dinode` is the 128-byte on-disk inode wrapper.
- `struct ufs_slot` carries directory search/insert/remove state returned by name lookup inside a directory block.
- `struct instats` exposes inode-cache kstats.
- `struct ufs_q` is the generic queue/thread-control structure used by delete, reclaim, idle, and failure-handling threads.
- `struct ufs_delq_info` records unreclaimed blocks/files on the delete queue for statvfs accuracy.
- `iqhead_t` is the idle-queue head layout compatible with inode free-list links.
- `struct ufsvfs` is per-mounted-UFS state: VFS/root/dev/superblock, quota state, delete/reclaim queues, geometry constants, lockfs state, direct I/O settings, logging state, panic/fix state, deferred time settings, device ID, snapshot handle, summary logging flags, validfs state, and delete queue accounting.

## Flags and Conversions

Defines inode flags (`IUPD`, `IACC`, `IMOD`, `ICHG`, `IFASTSYMLNK`, `IDEL`, `IDIRECTIO`, `ISEQ`, etc.), cflags (`IXATTR`, `IFALLOCATE`, `ICOMPRESS`), file mode bits, sync modes, truncation/free flags, directory operation enums, bmap allocation mode enum, `ufid`, `UFS_HOLE`, `ESAME`, `VTOI`, `ITOV`, `ITOF`, inode hash macros, and fallocate block detection.

## Locking Contract

The file documents lock ordering: `i_rwlock > i_contents > i_tlock`, quota paths with `vfs_dqrwlock`, and inode-hash locking. It also documents special rules for `i_flag` updates and `i_seq`: timestamp-changing updates must increment `i_seq`, deferred updates may need `ISEQ`, and callers must respect `i_contents`/`i_tlock` rules.

## Kernel Interfaces

The prototype set covers inode lifecycle, read/write engines, directory lookup/entry/removal, allocation/free/reallocation, block mapping, superblock and summary sync, bad-block checks, page writeback, inode queues, delete/reclaim/idle threads, lockfs operations, ACL/shadow inode operations, direct I/O, PXFS data extensions, forced unmount freeze/thaw, and extended-attribute directories.

## Risk Notes

This is the central UFS implementation contract. Lock-order mistakes can deadlock across vnode, quota, and lockfs paths. The on-disk inode is fixed-size and compatibility-sensitive, including little-endian old-device handling.
