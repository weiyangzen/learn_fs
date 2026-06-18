# File Research: sources/os/linux/linux-stable/fs/orangefs/namei.c

## Scope

This file implements OrangeFS directory inode namespace operations: create, lookup, unlink/rmdir, symlink, mkdir, and rename.

## APIs Covered

- VFS methods: `orangefs_create()`, `orangefs_lookup()`, `orangefs_unlink()`, `orangefs_symlink()`, `orangefs_mkdir()`, `orangefs_rename()`.
- Exports `orangefs_dir_inode_operations`.

## Control Flow And Behavior

- Create/mkdir/symlink allocate an OrangeFS op, fill parent ref and default sys attributes, copy names/targets, service the op, then instantiate a new VFS inode from the returned object reference.
- Lookup always issues a server lookup, including create-intent paths, so existing objects are not bypassed incorrectly.
- Successful lookups set dentry timeout and use `orangefs_iget()`; `-ENOENT` creates a negative dentry.
- Unlink and rmdir share REMOVE, drop target link count on success, and update parent mtime/ctime.
- Symlink validates target length, creates symlink object, then fixes `i_size` locally because symlink size cannot later be refreshed by getattr.
- Mkdir keeps directory link counts effectively constant because cross-client directory nlink consistency is not available.
- Rename rejects all nonzero rename flags, updates new parent time, sends RENAME, and updates overwritten target ctime if present.

## Risks And Invariants

- Names are bounded by `ORANGEFS_NAME_MAX - 1`.
- Parent timestamps are explicitly updated with `__orangefs_setattr()`.
- New dentries receive OrangeFS dcache timeouts for later revalidation.
- No advanced rename flags are supported.
