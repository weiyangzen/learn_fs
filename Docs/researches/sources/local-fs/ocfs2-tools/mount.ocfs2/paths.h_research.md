# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/paths.h

Path constants for mount table handling.

It defines `_PATH_FSTAB` as `/etc/fstab`, derives mtab lock/temp paths from `_PATH_MOUNTED` when available, falls back to `/etc/mtab~` and `/etc/mtab.tmp`, and sets `LOCK_TIMEOUT` to 10 seconds.
