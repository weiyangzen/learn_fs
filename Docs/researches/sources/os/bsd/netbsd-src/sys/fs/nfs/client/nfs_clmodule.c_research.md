# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clmodule.c

This is a small NetBSD module wrapper for `nfs_client`.

Key behavior:
- Declares `MODULE(MODULE_CLASS_MISC, nfs_client, "nfs_common,sysmon_taskq")`.
- `nfs_client_modcmd()` accepts `MODULE_CMD_INIT` and `MODULE_CMD_FINI`, returning success for both.
- Unknown module commands return `ENOTTY`.

Dependencies:
- The module depends on `nfs_common` and `sysmon_taskq`.
- It does not initialize the detailed NFS client subsystem itself; that work is in other module/port setup code such as `nfs_clport.c`.

Research notes:
- This file is purely module metadata/control.
- It has no NFS protocol, vnode, cache, or I/O logic.
