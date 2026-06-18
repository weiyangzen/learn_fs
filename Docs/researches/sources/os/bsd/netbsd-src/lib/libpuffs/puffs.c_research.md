# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/puffs.c

This is the central libpuffs mount, configuration, daemonization, and event-loop implementation. It exports standard puffs mount options, owns the global `pu_lock`, initializes `struct puffs_usermount`, fills the kernel vnode operation mask from configured callbacks, opens/mounts `/dev/puffs`, and drives request processing through kqueue and frame controllers.

`puffs_init` allocates the usermount and kernel arguments, sets `PUFFSVERSION`, kernel flags, operation mask, mount names, default statvfs/root info/message length/time32 flag, stores the operations table, initializes node and frame lists, installs FS frame callbacks, default path functions, default error notification, and sets state to `PUFFS_STATE_BEFOREMOUNT`. It frees the passed ops table after copying it.

Configuration helpers set blocking mode, stack size, root node and root info, private mount data, mount display names, max request length, file-handle size, cookie hash buckets, path callbacks, name modifiers, error notification, cookie mapping, main-loop callbacks, timeout, and pre/post operation hooks. `puffs_setback` sets selected kernel setback bits for operations where that is legal.

`puffs_mount` supports a special `PUFFS_COMFD` environment path for passing mount data over an existing descriptor; otherwise it canonicalizes the mountpoint, opens `_PATH_PUFFS`, fills `pa_fd`, and calls `mount(MOUNT_PUFFS, ...)`. It adds `MNT_NOSUID|MNT_NODEV` for non-root users and tears down deferred daemon notification state.

The main loop sets the puffs fd nonblocking, registers frame IO with kqueue, installs signal events requested by `puffs_unmountonsignal`, creates a call context, and enters `puffs__theloop`. The loop schedules pending contexts, calls an optional loop function, tries to flush queued writes before waiting, manages EVFILT_WRITE enable/disable, dispatches read/write/signal events to frame handlers, handles close/error notification, and frees deferred removed IO descriptors. `puffs_exit` sends an unmount frame and `finalpush` attempts to write all pending frames before returning.
