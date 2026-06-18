# File Research: sources/os/linux/linux/fs/ntfs/dir.c

## Purpose
Implements NTFS directory operations for the Linux NTFS driver, centered on `$I30` directory indexes: name lookup, directory iteration, empty-directory checks, open/release state, and directory fsync.

## Key Elements
Defines the global little-endian `$I30` name used by directory index attributes. `ntfs_lookup_inode_by_name()` searches a directory's `$INDEX_ROOT` first, then descends through `$INDEX_ALLOCATION` blocks when the B+tree has child nodes. It performs exact case-sensitive matching first, keeps a single case-insensitive fallback for non-case-sensitive mounts and DOS namespace aliases, and returns an NTFS MFT reference rather than a plain inode number.

Directory iteration is built around `ntfs_readdir()`, `ntfs_index_ctx_get()`, `ntfs_index_walk_down()`, and `ntfs_index_next()`. It emits `.` and `..`, walks index entries in collation order, converts UTF-16 NTFS names through the mount NLS table, skips DOS-only aliases, root self references, optionally hidden/system files, and chooses `d_type` from directory, reparse tag, or regular file attributes. `struct ntfs_file_private` stores the last key and logical position so a later iterate call can resume through `ntfs_index_lookup()` instead of restarting with a linear walk.

The file adds directory-oriented readahead in two places: `ntfs_ia_blocks_readahead()` reads ahead index allocation pages, while an rb-tree of `ntfs_index_ra` ranges batches readahead for referenced MFT records during iteration.

## Dependencies And Integration
Depends on `dir.h`, `mft.h`, `ntfs.h`, `index.h`, and `reparse.h`. It calls low-level MFT mapping, attribute search, index validation, NTFS collation/name comparison, reparse d_type classification, and generic VFS directory/file operation helpers. `ntfs_dir_ops` wires the implementation into VFS `.iterate_shared`, `.fsync`, `.open`, `.release`, ioctl, compat ioctl, and lease hooks.

## Behavior/Risks
Index parsing is corruption-sensitive and uses extensive bounds checks for entry length, key length, index block VCN, INDX magic, block size, and page-boundary assumptions. Lookup allocates `struct ntfs_name` only when dcache alias handling needs the on-disk spelling or DOS-name marker. `ntfs_check_empty_dir()` treats a directory as empty only when the resident index root contains only the terminal entry. `ntfs_dir_fsync()` is broad: it writes parent directory index allocation inodes for hard links, the directory data, the index bitmap, MFT bitmap, LCN bitmap, `$MFT`, and finally syncs the block device.
