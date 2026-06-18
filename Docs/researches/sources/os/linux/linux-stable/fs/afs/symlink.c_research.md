# File Research: sources/os/linux/linux-stable/fs/afs/symlink.c

## Scope

Caches, validates, reads, exposes, and writes back AFS symlink contents.

## APIs And Behavior

- RCU/refcount helpers manage `struct afs_symlink` objects attached to vnodes.
- `afs_init_new_symlink()` installs newly created symlink text and optionally stages it in a folio queue for fscache writeback.
- `afs_read_symlink()`/`afs_do_read_symlink()` perform a single-unit netfs read, cap size at one page minus NUL, copy data into a NUL-terminated symlink object, and optionally discard transient folio buffers.
- `afs_get_link()` supports RCU pathwalk for already-valid cached links and locked slow-path download/validation otherwise.
- `afs_readlink()` copies cached link content to userspace.
- `afs_symlink_writepages()` writes staged symlink data to cache and frees the folio queue.

## State And Dependencies

Uses vnode `symlink`, `directory`, `directory_size`, `validate_lock`, callback promise state, fscache cookies, netfs single-read/writeback helpers, and VFS inode/address-space operation tables.

## Risks And Invariants

AFS symlinks are read as one unit to avoid content races across partial reads. RCU pathwalk may only return cached data when vnode validity is already proven. Cached symlink text is invalidated on callback-driven data changes.
