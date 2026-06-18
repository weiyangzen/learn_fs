# File Research: sources/os/linux/linux/fs/ocfs2/cluster/sys.h

Small header declaring O2CB sysfs lifecycle hooks.

Declares:
- `o2cb_sys_shutdown()`.
- `o2cb_sys_init()`.

Used by:
- `nodemanager.c` during module init/exit.
