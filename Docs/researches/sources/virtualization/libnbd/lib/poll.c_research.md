# File Research: sources/virtualization/libnbd/lib/poll.c

Simple `poll(2)`-based event loop for users who do not integrate libnbd into their own loop.

Key functions:
- `do_poll`: builds pollfds for the NBD fd and optional extra fd, maps current state direction to POLLIN/POLLOUT, waits, and notifies read or write readiness.
- `nbd_unlocked_poll`: polls only the NBD connection.
- `nbd_unlocked_poll2`: also watches a caller-provided fd for readability.

Interactions:
- Uses `nbd_unlocked_aio_get_fd`, generated state direction, and `aio_notify_read/write`.

Research notes:
- The handle lock is intentionally not released during `poll`, to prevent another thread from closing fds being polled.
- If both read and write are ready, read notification is preferred because it services older server replies first.
