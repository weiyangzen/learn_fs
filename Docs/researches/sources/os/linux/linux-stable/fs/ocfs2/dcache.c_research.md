# File Research: sources/os/linux/linux-stable/fs/ocfs2/dcache.c

## Summary
Implements OCFS2 dentry cache validation and cluster dentry-lock attachment. It keeps local VFS dentries coherent with clustered directory operations by associating positive dentries with lock resources keyed by parent directory block and target inode, validating stale dentries, sharing locks among local aliases, releasing dentry locks on final put, and preserving lock semantics across rename/move.

## Main Responsibilities
- Attach generation values to negative dentries so they can be invalidated when the parent directory lock generation changes.
- Revalidate positive and negative dentries for VFS lookup.
- Find local aliases for an inode under a specific parent directory block.
- Attach positive dentries to an `ocfs2_dentry_lock`, creating or reusing the per-parent/inode lock resource.
- Drop dentry-lock references and release underlying cluster lock resources.
- Provide `d_iput` cleanup and a lock-aware `d_move()` helper used by rename.
- Publish `ocfs2_dentry_ops`.

## Key Interfaces
- `ocfs2_dentry_attach_gen()` stores the parent directory lock generation on a negative dentry.
- `ocfs2_dentry_attach_lock()` attaches a positive dentry to a cluster dentry lock and briefly takes/releases the PR lock.
- `ocfs2_find_local_alias()` searches the inode alias list for another dentry with the same parent block.
- `ocfs2_dentry_lock_put()` decrements lock sharing and destroys the lock when the last dentry reference disappears.
- `ocfs2_dentry_move()` updates dentry lock ownership when a dentry moves between directories.
- `ocfs2_dentry_ops` installs `.d_revalidate` and `.d_iput`.

## Important Behavior
Negative dentry validation compares the stored generation in `d_fsdata` to `OCFS2_I(dir)->ip_dir_lock_gen`. A mismatch invalidates the dentry. Positive dentries are invalidated if they point to the root inode, a bad inode, an inode marked `OCFS2_INODE_DELETED`, an inode with zero link count, or a dentry missing cluster-lock state.

Dentry locks are per target inode within a parent directory, not per full filename. The file comments explain this as a compromise: full names are too large for cluster lock names, but parent-directory scoping plus directory locks still lets all nodes agree about unlink/rename invalidation.

`ocfs2_dentry_attach_lock()` is called with parent directory semaphore and parent directory cluster lock held. It reuses an alias lock when one already exists for the same parent block; otherwise it allocates a new `ocfs2_dentry_lock`, grabs an inode reference, initializes the lock resource, installs it under `dentry_attach_lock`, and acquires/releases the dentry lock once to establish PR-mode notification.

`ocfs2_dentry_move()` leaves lock state unchanged for same-directory moves. Cross-directory moves drop the old dentry-lock reference, clear `d_fsdata`, attach a new lock keyed by the new parent block, and then calls `d_move()`.

## State and Synchronization
The global `dentry_attach_lock` protects attachment/detachment and the shared `dl_count`. Alias search uses `inode->i_lock` and each dentry's `d_lock`. Inode deletion state is checked under `OCFS2_I(inode)->ip_lock`. Dentry-lock release delegates to `ocfs2_simple_drop_lockres()` and `ocfs2_lock_res_free()`.

## Cross-File Interactions
This file depends on OCFS2 inode state from `inode.h`, lock resource helpers from `dlmglue.h`, allocation and file headers for filesystem context, and VFS dentry operations. Rename code calls `ocfs2_dentry_move()`, lookup/create paths call `ocfs2_dentry_attach_lock()`, and remote downconvert/delete logic relies on these lock resources to unhash aliases.

## Risks
`d_fsdata` is overloaded: negative dentries store a generation value, while positive dentries store an `ocfs2_dentry_lock *`. Converting a negative dentry to positive must clear the generation before lock attachment. Races with pruning and concurrent attachment are guarded by `dentry_attach_lock`, and mistakes can leak inode references or create duplicate lock resources. Missing dentry locks on live hashed positive dentries are logged as errors because they undermine clustered coherency.
