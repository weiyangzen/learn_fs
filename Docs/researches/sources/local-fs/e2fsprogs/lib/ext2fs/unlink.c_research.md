# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/unlink.c

## Purpose
Removes a directory entry from an ext filesystem directory.

## Main Behavior
- `ext2fs_unlink()` validates writable filesystem state and requires either a name or inode.
- Iterates the target directory with `DIRENT_FLAG_INCLUDE_EMPTY`.
- `unlink_proc()` matches by name length/content and optionally inode unless `EXT2FS_UNLINK_FORCE` is set.
- If the matched entry is not first in the block, it merges the entry into the previous record by extending `prev->rec_len`; otherwise it clears `dirent->inode`.

## Integration
Uses `ext2fs_dir_iterate()` and returns `DIRENT_CHANGED | DIRENT_ABORT` once the entry is removed.

## Risks / Notes
Returns `EXT2_ET_DIR_NO_SPACE` when no matching entry is found, reusing an existing error code for “not removed”.
