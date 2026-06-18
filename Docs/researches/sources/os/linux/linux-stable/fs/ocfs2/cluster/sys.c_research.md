# File Research: sources/os/linux/linux-stable/fs/ocfs2/cluster/sys.c

## Summary
Implements the O2CB sysfs root under `fs_kobj`, exposing the nodemanager interface revision and installing the logmask sysfs tree.

## Main Responsibilities
- Create `/sys/fs/o2cb`.
- Expose `interface_revision` from `O2NM_API_VERSION`.
- Create the default O2CB attribute group.
- Initialize and shut down masklog sysfs support.
- Unregister the O2CB kset on shutdown or init failure.

## Key Interfaces
- `o2cb_sys_init()` creates sysfs state and calls `mlog_sys_init()`.
- `o2cb_sys_shutdown()` shuts down masklog and unregisters the kset.

## Risks
Init error handling unregisters the kset but does not separately remove a partially created attribute group. Shutdown ordering matters because masklog is parented under the O2CB kset.
