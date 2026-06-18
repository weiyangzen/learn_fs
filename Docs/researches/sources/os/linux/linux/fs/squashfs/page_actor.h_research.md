# File Research: sources/os/linux/linux/fs/squashfs/page_actor.h

Declares `struct squashfs_page_actor` and inline wrappers for first/next/finish operations.

The actor stores either buffer pointers or page pointers, mapping state, optional temporary buffer, last page, output length, page count, current index, and decompressor buffer policy.

`squashfs_page_actor_free()` frees temporary state and returns the last completed page, or `ERR_PTR(-EIO)` if not all expected pages were consumed.

`squashfs_actor_nobuff()` disables temporary-buffer fallback for paths that require direct copying behavior.
