# File Research: sources/os/linux/linux-stable/fs/squashfs/page_actor.h

## Summary
Declares `struct squashfs_page_actor` and inline helpers for actor use and teardown.

## Main Contents
- Buffer/page union for intermediate and direct output modes.
- Function pointers for first/next/finish page operations.
- State fields for direct page-cache iteration and temporary buffers.
- Inline wrappers `squashfs_first_page()`, `squashfs_next_page()`, `squashfs_finish_page()`, and `squashfs_actor_nobuff()`.

## Important Details
`squashfs_page_actor_free()` returns the last page if every supplied page was consumed, otherwise `ERR_PTR(-EIO)`. This return value is used by direct read and readahead paths to decide whether decompression filled a complete page set.

## Risks
The actor structure is shared with all compression wrappers. Backend code must honor `ERR_PTR`, `NULL`, and normal page-buffer returns from the page iteration helpers.
