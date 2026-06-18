# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_onexit.c

Implements per-`/dev/zfs` control-device cleanup callbacks. It lets kernel code associate cleanup state with a clone-opened ZFS control fd so state can survive across related ioctls and still be released automatically when the fd closes or the process exits.

Key elements:
- `zfs_onexit_init()` allocates a `zfs_onexit_t`, initializes its mutex, and creates the action list.
- `zfs_onexit_destroy()` removes every registered action, drops the lock while firing each callback, frees action nodes, and tears down the list/mutex.
- `zfs_onexit_fd_hold()` validates a user fd, obtains the underlying minor, confirms it is a ZFS control-device minor, and keeps the file table entry held until `zfs_onexit_fd_rele()`.
- `zfs_onexit_add_cb()` registers a callback/data pair on a control minor and returns an action handle, implemented as the action-node address cast to `uint64_t`.
- `zfs_onexit_del_cb()` removes a callback by action handle and optionally fires it before freeing the node.
- `zfs_onexit_cb_data()` returns the callback data associated with an action handle without removing it.

Main dependencies and interactions:
- Uses `zfsdev_get_soft_state()` from `zfs_ioctl.c` to validate that a minor is a `ZSST_CTLDEV` control device rather than a zvol minor.
- Used by receive and temporary snapshot/hold flows to store cleanup state tied to a caller-supplied cleanup fd.
- Relies on `/dev/zfs` clone opens with `O_EXCL`, which create unique control minors in `zfs_ctldev_init()`.

Implementation notes:
- Callers are expected to hold the fd before doing work so later callback registration or lookup cannot fail because the fd was closed concurrently.
- The callback list is protected by `zo_lock`; callbacks are invoked after removing the node and outside the lock to avoid callback-induced deadlocks.
- Action handles are kernel pointers exposed as opaque integers to userland, but each lookup scans the current minor's action list before accepting the handle.

Risk/attention points:
- Action handles are only meaningful for the owning control minor and must not be treated as portable or persistent identifiers.
- Consumers must balance `zfs_onexit_fd_hold()` with `zfs_onexit_fd_rele()` or they will leak file references.
- Callback functions must tolerate being fired during close/exit, explicit delete, or cleanup after abnormal caller termination.
