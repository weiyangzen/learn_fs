# File Research: sources/teaching/minix/minix/servers/vfs/sdev.c

Implements the lower VFS socket layer: communication with socket drivers and completion of long-lived socket operations.

Key behavior:
- `sdev_sendrec` sends short-lived socket-driver requests asynchronously, then blocks the current worker thread until the reply arrives.
- `sdev_suspend` records socket request state, grants, request type, and auxiliary accept/recvmsg state in `fp_sdev`, then suspends the process on `_SDEV`.
- `sdev_socket` creates sockets or socket pairs through a socket driver and converts driver-local socket IDs to VFS `dev_t` values.
- `sdev_bind`, `sdev_connect`, `sdev_accept`, `sdev_readwrite`, and `sdev_ioctl` send long-lived requests and suspend the process.
- `sdev_listen`, `sdev_shutdown`, many get/set option calls, and non-suspending close use short-lived request/reply patterns.
- `sdev_close` may suspend only for user `close(2)` where SO_LINGER can block; other close paths wait synchronously with a nonblocking close parameter.
- `sdev_select` initiates socket-driver select polling without suspending the process.

Reply handling:
- `sdev_reply` receives driver replies, routes select replies to `select_sdev_reply1/2`, wakes blocked worker threads for short-lived calls, resumes suspended processes for long-lived calls, and spawns a worker for successful accept replies.
- `sdev_finish` revokes grants and completes suspended calls, either by `replycode` or by calling upper-layer resume functions.
- `sdev_finish_accept` creates the VFS device identifier for accepted sockets and calls `resume_accept`.
- `sdev_cancel` sends cancel requests for signal-interrupted socket calls and handles the original reply.
- `sdev_stop` aborts calls when a socket driver dies.

Important dependencies:
- Socket-driver registration and device decoding are provided by `smap.c`.
- Upper socket syscall state is completed through `socket.c` resume functions.
- Select integration uses `select_sdev_reply1/2`.

Notable implementation details:
- Accept success is special because creating the accepted socket fd may block, so it cannot be completed in the main VFS thread.
- Cancel replies can still represent success or partial success; cancellation is not treated as guaranteed failure.
