# File Research: sources/os/bsd/freebsd-src/sys/fs/devfs/devfs_devs.c

Read completely: 751 lines.

Purpose: manages global character-device registration and per-mount synthetic devfs dirent population.

Key global state:
- `cdevp_list` is the global active-device list protected by `dev_lock()/devmtx`.
- `devfs_inos` allocates devfs inode numbers.
- `devfs_generation` tracks device-list changes for mount population.
- `devfs_rule_depth` controls nested ruleset include depth.

Key functions:
- `sysctl_devname()` maps a device number to a registered device name.
- `devfs_alloc()` allocates and initializes `struct cdev_priv`/`struct cdev`.
- `devfs_free()` releases credentials, inode, dirent arrays, locks, and private storage.
- `devfs_dev_exists()` checks for path conflicts with active devices and referenced directories.
- `devfs_find()` looks up child dirents while ignoring inactive character devices.
- `devfs_newdirent()` allocates dirents with embedded `struct dirent`, timestamps, link count, and MAC labels.
- `devfs_vmkdir()` creates synthetic directories plus `.` and `..`, links into parents, and applies rules.
- `devfs_delete()` dooms a dirent, revokes associated vnode, frees symlink/MAC/inode state, and may prune empty parents.
- `devfs_cleanup()` and `devfs_purge()` remove all per-mount dirents on unmount.
- `devfs_populate()` walks `cdevp_list`, removes inactive entries, creates missing mount dirents, handles aliases as symlinks, applies rules, and updates mount generation.
- `devfs_create()` marks a cdev active, assigns inode, references it, inserts into global list, and bumps generation.
- `devfs_destroy()` clears active state and bumps generation.

Important behavior:
- Each `cdev_priv` owns an array of per-mount dirent pointers indexed by `dm_idx`; `devfs_metoo()` grows that array.
- Inactive devices are garbage-collected only when their `cdp_inuse` drops to zero.
- Device names containing slashes create intermediate devfs directories.

Research notes:
- This file is the core bridge from kernel cdev registration to visible `/dev` filesystem entries.
