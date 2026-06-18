# File Research: sources/os/bsd/openbsd-src/sbin/newfs/pathnames.h

Purpose: Defines path constants used by `newfs.c`.

Constants:
- `_PATH_SBIN`: `/sbin`, first lookup directory for filesystem-specific `newfs_<type>` tools.
- `_PATH_USRSBIN`: `/usr/sbin`, fallback lookup directory.
- `_PATH_MNT`: `/mnt`, fallback temporary mountpoint used by MFS prepopulation when `/tmp` is read-only.

Integration:
- Included by `newfs.c`.
- Complements `<paths.h>` constants such as `_PATH_DEV` and `_PATH_TMP`.
