# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_lookup.c

## Purpose
Implements ext2 directory read, lookup, directory-entry mutation, empty-directory checks, and rename ancestry validation for FreeBSD ext2fs.

## Main Elements
- `ext2_readdir()` reads ext2 directory blocks, validates record sizes, converts ext2 file types to BSD `dirent` types, emits cookies, and reports EOF.
- `ext2_lookup()` delegates to `ext2_lookup_ino()`, the central cached lookup implementation.
- `ext2_lookup_ino()` handles LOOKUP/CREATE/RENAME/DELETE semantics, negative cache entries, parent locking, sticky-directory deletion checks, `.`/`..` handling, vnode acquisition, htree lookup fallback, and directory insertion slot tracking.
- `ext2_search_dirblock()` scans one directory block, detects matching names, tracks reusable or compactable free space, and skips checksum tails.
- `ext2_check_direntry()` validates record length, alignment, block bounds, inode range, and root entry shape.
- `ext2_add_first_entry()`, `ext2_add_entry()`, `ext2_direnter()`, `ext2_dirremove()`, and `ext2_dirrewrite()` insert, compact, remove, or retarget directory entries, updating metadata checksums when needed.
- `ext2_dirempty()` accepts only `.` and correct `..` entries.
- `ext2_checkpath()` walks `..` upward to prevent directory rename cycles.

## Dependencies And Integration
Uses `ext2_blkatoff()`, htree helpers, checksum helpers, `ext2_truncate()`, vnode/namecache APIs, and ext2 inode slot fields (`i_offset`, `i_count`, `i_endoff`, `i_diroff`).

## Risk Notes
Directory corruption is mostly reported through SDT probes and `EIO`/`EINVAL`. HTree failures fall back to linear search, but directory checksum and compaction correctness are critical because mutations rewrite shared directory blocks.
