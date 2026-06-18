# File Research: sources/os/linux/linux-stable/fs/gfs2/inode.c

## Scope

This file implements GFS2 inode lookup, setup, creation, linking, unlink/rmdir, symlink, mkdir/mknod, atomic open, rename/exchange, symlink following, permission checks, setattr/getattr, fiemap, seek-data/hole helpers, update-time handling, and inode operation tables.

## Public And Internal APIs Covered

- Exported helpers: `gfs2_setup_inode()`, `gfs2_inode_lookup()`, `gfs2_lookup_by_inum()`, `gfs2_lookup_meta()`, `gfs2_lookupi()`, `gfs2_dinode_dealloc()`, `gfs2_permission()`, `gfs2_seek_data()`, `gfs2_seek_hole()`.
- VFS operation tables: `gfs2_file_iops`, `gfs2_dir_iops`, and `gfs2_symlink_iops`.
- Creation helpers: `gfs2_create_inode()`, `alloc_dinode()`, `init_dinode()`, `gfs2_init_dir()`, `gfs2_init_xattr()`, `link_dinode()`.
- Namespace operations: `gfs2_create()`, `gfs2_lookup()`, `gfs2_link()`, `gfs2_unlink()`, `gfs2_symlink()`, `gfs2_mkdir()`, `gfs2_mknod()`, `gfs2_atomic_open()`, `gfs2_rename2()`.
- Attribute/data-map operations: `gfs2_setattr()`, `gfs2_getattr()`, `gfs2_fiemap()`, `gfs2_update_time()`.

## Control Flow And Behavior

- `gfs2_set_iop()` selects inode and file operation tables by inode mode and local-vs-DLM flock mode.
- `gfs2_setup_inode()` clears `__GFP_FS` from inode mapping allocations to avoid reclaim recursion into the filesystem.
- `gfs2_inode_lookup()` uses `iget5_locked()`, allocates inode and iopen glocks for new inodes, optionally verifies block type, checks deleted generations via the inode LVB, binds glock objects, instantiates disk state when type is unknown, takes an iopen shared holder, sets operation tables, and handles stale-generation failures.
- `gfs2_lookupi()` handles dot/root-dotdot special cases, avoids retaking a directory glock already held by the current task, checks execute permission unless root lookup, and delegates directory search.
- Create path obtains parent quota data, updates rindex, locks parent exclusive, validates permissions/link limits/name, handles existing files for atomic open, reserves directory-add space, allocates a VFS inode, applies ACL and suiddir/sgid uid/gid rules, inherits JDATA/SYSTEM/TOPDIR behavior, allocates dinode and optional xattr block, creates inode/iopen glocks, inserts the inode, initializes on-disk dinode, applies ACL/security xattrs, links the inode into the directory, instantiates dentry/file, and has a long cleanup path for partially created dinodes.
- Dinode deallocation checks the inode owns exactly one block, finds the rgrp, locks it node-scope exclusive, frees the dinode, releases final pages, and updates quota/statfs/rgrp transaction state.
- Hard link takes parent and child exclusive glocks, validates permissions, link counts, immutability/append-only state, reserves directory-add blocks, adds the directory entry, increments child nlink, and instantiates the dentry.
- Unlink/rmdir updates rindex, locks parent, child, and child rgrp, validates sticky-bit/append/immutable/permission and directory emptiness, removes the dirent, updates link count and ctime, and calls `gfs2_unlink_di()` when nlink reaches zero.
- Rename uses a global rename glock for cross-directory operations, rejects moving a directory into its own subtree, asynchronously acquires all participating inode glocks with retry on `-ESTALE`, optionally locks target rgrp for unlink flag updates, validates old and new entries, reserves new directory entry space, unlinks target if present, updates moved inode or dotdot, deletes old dirent, and adds new dirent.
- Exchange similarly locks participating directories/inodes, validates both entries, updates dotdot/ctime for both moved inodes, swaps directory entries, and adjusts parent nlinks when directories cross parents.
- `gfs2_rename2()` supports `RENAME_EXCHANGE`, treats `RENAME_NOREPLACE` as redundant, and rejects other flags.
- `gfs2_get_link()` reads stuffed symlink data from the dinode under a shared glock.
- `gfs2_permission()` can run from RCU mode; it returns `-ECHILD` when it would need to block. Otherwise it takes a shared/any glock unless already held and delegates to generic permission after immutable write rejection.
- `gfs2_setattr()` takes the inode glock exclusive, performs VFS setattr checks, routes size changes to truncate code, UID/GID changes through quota transfer, and mode/time/simple changes through transactions and ACL chmod.
- `gfs2_getattr()` takes a shared/any glock unless already held, maps append/immutable disk flags to STATX attributes, and calls `generic_fillattr()`.
- `gfs2_fiemap()` and seek-data/hole acquire shared inode glocks around iomap queries and pre-fault fiemap output buffers on `-EFAULT`.
- `gfs2_update_time()` upgrades an already-held non-exclusive glock to exclusive before generic timestamp update; NOWAIT returns `-EAGAIN`.

## State And Data Structures

- Inode creation and lookup manipulate `gfs2_inode` identity, glocks, iopen holder, quota data, rgrp reservations, disk flags, size/blocks, mode, ACL/security xattrs, directory entry counts, and allocation goals.
- Directory-add operations use `struct gfs2_diradd` and transaction reservations calculated by `gfs2_trans_da_blks()`.
- Multi-inode rename uses arrays of `gfs2_holder` with `GL_ASYNC` and the global `sd_rename_gl`.
- Quota-changing setattr uses old/new uid/gid pairs, `gfs2_alloc_parms`, quota locks, quota checks, and quota deltas over current inode block count.

## Dependencies

- VFS inode, dentry, namei, ACL, xattr, LSM, permission, setattr, fiemap, and iomap APIs.
- GFS2 glocks/glops, directory code, bmap/iomap, metadata I/O, quota, rgrp allocation, transactions, super/withdraw helpers, ACL/xattr code, and file operations from `file.c`.

## Risks And Invariants

- New inode creation is not a single transaction; comments note the crash window where an allocated block can look like a valid inode, and cleanup must zero link count/deallocate correctly on failure.
- Inode/iopen glock object binding must be undone on failure to avoid stale object pointers.
- Rename/exchange require strict multi-glock acquisition and retry discipline to avoid deadlocks and stale state.
- Directory moves must preserve dotdot and parent nlink invariants.
- Permission/getattr paths must avoid blocking in RCU mode.
- Quota transfer on chown must debit old IDs and credit new IDs under quota locks in the same transaction.
- Fiemap must not fault user memory while holding the glock; it retries after faulting the destination.
