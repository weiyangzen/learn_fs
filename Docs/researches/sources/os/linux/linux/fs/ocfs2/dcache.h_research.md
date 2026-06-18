# File Research: sources/os/linux/linux/fs/ocfs2/dcache.h

## Purpose
Declares OCFS2 dcache operations and dentry lock structures.

## Main Structure
`struct ocfs2_dentry_lock` contains:
- reference count `dl_count`
- parent directory block number
- held inode reference
- embedded OCFS2 lock resource.

The inode reference is kept until the lock resource is destroyed.

## Public Declarations
- `ocfs2_dentry_ops`: dentry operation table.
- `ocfs2_dentry_attach_lock()`: attach positive dentry to cluster dentry lock.
- `ocfs2_dentry_lock_put()`: decrement/free dentry lock.
- `ocfs2_find_local_alias()`: find alias in same parent.
- `ocfs2_dentry_move()`: rename-aware dentry move.
- `ocfs2_dentry_attach_gen()`: attach parent generation to negative dentry.
- `dentry_attach_lock`: global spinlock protecting lock attach/detach accounting.
