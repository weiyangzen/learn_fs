# File Research: sources/os/linux/linux-stable/fs/udf/dir.c

## Summary
Provides UDF directory file operations, primarily `readdir`, with directory position validation using inode version cookies.

## Key Functions
- `udf_readdir()`: emits `.` and directory entries, handles parent entries as `..`, skips hidden/deleted entries unless mount flags expose them, and converts UDF names to Linux names.
- `udf_dir_open()` / `udf_dir_release()`: allocate and free the per-open inode-version cookie.
- `udf_dir_llseek()`: uses `generic_llseek_cookie()` so seeks invalidate cached directory position state.
- `udf_dir_operations`: directory file operations table.

## Important Behavior
UDF directory offsets exposed to users are encoded as `(on_disk_pos >> 2) + 1`, leaving position zero for `.`. If the directory inode version changes since the last successful read or seek, the code rescans from the beginning to validate the requested position because UDF entries do not have a reliable self-identifying boundary.

Actual directory-entry parsing is delegated to `udf_fileident_iter` helpers in `directory.c`.

## Risks
Correct directory seeking depends on inode version tracking. If the version cookie is stale, scanning from the beginning is required to avoid starting in the middle of a variable-length file identifier descriptor.
