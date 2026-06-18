# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/get_pathname.c

## Role

Builds a pathname string from a directory inode and optional child inode.

## Main Flow

- `get_pathname_proc()` scans directory entries, records `..`, and captures the child name matching `search_ino`.
- `ext2fs_get_pathname_int()` recursively resolves parent paths up to depth 32.
- Handles `dir == ino`, missing/zero parents, non-directory fallback formatting, and unknown child names.
- Public `ext2fs_get_pathname()` allocates one block-sized directory buffer and normalizes `dir == ino` to directory-only lookup.

## Dependencies

Uses `ext2fs_dir_iterate`, directory-entry name helpers, and ext2fs memory allocation.

## Risks / Notes

- Recursion returns `"..."` when depth is exhausted or parent is zero.
- If the target child is not found under a valid parent, output includes `"???"`.
- Returned `name` is allocated and must be freed by the caller.
