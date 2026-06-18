# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_comm.c

This file implements kernel-side communication between `/dev` filesystem code and user-level `devfsadmd`/`devfsadm` services. It handles door setup, daemon startup requests, wait coordination, and registration of the daemon’s door pathname.

Key routines:
- `sdev_devfsadm_lockinit()` and `sdev_devfsadm_lockdestroy()` initialize global synchronization.
- `sdev_wait4lookup()` waits for lookup or readdir completion, either while devfsadm is running or while an in-kernel callback/plugin lookup is active.
- `sdev_unblock_others()` clears lookup/read flags and broadcasts waiters.
- `sdev_start_devfsadmd()` emits a sysevent requesting daemon startup.
- `sdev_open_upcall_door()` waits for the daemon to register a door filename and opens it with `door_ki_open()`.
- `sdev_ki_call_devfsadmd()` performs the kernel door upcall, with retry behavior for `EINTR`, `EAGAIN`, and limited rebinding on `EBADF`.
- `sdev_devfsadm_revoked()` detects shutdown or revoked door handles.
- `sdev_devfsadmd_thread()` launches asynchronous full device configuration.
- `devname_filename_register()` is called from user/kernel control plumbing to install the door filename and wake waiters.

The global `devfsadm_state` bitset coordinates “running”, “has run”, and stop/run outcomes. Per-node lookup locks coordinate callers blocked on specific `sdev_node` creation.

Primary integration points are sysevents, kernel doors, `/dev` lookup state macros, and the task/thread path used by `sdev_subr.c`.

Risks include timeout behavior during daemon startup, stale/revoked door state, and ensuring every blocked lookup path eventually clears flags and broadcasts waiters.
