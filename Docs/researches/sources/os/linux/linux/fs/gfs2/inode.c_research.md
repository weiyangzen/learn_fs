# File Research: sources/os/linux/linux/fs/gfs2/inode.c

## Scope

Implements GFS2 inode lookup, creation, linking, unlink/rmdir, symlink/mkdir/mknod, atomic open, rename/exchange, permission checks, getattr/setattr, fiemap, seek-data/hole, symlink reads, inode operation tables, and inode setup/deallocation helpers.

## Public And Internal APIs Covered

- Exported helpers: `gfs2_setup_inode()`, `gfs2_inode_lookup()`, `gfs2_lookup_by_inum()`, `gfs2_lookup_meta()`, `gfs2_lookupi()`, `gfs2_permission()`, `gfs2_dinode_dealloc()`, `gfs2_seek_data()`, `gfs2_seek_hole()`.
- VFS inode operations: create, lookup, link, unlink/rmdir, symlink, mkdir, mknod, rename, permission, setattr, getattr, listxattr, fiemap, ACL operations, update_time, atomic_open, fileattr get/set.
- Creation internals: `create_ok()`, `alloc_dinode()`, `init_dinode()`, `gfs2_init_dir()`, `gfs2_init_xattr()`, `link_dinode()`, `gfs2_create_inode()`.
- Rename internals: `gfs2_rename()`, `gfs2_exchange()`, `gfs2_rename2()`, `gfs2_ok_to_move()`, `update_moved_ino()`.

## Control Flow And Behavior

- `gfs2_inode_lookup()` uses `iget5_locked()`, creates inode and iopen glocks for new inodes, optionally checks block type/generation, marks instantiate needed, attaches glock objects, sets inode/file ops, and handles stale generation mismatches.
- `gfs2_lookupi()` takes the directory glock shared unless already held, checks execute permission unless root/internal lookup, and searches the GFS2 directory.
- `gfs2_create_inode()` serializes on the parent directory glock exclusive, handles existing dentries for atomic open, reserves directory space, creates ACL/security xattrs, allocates dinode blocks, creates inode and iopen glocks, initializes the dinode, links it into the directory, and unwinds with deallocation on failure.
- Link/unlink paths take parent/child glocks, validate permissions, immutable/append/sticky-bit state, directory emptiness, quota/rgrp reservations, and update directory entries and link counts in transactions.
- Rename uses the global rename glock for cross-directory moves, asynchronously acquires involved inode glocks in deadlock-safe order, validates both old and new directory entries, reserves target directory space when needed, optionally unlinks the overwritten target, updates `..` for moved directories, and commits directory entry changes in one transaction.
- `RENAME_EXCHANGE` swaps two existing entries and adjusts parent link counts when directory/non-directory types cross parents.
- `gfs2_permission()` supports RCU/nonblocking permission checks by returning `-ECHILD` when it cannot take a glock.
- `gfs2_setattr()` takes the inode glock exclusive, handles size changes through truncate helpers, handles chown with quota transfer accounting, and updates ACLs on chmod.
- `gfs2_fiemap()`, `gfs2_seek_data()`, and `gfs2_seek_hole()` hold inode locks plus shared glocks and use iomap helpers; fiemap retries after faulting user extent memory.

## State And Invariants

- New inodes keep inode glock and iopen glock object pointers synchronized with `glock_set_object()` / `glock_clear_object()`.
- `i_no_addr`, `i_no_formal_ino`, and `gl_no_formal_ino` coordinate stale inode and remote delete detection.
- Directory operations assume parent/child/rgrp glocks are held before mutating directory entries, link counts, or unlink state.
- Creation failure before dentry instantiation must explicitly deallocate dinode/eattr state; after instantiation, eviction owns cleanup.
- Cross-directory rename must prevent moving a directory below itself by walking `..` under the rename glock.
