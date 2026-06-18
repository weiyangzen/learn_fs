# File Research: sources/os/bsd/dragonflybsd/sys/kern/sys_socket.c

## Summary
Provides the `fileops` implementation for sockets. It adapts generic descriptor operations to socket protocol operations for read, write, ioctl, stat, close, shutdown, and kqueue.

## Main Responsibilities
- Defines global `socketops`.
- Implements `soo_read()` using `so_pru_soreceive()`.
- Implements `soo_write()` using `so_pru_sosend()` and `SIGPIPE` handling.
- Implements socket ioctls for nonblocking, async, readable byte count, owner process/group, at-mark checks, interface ioctls, routing ioctls, and protocol control.
- Implements `soo_stat()` with `S_IFSOCK`, read/write permission bits based on socket state, receive-buffer size, credential owner, inode, and protocol sense data.
- Implements `soo_close()` and `soo_shutdown()`.

## Important Behavior
Read and write choose blocking behavior from explicit file-operation flags first, then from `fp->f_flag & FNONBLOCK`. `soo_write()` sends `SIGPIPE` on `EPIPE` unless `MSG_NOSIGNAL`, `SO_NOSIGPIPE`, or lack of LWP suppresses it.

`FIONBIO` is handled as a no-op at this layer because the generic ioctl path updates `fp->f_flag`. `FIOASYNC` updates both socket state and receive/send sockbuf async flags. Interface and routing ioctls are dispatched to `ifioctl()` and `rtioctl()` by ioctl group.

## Dependencies and Integration
This file is the bridge from the descriptor/file layer to socket protocol operations, routing, interface control, signal ownership, and kqueue socket filters.

## Risks
Close swaps `fp->f_ops` to `badfileops` before calling `soclose()` and then clears `f_data`, so any stale user of the file object must tolerate revoked operations. Ioctl routing by command group assumes protocol, interface, and route command namespaces remain compatible.
