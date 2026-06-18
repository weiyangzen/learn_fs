# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/metafs.c

Utility code for temporarily mounting the `gfs2meta` filesystem and taking an administrative flock on it.

Key functions:
- `mount_gfs2_meta`: creates `/tmp/.gfs2meta.XXXXXX`, installs signal handlers, mounts `gfs2meta`, and locks the mount directory.
- `cleanup_metafs`: fsyncs/closes the lock fd, unmounts the temporary mount, removes the temp directory, resets signals, and frees path/context memory.
- `copy_context_opt`: extracts a duplicate of the `context=` mount option from an `mntent`.

Internal helpers:
- `lock_for_admin`: opens the metafs path with `O_RDONLY | O_NOFOLLOW` and takes `LOCK_EX`.
- `setsigs` and `sighandler`: mark `metafs_interrupted` on several signals.

Dependencies include mount/umount syscalls, flock, mntent parsing, gettext, and POSIX signal handling.

Research notes:
- The global `metafs_interrupted` lets callers notice asynchronous interruption while admin operations are active.
- Cleanup only proceeds when `mfs->fd > 0`, so fd `0` would be treated as not mounted/locked.
