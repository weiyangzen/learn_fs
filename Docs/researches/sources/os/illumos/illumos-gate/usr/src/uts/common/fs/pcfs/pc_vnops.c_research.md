# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pcfs/pc_vnops.c

PCFS vnode operation implementation for file I/O, attributes, directory operations, VM paging, mmap, pathconf, file handles, and long filename extraction/rendering.

Key responsibilities:
- Defines separate vnode operation templates for regular files and directories.
- Implements read/write through `pcfs_read()`, `pcfs_write()`, and `rwpcp()`, using segmap, cluster allocation, zero-fill behavior for skipped clusters, FAT file-size limits, and sync flags.
- Implements attribute get/set, including FAT mode approximation, boot-partition permissions, FAT timestamp conversion/clamping, truncation, and access/modification time updates.
- Implements access, fsync, inactive, lookup, create, remove, rename, mkdir, rmdir, and readdir vnode operations by delegating to pcnode and directory helpers.
- Synthesizes root `.` and `..` entries for readdir and reads both long and short FAT directory entries into illumos dirent format.
- Implements VM page read/write paths through `pcfs_getpage()`, `pcfs_getapage()`, `pcfs_putpage()`, and `pcfs_putapage()`, translating FAT cluster mappings into block-device page I/O.
- Supports mmap through `pcfs_map()`, simple addmap/delmap, seek validation, pathconf values, and `F_FREESP` truncation via `pcfs_space()`.
- Builds and validates FAT long filename chunks with `set_long_fn_chunk()`, `get_long_fn_chunk()`, `pc_checksum_long_fn()`, and `pc_extract_long_fn()`.
- Emits short and long names for directory reads with `pc_read_short_fn()` and `pc_read_long_fn()`.
- Produces and resolves NFS-style file identifiers through `pcfs_fid()` and the VFS `vget` code in `pc_vfsops.c`.

Dependencies:
- Uses VM/page/segmap/pvn infrastructure, VFS/vnode operations, directory and allocation routines, Unicode conversion/textprep, PCFS locking, and policy hooks.
- Depends on FAT limits such as 32-bit file size and two-second timestamp resolution.

Notable risks:
- PCFS does not support sparse files; writes beyond EOF allocate intermediate clusters and only zero-fill skipped clusters in some paths.
- Pageout returns `ENOMEM` to avoid blocking/deadlock with the global PCFS lock, and asynchronous putpage is forcibly disabled.
- mmap is restricted to offsets/ranges below the FAT 32-bit file-size boundary.
- Long filename extraction treats detached, checksum-mismatched, invalid UTF, hidden, or malformed chains as invalid and resumes scanning.
- `pcfs_getapage()` has a panic path if `pvn_read_kluster()` unexpectedly returns NULL.
