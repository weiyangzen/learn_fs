# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_readwrite.c

Implements ext2 vnode read/write operations, with separate read paths for classic indirect blocks and ext4 extents.

Key entry points:
- `ext2fs_read()` dispatches to extent or indirect read based on `EXT4_EXTENTS`.
- `ext2_ind_read()` reads regular files, directories, and non-fast symlinks through vnode logical blocks.
- `ext4_ext_read()` resolves extent mappings and reads physical blocks from the device vnode.
- `ext2fs_write()` allocates buffers, copies user data, updates size, and writes buffers back.

Important behavior:
- Indirect reads use simple sequential read-ahead via `ci_lastr`.
- Extent reads use the extent cache, call `ext4_ext_find_extent()` on misses, and return success for cached gaps.
- Writes honor `IO_APPEND`, ext2 append-only files, vnode file-size limits, and filesystem overflow checks.
- Short or partial writes allocate with `B_CLRBUF` when needed.
- On `uiomove()` failure into a non-cleared buffer, the touched region is zeroed to avoid exposing stale page contents through mmap.
- `IO_UNIT` writes roll back file size and user I/O state via `ext2fs_truncate()`.

Dependencies:
- Uses `ext2fs_buf_alloc()`, `ext2fs_setsize()`, `ext2fs_update()`, `ext2fs_truncate()`, UVM vnode sizing, buffer cache, and extent helpers.

Watch points:
- Ext4 extent support here is read-oriented; writable ext4 extent semantics are not implemented in this file.
- `ext4_ext_read()` treats extent gaps as end of readable data for the current operation rather than synthesizing zero-filled holes.
