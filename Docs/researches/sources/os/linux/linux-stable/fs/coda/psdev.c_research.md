# File Research: sources/os/linux/linux-stable/fs/coda/psdev.c

This file implements the Coda pseudo-device character driver, module initialization/exit, and the bidirectional request/reply queues between kernel Coda VFS code and the Venus userspace cache manager.

Key responsibilities:
- Defines global `coda_comms[MAX_CODADEVS]`, `coda_hard`, and `coda_timeout`.
- Implements pseudo-device file operations: read, write, poll, ioctl, open, and release.
- Registers `/dev/cfsN` devices for Coda communication.
- Initializes and tears down Coda module state, including inode cache, char device, sysctl table, and filesystem registration.

Important control flow:
- `coda_psdev_open()` allows opens only from the initial PID and user namespaces, validates the minor, and initializes one `venus_comm` slot if unused.
- `coda_psdev_read()` waits for `vc_pending`, moves synchronous requests to `vc_processing`, and copies request data to Venus.
- `coda_psdev_write()` handles two paths:
  - Downcalls, identified by `DOWNCALL(hdr.opcode)`, are copied into a temporary buffer and passed to `coda_downcall()`.
  - Upcall replies are matched by `unique` in `vc_processing`, copied into the waiting request buffer, marked `CODA_REQ_WRITE`, and wake the sleeping requester.
- `CODA_OPEN_BY_FD` replies convert a Venus-provided fd into a kernel `struct file *` using `fget()`.
- `coda_psdev_release()` aborts all pending and processing synchronous requests and frees async requests.

Dependencies:
- `coda_downcall()` is implemented in `upcall.c`.
- Sysctl init/cleanup is implemented in `sysctl.c`.
- Filesystem type and inode cache setup are provided by `inode.c`.

Risks and invariants:
- Only one opener per pseudo-device slot is allowed.
- Request queues are protected by `vc_mutex`; readers also use `vc_waitq`.
- `coda_psdev_write()` returns `-ESRCH` if a Venus reply does not match an outstanding processing request.
- Release aborts waiters so kernel callers do not sleep forever when Venus exits.
