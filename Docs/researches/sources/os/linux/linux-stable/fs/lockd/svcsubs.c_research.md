# File Research: sources/os/linux/linux-stable/fs/lockd/svcsubs.c

## Summary
Support routines for lockd server file tracking and resource reclamation. It maintains the global `nlm_file` hash table, opens/closes backing VFS files through nfsd callbacks, and traverses locks, blocks, and shares for cleanup.

## Main APIs
- `nlm_lookup_file()` maps an NFS file handle to an `nlm_file` and opens read/write backing files.
- `nlm_release_file()` drops references and frees unused file records.
- `nlmsvc_mark_resources()`, `nlmsvc_free_host_resources()`, `nlmsvc_invalidate_all()`.
- `nlmsvc_unlock_all_by_sb()` and `nlmsvc_unlock_all_by_ip()` export bulk unlock operations.

## Behavior
Files are hashed by the first NFSv2 file-handle bytes. `nlm_do_fopen()` tries required open modes via `nlmsvc_ops->fopen()`, translating `-EWOULDBLOCK` to drop-reply, `-ESTALE` to stale-FH, and other errors to failed. Cleanup walks VFS POSIX locks on each inode, lockd blocks, and DOS shares, then closes and frees unused file records.

## State and Synchronization
`nlm_file_mutex` protects the global hash table and file reference count. Each `nlm_file` has `f_mutex` for block-list-sensitive operations. VFS lock lists are inspected under each inode lock context’s `flc_lock`.

## Dependencies
nfsd/lockd binding callbacks, generic VFS lock context APIs, `svclock.c` block traversal, `svcshare.c` share traversal, and RPC address comparison.

## Risks
The comments explicitly avoid normal refcount purity because `fs/locks.c` can split/delete locks without lockd notification. Cleanup therefore relies on repeated global traversal and lock-list inspection. Failure to remove all host locks triggers `BUG()`.
