# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null.h

This header defines nullfs mount arguments and mount-private state. `struct null_args` contains the target path and export arguments. `struct null_mount` stores the nullfs mount pointer, held root vnode reference, and export state.

It also defines `MOUNTTONULLMOUNT()`, optional `NULLFSDEBUG()`, and the `nullfs_export()` prototype.

Research notes: nullfs private state is intentionally small because DragonFly’s implementation relies heavily on namecache forwarding instead of private overlay vnodes.
