# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_debug.c

Implements a small global in-kernel ZFS debug message buffer. Messages are stored in `zfs_dbgmsgs`, protected by `zfs_dbgmsgs_lock`, with a byte-size limit controlled by `zfs_dbgmsg_maxsize` defaulting to 4 MiB.

`zfs_dbgmsg_init()` creates the list and initializes the mutex. `zfs_dbgmsg_fini()` drains all stored messages, frees their variable-sized allocations, destroys the mutex, and asserts that accounting returned to zero.

`zfs_dbgmsg()` formats a printf-style message into a variable-sized `zfs_dbgmsg_t`, records wall-clock and high-resolution timestamps, emits a DTrace probe, appends the record to the list, and trims oldest records until `zfs_dbgmsg_size` is below the configured limit.

`zfs_dbgmsg_print()` prints all currently buffered messages under the lock with a caller-supplied tag. The comments document inspection through MDB `::zfs_dbgmsg` and DTrace probes.

The design is intentionally lossy under pressure: newest messages are kept and oldest messages are freed once the byte cap is exceeded.
