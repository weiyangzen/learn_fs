# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/puffs_subr.c

This file contains small shared PUFFS helpers used by VFS, vnode, and message layers. When `PUFFSDEBUG` is enabled it defines the global `puffsdebug` consumed by `DPRINTF` macros in `puffs_sys.h`.

`puffs_makecn()` converts a kernel `componentname` into a protocol `puffs_kcn`, optionally copying a full pathname buffer when `PUFFS_KFLAG_LOOKUP_FULLPNBUF` is active. It stores namei operation, flags, NUL-terminated name, name length, resets `pkcn_consume`, and converts credentials with `puffs_credcvt()`. `puffs_credcvt()` maps `NOCRED`/`FSCRED` to internal credential tags and otherwise converts kauth credentials to `uucred`.

The async completion helpers pair with `puffs_msg_setcall()` in `puffs_vnops.c` and `puffs_msgif.c`. `puffs_parkdone_asyncbioread()` validates reply errors and residuals, copies returned read data into the buffer, and calls `biodone()`. `puffs_parkdone_asyncbiowrite()` validates write residuals and completes the buffer. `puffs_parkdone_poll()` records returned poll events in the node, calls `selnotify()`, and releases the node reference retained for async polling.

Mount reference helpers `puffs_mp_reference()` and `puffs_mp_release()` protect `struct puffs_mount` while message code crosses locks and userland; release broadcasts when the count reaches zero. `puffs_gop_size()` and `puffs_gop_markupdate()` are genfs hooks for size and timestamp update propagation. `puffs_senderr()` builds a fire-and-forget `PUFFSOP_ERROR` message to notify userland about invalid server behavior detected by the kernel.
