# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_run.c

Read completely: 214 lines.

Implements the server event loop and exit hook. `svc_run()` chooses between a `select()` loop and a `poll()` loop based on `__svc_flags & SVC_FDSET_POLL`.

Both loops copy the current service fd state under `svc_fd_lock`, wait up to 30 seconds, dispatch ready fds via `svc_getreqset2()` or `svc_getreq_poll()`, and call `__svc_clean_idle(NULL, 30, FALSE)` on timeout. They tolerate repeated `EINTR` and limited `EBADF` retries outside rump builds.

`svc_exit()` causes the loop to drain by clearing the service fdset under write lock. The loops then fail to get work and return through their cleanup paths.
