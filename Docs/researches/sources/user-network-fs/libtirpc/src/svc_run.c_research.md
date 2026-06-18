<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_run.c -->
# sources/user-network-fs/libtirpc/src/svc_run.c

Purpose: default RPC server event loop built on `poll()`, plus an exit helper.

Important APIs and functions: `svc_run()` loops forever while service poll descriptors exist and dispatches readiness through `svc_getreq_poll()`. `svc_exit()` frees global poll state to make `svc_run()` leave its loop.

Control flow: `svc_run()` snapshots `svc_max_pollfd`, resizes a private pollfd array when the global size changes, copies global `svc_pollfd` entries, blocks in `poll(..., -1)`, ignores `EINTR`, warns and exits on other poll failures, and dispatches ready fds. If no poll descriptors exist, it breaks. `svc_exit()` takes `svc_fd_lock`, frees `svc_pollfd`, nulls it, and zeroes `svc_max_pollfd`.

State and persistence: reads global `svc_pollfd`/`svc_max_pollfd`; `svc_exit()` mutates and frees them. The local poll array is allocated and freed inside `svc_run()`.

Dependencies and integration points: used by applications that rely on the classic blocking server loop after registering transports in `svc.c`. Dispatches into `svc_getreq_poll()`.

Risks: `svc_run()` snapshots globals without holding `svc_fd_lock` while copying, so concurrent registration/unregistration can race with the copy. `svc_exit()` is coarse: it removes the global poll array rather than marking a loop-specific stop flag.

Test signals: loop dispatch with one and multiple transports, EINTR continuation, poll failure warning, descriptor array growth/shrink, `svc_exit()` causing loop termination from another thread, and no-transport immediate return.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_run.c -->
