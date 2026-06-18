# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/puffs_priv.h

This private libpuffs header defines internal synchronization, mount state, frame IO, and call-context structures. It includes the puffs message interface, pthreads, public puffs definitions, and ucontext support.

`PU_LOCK` and `PU_UNLOCK` wrap the global `pu_lock`. `PU_CMAP` maps a cookie to a `puffs_node` either through the mount's cookie map callback or by direct cast. `struct puffs_framectrl` groups read, write, compare, got-frame, and fd-notify callbacks for a frame stream. `struct puffs_fctrl_io` stores per-fd frame IO state, send/rescue/event queues, current input frame, read/write wait counts, and list linkage. `FIO_EN_WRITE` and `FIO_RM_WRITE` decide when kqueue write interest should be enabled or disabled.

`struct puffs_usermount` is the private mount instance: operations table, puffs fd, max request length, flags, coroutine stack settings, main context, kqueue state, daemon pipe, root pnode, pnode list, call-context lists, path/name/cookie/error callbacks, pre/post hooks, frame controllers, IO lists, event array, loop callback and timeout, pending kernel args, next request id, and private data. State macros preserve low state bits while setting auxiliary flags.

`struct puffs_cc` represents a call context using either real `ucontext_t` state or a fake function/argument pair, plus caller pid/lwp id and scheduling linkage. `struct puffs_newinfo` stores pointers into reply message fields. The bottom of the file declares internal frame, main-loop, call-context, and FS-frame functions.
