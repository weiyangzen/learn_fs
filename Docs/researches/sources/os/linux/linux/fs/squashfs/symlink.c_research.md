# File Research: sources/os/linux/linux/fs/squashfs/symlink.c

Implements symlink page reads.

SquashFS stores symlink bodies inside inode-table metadata. `squashfs_symlink_read_folio()` skips to the requested offset, then reads across metadata cache entries directly while using `kmap_local_folio()`.

It zero-fills the rest of the folio when the symlink tail is copied, flushes dcache, and completes the folio with success or error.

Exports symlink address-space ops and inode ops using `page_get_link` and SquashFS xattr listing.
