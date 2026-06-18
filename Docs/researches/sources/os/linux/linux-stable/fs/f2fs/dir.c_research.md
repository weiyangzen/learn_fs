# File Research: sources/os/linux/linux-stable/fs/f2fs/dir.c

`dir.c` implements F2FS directory lookup, dentry insertion/deletion, empty-directory checks, readdir, and directory file operations. It supports inline dentry directories, regular hashed directory blocks, encrypted names, and Unicode casefolded lookup.

Filename setup wraps fscrypt name preparation and adds F2FS-specific casefolding and hash calculation. `f2fs_setup_filename()` and `f2fs_prepare_lookup()` populate `struct f2fs_filename`; no-key encrypted names reuse the decoded hash, while normal names may allocate a casefold buffer and compute the F2FS dirhash. `f2fs_free_filename()` releases crypto and casefold buffers.

Directory layout helpers compute block counts, bucket counts, bucket sizes, and logical block indexes for F2FS’s level/bucket hash directory scheme. Lookup searches inline dentries first, then each hash level and bucket through `find_in_level()`. Casefolded directories may fall back to a linear search depending on the `lookup_mode` and superblock compatibility fallback state.

`f2fs_find_target_dentry()` scans a dentry bitmap, skips unused slots, validates nonzero name length, optionally filters by hash, matches names through Unicode casefold or fscrypt matching, and tracks maximum free slot runs for create acceleration. Missed lookups remember the current task on the directory inode to optimize the subsequent create path while still rechecking for stackable-filesystem races when needed.

Creation paths allocate or initialize inode metadata, create `.` and `..` for new directories, initialize ACL/security/encryption context, copy dentry name metadata into the inode page for recovery, handle encrypted+casefold hash storage or `LOST_PINO`, and update parent timestamps/depth/link counts. `f2fs_add_dentry()` prefers inline insertion and falls back to regular hashed-directory insertion.

Deletion clears the relevant bitmap slots, handles inline dentry deletion separately, truncates now-empty regular dentry blocks, clears dirty/page-cache state when a dentry page is deallocated, updates parent metadata, and drops the target inode link count. Directory emptiness scans inline or regular blocks, ignoring `.` and `..` in block zero.

`f2fs_fill_dentries()` is the core readdir scanner. It validates dentry name lengths and slot bounds, marks corruption and `SBI_NEED_FSCK` on invalid entries, converts encrypted disk names to user names, emits entries through `dir_emit()`, and optionally triggers node-page readahead for emitted inode numbers. `f2fs_readdir()` handles encrypted readdir setup, inline directories, page-cache readahead, fatal signal interruption, and trace reporting.

The exported `f2fs_dir_operations` provide llseek, generic directory read, shared iterate, fsync, ioctl/compat ioctl, and lease operations. Key dependencies are `data.c` folio read/new/truncate helpers, inline dentry helpers, inode/node update routines, fscrypt, Unicode casefold support, ACL/security initialization, orphan handling, and tracepoints.
