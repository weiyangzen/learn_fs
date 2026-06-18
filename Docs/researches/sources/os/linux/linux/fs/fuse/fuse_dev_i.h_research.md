# File Research: sources/os/linux/linux/fs/fuse/fuse_dev_i.h

Purpose: Internal header for `/dev/fuse` request/copy plumbing and processing queue lookup helpers.

Key responsibilities:
- Defines request-id bit layout: ordinary requests use even IDs and interrupts use `FUSE_INT_REQ_BIT`.
- Declares `struct fuse_copy_state`, which tracks copying request data between kernel request buffers, user iovecs, pipe buffers, pages, and io_uring-specific state.
- Defines `FUSE_DEV_FC_DISCONNECTED` sentinel used after `/dev/fuse` release.
- Provides helpers to retrieve `struct fuse_dev` and safely load `fud->fc` with acquire ordering.
- Declares processing queue helpers: hash lookup, request find, request end, pending request removal, timeout checks.
- Declares copy helpers for args in/out and queueing FORGET/INTERRUPT messages to the device queue.

Important data/control flow:
- `fuse_dev_fc_get()` pairs with connection install/release atomic updates and is central to safe lockless device-to-connection access.
- `__fuse_get_dev()` returns NULL if the device is not attached to a connection.
- Copy state tracks whether data is moving to or from userspace, whether folios can be moved, and whether the path is io_uring-backed.

External dependencies:
- Struct definitions from `fuse_i.h` and device implementation files.
- Linux pipe, iov_iter, page, and waitqueue APIs.

Notable edge cases:
- `fud->fc` may be NULL, a valid connection, or the disconnected sentinel.
- Most readers can dereference `fud->fc` safely after acquire load, but release/install paths require special handling.
