# File Research: sources/os/linux/linux-stable/fs/afs/dir_silly.c

## Summary
Implements AFS silly rename handling for unlinking open files. Because AFS servers are stateless with respect to open file references, the client renames an open-but-unlinked file to a hidden `.__afsNNNN` name and removes it later when the dentry/inode is finally released.

## Main Responsibilities
- Performs server-side rename to a generated silly name.
- Marks dentries with `DCACHE_NFSFS_RENAMED`.
- Locally edits cached directory contents after successful silly rename/unlink.
- Removes silly-renamed files during `dentry_iput`.
- Handles lookup races while transferring silly-delete state to aliases.

## Key APIs
- `afs_sillyrename()`.
- `afs_silly_iput()`.
- Internal operations: `afs_do_silly_rename()` and `afs_do_silly_unlink()`.

## Important Behavior
Silly names use the `.__afs` prefix, which the comment notes is understood by the AFS salvager. The generated name is found with `lookup_noperm()` and must be negative before use.

On rename success, the target vnode gets `AFS_VNODE_SILLY_DELETED`, and `d_move()` moves the original dentry to the silly dentry. On `-ERESTARTSYS`, both dentries are dropped so a later lookup will revalidate unknown server state.

`afs_silly_iput()` uses `d_alloc_parallel()` to avoid racing lookup. If another lookup already instantiated an alias, it transfers `DCACHE_NFSFS_RENAMED` to that alias instead of performing unlink itself.

## State and Synchronization
Directory updates use `dvnode->validate_lock` and only apply local edits when the cached directory is valid and the returned data version matches the expected delta. `dvnode->rmdir_lock` protects silly-unlink against directory removal races. Lock state is forced to `AFS_VNODE_LOCK_DELETED` before final silly unlink to suppress lock-release complaints.

## Risks
The hidden-name generator is a static counter and retries until it finds a negative dentry. If rename result is interrupted, the client deliberately drops cached dentries because server state is unknown. The final unlink uses `dvnode->silly_key`; stale or missing key state would affect cleanup.
