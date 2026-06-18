# File Research: sources/os/linux/linux-stable/fs/ubifs/sysfs.c

## Purpose
Adds UBIFS sysfs support under `/sys/fs/ubifs`, exposing per-mounted-volume read-only error counters.

## Key Behavior
- Defines read-only attributes: `errors_magic`, `errors_node`, and `errors_crc`.
- `ubifs_attr_show()` maps attributes to `sbi->stats` counters and emits decimal values.
- `ubifs_sysfs_register()` allocates `ubifs_stats_info`, formats the per-volume directory name, initializes the mount kobject, and adds it to sysfs.
- `ubifs_sysfs_unregister()` deletes and puts the kobject, waits for release completion, and frees stats.
- `ubifs_sysfs_init()` registers the top-level `ubifs` kset below `fs_kobj`.
- `ubifs_sysfs_exit()` unregisters the kset.

## Important Dependencies
- Called during mount/unmount from `super.c`.
- Relies on `struct ubifs_info` embedding a `kobject`, completion, UBI volume identifiers, and stats pointer.
- Counter updates are elsewhere in UBIFS I/O/validation code.

## Invariants and Risks
- Register failure calls `kobject_put()` and waits for the release callback before freeing stats.
- Directory name length is checked against `UBIFS_DFS_DIR_LEN`.
- Attributes are read-only; this file does not implement tuning or mutation interfaces.
