# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/lookup.c

Implements `ext2fs_lookup()`, a simple directory name lookup over `ext2fs_dir_iterate()`. The callback compares requested name length and bytes against each dirent and aborts iteration on match.

Returns the found inode through the caller pointer, or `EXT2_ET_FILE_NOT_FOUND` when no entry matches. This is a low-level exact-byte lookup; higher-level casefold or path traversal behavior is handled elsewhere.
