# File Research: sources/os/linux/linux/fs/gfs2/main.c

Implements GFS2 module initialization and teardown. It creates global caches, workqueues, shrinkers, mempools, debugfs/sysfs support, and registers the `gfs2` and `gfs2meta` filesystem types.

Important behavior:
- Initializes global qstrs for `.` and `..`, quota hash buckets, sysfs support, quota-data LRU, and glock subsystem.
- Creates slab caches for glocks, glock address spaces, inodes, bufdata, resource groups, quota data, qadata, and transactions.
- Initializes object constructors for inodes and glocks so embedded lists, locks, holders, resource reservations, and address spaces start in valid states.
- Registers the quota-data shrinker and allocates `gfs2_recovery_wq`, `gfs2_control_wq`, and `gfs2_freeze_wq`.
- Creates the page mempool used by log descriptor/header I/O.
- Registers debugfs, then `gfs2_fs_type` and `gfs2meta_fs_type`.
- Teardown reverses registration, destroys workqueues/LRU/mempool/caches, runs `rcu_barrier()`, and uninitializes sysfs.

The file owns process-wide resource lifetime. Risk areas are failure-label ordering in init and ensuring RCU-deferred quota data is drained before caches are destroyed.
