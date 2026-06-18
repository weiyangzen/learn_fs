# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/fstab.c

Implements mount table reading, lookup, locking, and update logic for `mount.ocfs2`, based on classic util-linux mount code with OCFS2 modifications.

Key responsibilities:
- Detects whether `/etc/mtab` exists, is a symlink, or is writable.
- Reads `/etc/mtab`, falling back to `/proc/mounts`.
- Stores mount entries in a doubly linked `mntentchn` list.
- Finds mount entries by device, directory, or `loop=` option.
- Checks whether a name appears exactly once in the mount table.
- Locks `/etc/mtab` safely using link-based lock creation plus `fcntl()`.
- Updates `/etc/mtab` by rewriting through a temporary file and renaming.

Important functions:
- `mtab_does_not_exist()`, `mtab_is_a_symlink()`, `mtab_is_writable()`.
- `mtab_head()`, `read_mounttable()`, `read_mntentchn()`.
- `getmntfile()`, `getmntdirbackward()`, `getmntdevbackward()`, `getmntoptfile()`.
- `is_mounted_once()`.
- `lock_mtab()`, `unlock_mtab()`, `update_mtab()`.

Disabled code:
- fstab reading and lookup functions are compiled out with `#if 0 /* OCFS2 modification */`.
- LABEL/UUID fstab resolution helpers are also disabled.

Dependencies:
- Local mount helper infrastructure: `mntent.h`, `sundries.h`, `xmalloc.h`, `paths.h`, `nls.h`.
- Mount path constants such as `MOUNTED`, `MOUNTED_LOCK`, and `MOUNTED_TEMP`.

Research notes:
- If `/etc/mtab` is missing or a symlink, `update_mtab()` returns without writing.
- Lock handling installs signal handlers to ensure lock cleanup.
- `update_mtab()` supports unmount removal, remount option update, and insertion of absent entries.
