# File Research: sources/os/linux/linux/fs/ocfs2/cluster/sys.c

O2CB sysfs interface setup.

Behavior:
- Creates kset `o2cb` under `fs_kobj`.
- Adds attribute group containing `interface_revision`, which reports `O2NM_API_VERSION`.
- Initializes masklog sysfs under the O2CB kset with `mlog_sys_init()`.

Lifecycle:
- `o2cb_sys_init()` creates kset, sysfs group, and logmask interface; rolls back on failure.
- `o2cb_sys_shutdown()` shuts down masklog sysfs and unregisters the kset.

Dependency:
- Uses `ocfs2_nodemanager.h` for API version and `masklog.h` for logging sysfs.
