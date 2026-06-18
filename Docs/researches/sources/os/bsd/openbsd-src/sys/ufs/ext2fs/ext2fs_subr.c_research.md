# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_subr.c

Provides ext2 helper routines for directory block access and vnode initialization.

Key entry points:
- `ext2fs_bufatoff()` returns a buffer for a directory offset and optionally a pointer inside the buffer.
- `ext2fs_vinit()` initializes vnode type/op vectors for an inode and handles special-device aliasing.

Important behavior:
- `ext2fs_bufatoff()` resolves ext4 extents directly when the inode has `EXT4_EXTENTS`; otherwise it falls back to vnode logical `bread()`.
- Special block/char vnodes are switched to `ext2fs_specvops` and passed through `checkalias()`.
- FIFO vnodes use `ext2fs_fifovops` when FIFO support is compiled in.
- The root inode gets `VROOT`.
- `i_modrev` is initialized from microtime.

Dependencies:
- Uses ext2 extent lookup, UFS inode/vnode wrappers, buffer cache, and spec/fifo vnode infrastructure.

Watch points:
- Extent lookup failure in `ext2fs_bufatoff()` silently falls back to normal block mapping.
- Device alias handling transfers `v_data` from the discarded vnode to the alias vnode.
