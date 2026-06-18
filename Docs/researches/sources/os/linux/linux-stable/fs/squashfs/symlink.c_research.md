# File Research: sources/os/linux/linux-stable/fs/squashfs/symlink.c

## Summary
Implements page-cache reading for Squashfs symlink bodies stored inline in inode-table metadata.

## Key APIs
- `squashfs_symlink_aops`.
- `squashfs_symlink_inode_ops`.

## Important Behavior
The symlink read path skips to the requested folio offset in metadata, then reads one or more metadata cache entries directly with `squashfs_cache_get()` and copies into a locally mapped folio. It avoids `squashfs_read_metadata()` for the copy loop because that helper can sleep while the folio is kmapped.

The final partial page is zero-filled, dcache is flushed, and the folio is completed through `folio_end_read()`.

## Risks
The path must balance cache puts on every error and avoid sleeping while using `kmap_local_folio()`. Inode parsing limits symlink size to at most one page, simplifying the address-space behavior.
