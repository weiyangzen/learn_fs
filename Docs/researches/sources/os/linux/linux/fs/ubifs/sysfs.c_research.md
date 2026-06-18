# File Research: sources/os/linux/linux/fs/ubifs/sysfs.c

Read completely: 156 lines.

This file implements UBIFS sysfs registration and per-mount read-only error counters under the global `fs/ubifs` kset.

Main entry points: `ubifs_sysfs_register`, `ubifs_sysfs_unregister`, `ubifs_sysfs_init`, and `ubifs_sysfs_exit`.

Exposed attributes: `errors_magic`, `errors_node`, and `errors_crc`, each read-only. `ubifs_attr_show` maps them to `sbi->stats->magic_errors`, `node_errors`, and `crc_errors`.

Per-mount registration: `ubifs_sysfs_register` allocates `struct ubifs_stats_info`, formats the mount object name from UBI device and volume IDs, attaches the kobject to `ubifs_kset`, initializes the unregister completion, and calls `kobject_init_and_add`.

Teardown: `ubifs_sysfs_unregister` deletes and puts the per-mount kobject, waits for its release callback to complete, and frees the stats structure. The release callback completes `c->kobj_unregister`.

Global lifecycle: `ubifs_sysfs_init` names and registers the `ubifs` kset under `fs_kobj`; `ubifs_sysfs_exit` unregisters it.

Important interactions: `super.c` initializes global sysfs during module init and registers each mount early in `mount_ubifs`; `io.c` node validation increments these counters when stats are allocated.

Reliability notes: name length is checked against `UBIFS_DFS_DIR_LEN`. Registration failure paths call `kobject_put`, wait for completion where appropriate, free stats, and log the failed `ubifs<ubi>_<vol>` object.
