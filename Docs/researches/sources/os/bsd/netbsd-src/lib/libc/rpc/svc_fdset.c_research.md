# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_fdset.c

Read completely: 494 lines.

Implements dynamic service fd-set and pollfd management. Internally `struct svc_fdset` tracks a resizable `fd_set`, current max fd, fd capacity, a resizable `pollfd` array, allocated poll capacity, and used poll slots. The global single-threaded instance can be replaced by per-thread instances when `svc_fdset_init(SVC_FDSET_MT)` is used.

Public helpers include `svc_fdset_init()`, `svc_fdset_zero()`, `svc_fdset_set()`, `svc_fdset_isset()`, `svc_fdset_clr()`, `svc_fdset_copy()`, `svc_fdset_get()`, `svc_fdset_getmax()`, `svc_fdset_getsize()`, `svc_pollfd_copy()`, `svc_pollfd_get()`, `svc_pollfd_getmax()`, and `svc_pollfd_getsize()`.

The fdset resizes in `FD_SETSIZE` chunks and can represent fds beyond the traditional fixed `FD_SETSIZE`. Poll arrays use `fd = -1` holes and shrink `fdused` when trailing slots become empty. Under `_LIBC`, `svc_fdset_sanitize()` updates legacy exported globals `svc_fdset` and `svc_maxfd`.

Reliability notes: per-thread initialization copies the global struct shallowly, so transition timing matters; callers protect access with `svc_fd_lock` in higher-level service code.
