# File Research: sources/os/linux/linux/fs/fs_struct.c

## Purpose
This file manages `struct fs_struct`, the per-task or shared process filesystem context containing root, current working directory, umask, and reference count. It handles setting root/pwd, chroot reference rewrites, copy/unshare, exit, and init state.

## Main Definitions
- `set_fs_root()` replaces `fs->root` with a referenced new path and drops the old path afterward.
- `set_fs_pwd()` does the same for `fs->pwd`.
- `replace_path()` updates a path if it exactly matches an old path.
- `chroot_fs_refs()` walks all processes/threads and rewrites matching `root` and `pwd` references from `old_root` to `new_root`.
- `free_fs_struct()` drops root and pwd paths and frees from `fs_cachep`.
- `exit_fs()` detaches the task from its fs context and frees it when the user count reaches zero.
- `copy_fs_struct()` allocates a private copy of an existing fs context.
- `unshare_fs_struct()` installs a copied fs context for `current`.
- `init_fs` provides the boot/init task filesystem context with default umask `0022`.

## Control Flow And Behavior
Root and pwd updates take a reference on the new path first, update under the fs seqlock, then release the old path after dropping the lock. Copying allocates from `fs_cachep`, initializes a new seqlock and metadata, then snapshots root and pwd under the old fs seqlock.

`chroot_fs_refs()` traverses the full task list under `tasklist_lock`, locks each task, and replaces `root` and `pwd` references that still point to `old_root`. It increments `new_root` once per replacement and later drops `old_root` the same number of times.

## Dependencies And Interfaces
The file uses scheduler task traversal, task locks, seqlocks, path reference helpers, and the global `fs_cachep`. `unshare_fs_struct()` is exported GPL for other kernel code.

## Concurrency And Safety
`fs_struct` fields are protected by `fs->seq`; task ownership is protected by `task_lock()`. The code carefully avoids dropping path references while holding the seqlock because `path_put()` can block.

## Research Notes
This file is central to namespace-like behavior at the task level. Its most important lifetime rule is that path references are acquired before publishing and released after unpublishing, preserving stable root/pwd paths for concurrent readers.
