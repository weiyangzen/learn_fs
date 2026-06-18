# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_vnops.c

Read completely: 2222 lines.

Implements NetBSD UDF vnode operations for regular file I/O, directory lookup/iteration, attributes, permissions, symlinks, creation/removal, vnode lifecycle, syncing, advisory locking, and operation-vector registration.

Reads and writes use UBC through `ubc_uiomove()`, with file growth handled by `udf_grow_node()` and rollback through `udf_chsize()` on write failure. Directory reads synthesize `.` at offset zero, then walk the UDF FID stream with `udf_read_fid_stream()`, skipping deleted and invisible entries. Lookup checks execute permission, rejects read-only DELETE/RENAME, uses the name cache, handles `.` and `..`, resolves names through `udf_lookup_name_in_dir()`, and instantiates nodes with `udf_get_node()`.

Attribute handling maps file/extfile entries into `vattr`, including UID/GID anonymous translation, UDF timestamps, byte counts, link counts, and special-device extended attributes. Symlink support converts between Unix paths and UDF path components, including root and mount-root component types. Mutation operations delegate to UDF helpers: `udf_create_node()`, `udf_dir_attach()`, `udf_dir_detach()`, `udf_resize_node()`, `udf_shrink_node()`, and `udf_rename()` from `udf_rename.c`.

Lifecycle paths recycle unlinked non-system nodes, delete backing allocation on reclaim, wait for outstanding node-descriptor writes, and dispose node state. `udf_fsync()` flushes buffers, handles wait/non-wait behavior, skips metadata writeback on read-only mounts, and writes dirty node descriptors. `udf_trivial_bmap()` maps logical blocks 1:1 to the UDF vnode and `udf_vfsstrategy()` dispatches translated file-buffer I/O through UDF file-buffer helpers.

Risks and notes: extended attribute reads/writes are marked unimplemented; chflags is unsupported; file flags such as immutable/append are TODO placeholders; `_PC_FILESIZEBITS` returns 64 despite an in-source note that POSIX math suggests 65; several vnode table entries are marked TODO or “TEST ME”; `udf_getattr()` ignores `udf_do_readlink()` errors when computing symlink size; `udf_do_symlink()` has subtle absolute-path mountpoint handling; and `udf_fsync()` does not issue a device cache flush for `FSYNC_CACHE`.
