# File Research: sources/os/linux/linux/fs/orangefs/devorangefs-req.c

Implements the `/dev/pvfs2-req` character device used as the OrangeFS kernel/userspace RPC bridge.

Key behavior:
- Only one userspace client-core may open the device; opens must be `O_NONBLOCK` and from `init_user_ns`.
- `orangefs_devreq_read()` selects queued kernel operations from `orangefs_request_list`, skips operations for filesystems pending remount, copies protocol/version/tag/upcall to userspace, marks the op in-progress, and inserts it into the in-progress hash table.
- `orangefs_devreq_write_iter()` accepts daemon downcalls, validates protocol version/magic/tag, removes the matching in-progress op, copies the downcall and optional readdir trailer, then marks the op serviced or handles cancellation/give-up state.
- `orangefs_devreq_release()` finalizes bufmap state, marks mounted filesystems pending, purges waiting and in-progress operations, runs down shared buffers, and clears userspace version/open state.
- Ioctls expose protocol magic and max up/down sizes, initialize the shared buffer map, trigger remount-all, report upstream module status, and update debugfs client/kernel debug state.
- Compat ioctl translates 32-bit `ORANGEFS_DEV_MAP`.

Important dependencies:
- Coordinates with global request lists, operation state machine, bufmap, superblock list, debugfs, and waitqueue purge logic.
- Device polling reports `EPOLLIN` when kernel upcalls are queued.
