# File Research: sources/os/linux/linux-stable/fs/udf/file.c

## Summary
Implements UDF regular-file operations, mmap write-fault handling, write path expansion for inline files, ioctl handling, release-time preallocation cleanup, fsync, and setattr.

## Key Functions
- `udf_file_write_iter()`: performs generic write checks and expands in-ICB files to extent-backed files when writes no longer fit inline.
- `udf_page_mkwrite()`: prepares mmap writes, allocates blocks for non-inline files, and marks folios dirty.
- `udf_ioctl()`: handles volume identifier, block relocation, extended-attribute size, and extended-attribute block queries.
- `udf_release_file()`: on final writer close, discards preallocation and truncates tail extents.
- `udf_fsync()`: syncs file data and UDF metadata buffer tracking.
- `udf_setattr()`: enforces mount UID/GID override restrictions, handles size changes via `udf_setsize()`, updates extra permissions, and dirties the inode.

## Important Behavior
Files stored inline in the file entry (`ICBTAG_FLAG_AD_IN_ICB`) are expanded before writes that would exceed available entry space. After successful inline writes, `i_lenAlloc` is synchronized with `i_size`.

`udf_page_mkwrite()` uses page-fault accounting, invalidate locking, folio locking, and `__block_write_begin()` for non-inline files. Inline files are already allocated and only need dirtying.

Ioctls require read permission, and block relocation additionally requires `CAP_SYS_ADMIN`.

## Risks
Inline-to-extent conversion must happen under inode locking and invalidate locking to avoid stale page-cache state. Release-time truncation/preallocation cleanup assumes final writer detection using `i_writecount`.
