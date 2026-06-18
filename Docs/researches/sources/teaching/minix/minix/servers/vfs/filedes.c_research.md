# File Research: sources/teaching/minix/minix/servers/vfs/filedes.c

This file manages file descriptors and filp entries.

Key functions:
- `init_filps`: initializes filp mutexes.
- `check_fds`: checks if a process has enough free FD slots.
- `get_fd`: finds a free FD and optionally a free filp slot.
- `get_filp` / `get_filp2`: validates descriptor and optionally locks filp/vnode.
- `find_filp`: finds an open filp for a vnode and access mode.
- `find_filp_by_sock_dev`: finds socket filp by socket device.
- `invalidate_filp` and invalidation-by-major/socket-driver/endpoint helpers.
- `lock_filp`, `unlock_filp`, `unlock_filps`: combined filp/vnode locking helpers.
- `close_filp`: closes a filp, device, socket, or pipe and releases vnode references.
- `do_copyfd`: privileged cross-process descriptor copy/close service.

Important behavior:
- `get_fd` reserves neither FD nor filp permanently; callers claim after success.
- Filp locking also locks the vnode, upgrading FIFO read locks to write locks because pipe reads mutate state.
- Soft locks avoid relocking a vnode already locked by the same thread.
- Closed/invalidate filps only allow close operations.
- Last close on block devices flushes root-FS cache for non-root unmounted specials and closes the block driver.
- Character devices and sockets use their respective close paths.
- FIFO close releases blocked readers/writers and stores final pipe size on last close.
- `do_copyfd` supports driver back-calls such as UDS/VND descriptor passing and includes explicit deadlock/DoS protection for UDS passing its own sockets.

Notable security/control behavior:
- `do_copyfd` is currently superuser-gated, with comments noting it should become ACL-based.
- Copying a filp involved in a block-device ioctl by the target process is rejected to avoid deadlock.
