# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/namei.c

Implements pathname traversal for libext2fs. Public entry points are `ext2fs_namei()`, `ext2fs_namei_follow()`, and `ext2fs_follow_link()`.

`dir_namei()` walks path components relative to a root and cwd, resetting to root on absolute paths. It uses `ext2fs_lookup()` for each component and can follow symlinks between components.

`follow_link()` supports fast symlinks stored in `i_block`, inline-data symlinks, and block-backed symlinks. It enforces `EXT2FS_MAX_NESTED_LINKS` to prevent symlink loops.

The implementation uses caller-sized block buffers for lookup and raw symlink block reads. It does not implement Unix permission checks; it resolves ext filesystem metadata paths only.
