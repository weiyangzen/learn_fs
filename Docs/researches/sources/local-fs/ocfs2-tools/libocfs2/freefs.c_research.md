# File Research: sources/local-fs/ocfs2-tools/libocfs2/freefs.c

Purpose: frees an `ocfs2_filesys` object and its owned resources.

Key API:
- `ocfs2_freefs()`

Behavior:
- Aborts if passed `NULL`.
- Frees original superblock, active superblock, and device-name strings when present.
- Closes the I/O channel with `io_close()`.
- Frees the filesystem object itself.

Dependencies:
- Uses `ocfs2_free()` and `io_close()`.

Notable behavior:
- This is a low-level destructor and assumes callers pass a valid filesystem handle.
- It does not explicitly handle DLM, image state, or other optional substructures; those must be cleaned elsewhere before this destructor or by other close paths.
