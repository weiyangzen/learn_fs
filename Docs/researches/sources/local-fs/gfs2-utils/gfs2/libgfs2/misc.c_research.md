# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/misc.c

This file contains filesystem constant calculation and mount/device opening helpers.

Public APIs:
- `lgfs2_compute_heightsize()`
- `lgfs2_compute_constants()`
- `lgfs2_open_mnt()`
- `lgfs2_open_mnt_dev()`
- `lgfs2_open_mnt_dir()`

Behavior:
- Computes max file/journal tree heights and size coverage per metadata height.
- Initializes common superblock-derived constants such as pointer counts, hash sizes, journal block size, and bitmap block coverage.
- Scans `/proc/mounts` for mounted GFS2 filesystems.
- Matches a user path against mount dir, device name, same block device, or same file identity.
- Returns open fds for mount directory and backing device as requested.

Risk notes:
- `lgfs2_open_mnt()` returns success with `*mnt == NULL` when path is not a mounted GFS2 filesystem and closes `dirfd`; callers must distinguish this.
- If `open(path)` succeeds but `setmntent()` later paths fail, fd cleanup is caller-sensitive.
- `fdcmp()` treats block-device identity through `st_rdev` and regular identity through `st_dev/st_ino`.
