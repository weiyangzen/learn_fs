# File Research: sources/os/linux/linux-stable/fs/ocfs2/dcache.h

## Summary
Declares the OCFS2 dentry cache and dentry-lock interface used by lookup, rename, and dentry operation code. It defines the per-dentry-lock wrapper that ties VFS dentries to OCFS2 lock resources.

## Main Responsibilities
- Define `struct ocfs2_dentry_lock`, including reference count, parent block number, pinned inode, and lock resource.
- Expose OCFS2 dentry operations through `ocfs2_dentry_ops`.
- Declare helpers for attaching, finding, moving, and releasing dentry locks.
- Expose the global `dentry_attach_lock` for code that must synchronize dentry lock attachment.
- Declare generation attachment for negative dentries.

## Key Interfaces
- `ocfs2_dentry_attach_lock()` attaches a positive dentry to a lock resource.
- `ocfs2_dentry_lock_put()` releases one dentry's reference to a shared lock.
- `ocfs2_find_local_alias()` finds a local alias with the same parent directory block.
- `ocfs2_dentry_move()` performs a d_move while preserving OCFS2 dentry lock invariants.
- `ocfs2_dentry_attach_gen()` stores a parent generation on a negative dentry.

## Important Behavior
The dentry lock keeps an inode reference until its lock resource is destroyed. This ensures the inode remains valid for the lifetime of the lock resource, even though the usual final release path is through `->d_iput()`.

## State and Synchronization
`dl_count` tracks how many local dentries share the lock. `dl_parent_blkno` is part of the cluster lock identity. `dentry_attach_lock` serializes attaching and detaching these structures from dentries.

## Cross-File Interactions
`dcache.c` implements these declarations. Directory lookup and namei paths call into them after resolving or creating dentries. Lock helpers in `dlmglue.c` initialize, acquire, downconvert, and free the embedded `ocfs2_lock_res`.

## Risks
Callers must distinguish negative-dentry generation data from positive-dentry lock pointers in `d_fsdata`. They must also hold the directory locking required by `ocfs2_dentry_attach_lock()` so parent-block based lock naming remains valid while names are being resolved or moved.
