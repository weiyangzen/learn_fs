# File Research: sources/os/linux/linux/fs/ocfs2/dcache.c

## Purpose
Implements OCFS2 dentry cache behavior, including dentry revalidation, negative dentry generation tracking, cluster dentry-lock attachment/sharing, alias lookup, dentry lock cleanup, and dentry movement during rename.

## Negative Dentry Handling
`ocfs2_dentry_attach_gen()` stores the parent directory lock generation in `dentry->d_fsdata` for negative dentries. `ocfs2_dentry_revalidate()` compares that stored generation to the parent’s current `ip_dir_lock_gen`; mismatches invalidate the negative dentry.

## Positive Dentry Revalidation
`ocfs2_dentry_revalidate()` rejects:
- RCU lookup mode with `-ECHILD`
- root inode and bad inode cases
- inodes marked `OCFS2_INODE_DELETED`
- inodes with `i_nlink == 0`
- positive dentries without attached dentry-lock data.

Valid positive dentries rely on cluster dentry locks to receive invalidation on remote unlink/rename.

## Alias Lookup
`ocfs2_find_local_alias()` walks an inode’s alias list under `inode->i_lock`, checks parent block number and dentry fsdata, optionally skips unhashed dentries, and returns a pinned matching alias. This lets multiple local dentries for links in the same parent share one dentry lock.

## Dentry Lock Attachment
`ocfs2_dentry_attach_lock()` attaches a positive dentry to an `ocfs2_dentry_lock`, requiring the parent directory semaphore and cluster lock to already be held. It:
- ignores negative dentries.
- handles negative-to-positive conversion by clearing generation fsdata.
- reuses an existing alias lock if possible.
- otherwise allocates a new `ocfs2_dentry_lock`, grabs an inode reference, initializes a lock resource, and stores parent block number.
- increments `dl_count` under global `dentry_attach_lock`.
- briefly obtains/releases the PR-mode dentry lock to establish cluster notification.

## Lock Cleanup
`ocfs2_dentry_iput()` is the dentry operation for final inode put. It drops the dentry lock count and eventually frees the lock resource and inode reference through `ocfs2_dentry_lock_put()` and `ocfs2_drop_dentry_lock()`.

If a positive hashed dentry lacks lock data, it logs an error because cluster invalidation would be missing.

## Rename Move Handling
`ocfs2_dentry_move()` performs `d_move()` while keeping lock data consistent. If the parent directory changes, it drops the old dentry lock and attaches a new one based on the new parent block number before moving the dentry.

## Synchronization
The file uses:
- inode alias lock and dentry lock for alias traversal
- global `dentry_attach_lock` for attach/detach count changes
- OCFS2 cluster lock/resource APIs for distributed invalidation.
