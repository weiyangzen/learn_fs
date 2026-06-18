# File Research: sources/local-fs/erofs-utils/lib/inode.c

This is the main inode import, tree traversal, directory serialization, data-write, and on-disk inode flushing implementation for erofs-utils. It bridges host filesystem metadata, rebuild/import sources, compression, packed fragments, metadata zones, and final EROFS inode layout.

Major responsibilities:
- File type translation between POSIX modes, EROFS file types, and dirent `d_type`.
- In-memory inode deduplication by source `(dev, ino)` for hard links.
- Dentry allocation, sorting, NID invalidation, and directory stream generation.
- Data block reservation and writing for unencoded, compressed, chunked, symlink, special, directory, and special packed/metabox inodes.
- On-disk compact/extended inode selection and serialization.
- Whole-tree mkfs import, optionally with a worker thread for nondirectory data jobs.
- Incremental/rebuild integration with base directories and whiteout handling.

Key data/lifecycle functions:
- `erofs_inode_manager_init()`, `erofs_insert_ihash()`, `erofs_remove_ihash()`, `erofs_iget()`, `erofs_iput()` manage the global inode hash and refcounted in-memory inodes.
- `erofs_new_inode()` creates target-associated inodes with default flat-plain layout and unallocated NID.
- `erofs_fill_inode()` and `__erofs_fill_inode()` apply uid/gid fixes, Android fsconfig when enabled, timestamp policy, mode, size, source path, and compact/extended layout choice.
- `erofs_iget_from_local()` imports local `lstat()` metadata and reuses non-directory inodes when hard links are not dereferenced.

Directory handling:
- `erofs_d_alloc()` creates padded dentries.
- `erofs_dentry_mergesort()` sorts directory entries in EROFS order.
- `erofs_prepare_dir_file()` adds `.` unless omitted, always adds `..`, computes packed directory size, and marks layout undecided.
- `erofs_dirwriter_open()` exposes generated directory blocks through an `erofs_vfile`.
- `fill_dirblock()` emits dirent headers followed by names.
- `erofs_rebuild_inode_fix_pnid()` can patch `..` in reused base directories during incremental/rebuild flows.

Data writing:
- `erofs_allocate_inode_bh_data()` reserves data or directory blocks in the main buffer manager or metadata zone.
- `erofs_write_unencoded_data()` copies file data into allocated blocks and stores tail data for possible inline placement.
- `erofs_write_unencoded_file()` routes chunked files to blobchunk code when configured, otherwise flat inline/plain.
- `erofs_write_file_from_buffer()` handles symlinks and in-memory buffers.
- `erofs_write_dir_file()` writes directory data compressed or unencoded.
- `erofs_write_tail_end()` either binds tail data as inline metadata or writes a padded tail block.

On-disk serialization:
- `erofs_lookupnid()` assigns NIDs once inode buffer placement is known; metabox NIDs carry the metabox bit.
- `erofs_prepare_inode_buffer()` chooses inline vs non-inline, handles 48-bit requirements, allocates inode buffers, attaches inline data buffers, and registers flush callbacks.
- `erofs_iflush()` writes compact or extended inode structures, xattr ibodies, compression metadata, or chunk indexes.
- `erofs_fixup_root_inode()` updates `sbi->root_nid` or copies a late root inode back into an earlier root slot when old non-48-bit root constraints require it.

Tree import:
- `erofs_mkfs_import_localdir()` reads local directories, applies exclude rules, imports child inodes, and tracks whiteouts.
- `erofs_prepare_dir_inode()` merges local, rebuild, incremental base entries, strips overlayfs whiteouts if configured, and finalizes nlink/counts.
- `erofs_mkfs_begin_nondirectory()` opens file data, sets optional SHA-256 fingerprint xattr, starts compression if available and applicable, then queues the data job.
- `erofs_mkfs_dump_tree()` drives traversal from root, handles hard links, directory write ordering, pending grouped directory data, and root NID assignment.
- `erofs_importer_load_tree()` is the public entry point; incremental builds are rejected for metabox filesystems.
- `erofs_mkfs_build_special_from_fd()` imports generated special files such as packed inode/metabox from an fd.

Concurrency:
- When `EROFS_MT_ENABLED`, a bounded pthread queue handles mkfs job items asynchronously. The queue size is configured or derived from the file descriptor limit.

Important invariants:
- `inode->bh` placement determines NID.
- Special identifiers use pointer identity (`EROFS_PACKED_INODE`, `EROFS_METABOX_INODE`) and are not freed as normal paths.
- Compact inodes are upgraded when uid/gid/nlink/size/mtime/48-bit constraints require extended layout unless compact is forced.
- Directory data is generated lazily from dentries, so dentries hold inode refs until their NIDs are fixed.

Risks / notes:
- Many helper return values from `erofs_prepare_inode_buffer()` / `erofs_write_tail_end()` are assumed in some paths; failures would be serious because they occur late in object construction.
- The file is a central integration point; changes can affect local mkfs, OCI/S3 import, rebuild, incremental mode, compression, metadata zones, and root placement.
