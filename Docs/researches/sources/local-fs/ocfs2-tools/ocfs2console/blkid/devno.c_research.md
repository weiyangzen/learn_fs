# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/devno.c

Resolves block device numbers to device paths and provides string duplication helpers.

Key functions:
- `blkid_strndup`, `blkid_strdup`
  - Local allocation helpers used throughout bundled blkid.
- `blkid_devno_to_devname(dev_t devno)`
  - Searches `/devices`, `/devfs`, and `/dev`.
  - Performs breadth-first directory traversal.
  - Returns allocated path for first block device matching `st_rdev`.
- Internal helpers:
  - `add_to_dirlist`
  - `free_dirlist`
  - `scan_dir`

Dependencies:
- `stat`, `opendir`, `readdir`
- `makedev` availability via system headers

Notable details:
- Search avoids `.` and `..`, queues subdirectories, and stops on first match.
- Uses fixed 1024-byte path buffer while scanning.
- `blkid_devdirs` is exported for use by `devname.c`.
