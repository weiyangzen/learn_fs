# File Research: sources/os/linux/linux/fs/afs/symlink.c

## Scope

This file implements symlink-content caching, validation-aware `get_link`/`readlink`, single-shot symlink reads, cache writeback of symlink blobs, and eviction/invalidation of symlink copies.

## Public And Internal APIs Covered

- Symlink cache lifecycle: `afs_invalidate_symlink()`, `afs_evict_symlink()`, `afs_init_new_symlink()`.
- VFS inode ops: `afs_get_link()` and `afs_readlink()`.
- Address-space op: `afs_symlink_writepages()`.
- Exported operation tables: `afs_symlink_inode_operations` and `afs_symlink_aops`.

## Control Flow And Behavior

- Symlink contents are stored as refcounted `struct afs_symlink` objects under an RCU vnode pointer.
- Locally created symlinks are installed immediately and optionally copied into a folio-queue buffer for fscache writeback.
- Reads enforce AFS’s requirement to fetch symlink contents in one unit. Files larger than `PAGE_SIZE - 1` fail with `-EFBIG`.
- `afs_get_link()` supports RCU pathwalk only when a cached symlink exists and vnode validity is still good; otherwise it returns `-ECHILD`.
- Blocking lookup validates the vnode, takes `validate_lock`, downloads contents if missing, references the cached symlink, and returns it with a delayed put callback.
- If fscache is not enabled, the temporary folio-queue buffer is freed after reading.
- Writeback writes the symlink blob only when a callback promise still exists, then frees the buffer on success.

## State And Data Structures

- Uses `vnode->symlink`, `vnode->directory`, and `vnode->directory_size` to store content and cache/writeback buffers.
- `validate_lock` protects replacement and coherent read/download transitions.

## Dependencies

- Netfs single read/writeback helpers, fscache cookie state, folio queues, VFS delayed-call symlink API, and AFS validation.

## Risks And Invariants

- Symlink reads must be single-shot to avoid observing content modified between partial reads.
- RCU pathwalk cannot trigger validation or allocation.
- Cached symlink content is invalidated on callback/data-version changes.
