# File Research: sources/os/linux/linux/fs/udf/dir.c

## Purpose
Defines UDF directory file operations, primarily `readdir`.

## Main Functions
- `udf_readdir()`: emits `.` and directory entries by iterating UDF File Identifier Descriptors through `udf_fileident_iter`.
- `udf_dir_open()`: allocates a private inode-version cookie.
- `udf_dir_release()`: frees the private cookie.
- `udf_dir_llseek()`: uses `generic_llseek_cookie()` with the version cookie.
- `udf_dir_operations`: VFS file operations for directories.

## Important Design Points
- UDF has no reliable in-entry boundary marker for arbitrary seek positions, so if the directory inode version changed, readdir rescans from the beginning to validate position.
- `ctx->pos` is encoded as `(directory_byte_pos >> 2) + 1`, reserving zero for `.`.
- Hidden/deleted entries are filtered unless mount flags request unhide/undelete.
- Parent FID is emitted as `..`.
- Names are converted with `udf_get_filename()` before `dir_emit()`.

## Cross-File Relationships
- Uses iterator primitives from `directory.c`.
- Uses UDF mount flags and block mapping helpers from UDF support headers.
- Directory inode operations are assigned in `inode.c`.

## Risks / Review Notes
- If `file->private_data` allocation fails, open fails with `-ENOMEM`.
- `dir_emit()` inode number uses physical block from FID ICB location, not a stable UDF logical ID abstraction.
