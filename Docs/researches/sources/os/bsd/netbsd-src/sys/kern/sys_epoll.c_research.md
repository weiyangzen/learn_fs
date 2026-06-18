# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_epoll.c

Read completely: 682 lines.

This file implements Linux-style `epoll` APIs on top of NetBSD `kqueue`/`kevent`. An epoll fd is a kqueue fd, and epoll event masks are translated into read/write kevents with epoll metadata stored in `kevent.ext[]`.

Core translation:
- `sys_epoll_create1` validates `EPOLL_CLOEXEC` and calls `sys_kqueue1`.
- `epoll_to_kevent` maps epoll flags to up to two kevents (`EVFILT_READ`, `EVFILT_WRITE`), supporting edge-triggered `EV_CLEAR`, one-shot `EV_DISPATCH`, EOF/error flags, and a disabled read event for zero masks.
- `kevent_to_epoll` converts returned kevents back to `epoll_event`, carrying user data from `kext_data`.
- Callback shims let `kevent1` copy converted kernel buffers rather than copyin/copyout raw user kevents.

Control/wait paths:
- `epoll_ctl_common` validates epfd as kqueue, validates target fd, rejects regular vnode-like targets with Linux-compatible `EPERM`, disallows adding an epoll fd to itself, handles ADD/MOD/DEL, checks duplicate registration, and invokes `kevent1`.
- `sys_epoll_ctl` copies in events for non-DEL operations.
- `epoll_wait_common` validates epfd/maxevents, optionally swaps signal masks, calls `kevent1`, and restores the old mask.
- `sys_epoll_pwait2` copies timeout/sigmask, allocates a temporary event buffer, waits, and copies out returned events.

Loop/depth prevention:
- `epoll_recover_watch_tree` walks current process fds, finds kqueues watching other kqueues, and reconstructs directed edges from stored `kext_epfd`/`kext_fd`.
- `epoll_dfs` detects loops and enforces `EPOLL_MAX_DEPTH`.
- `epoll_check_loop_and_depth` adds the proposed edge and runs DFS when the target fd is another kqueue.

Integration: this depends on kqueue internals (`knote`, `kq_sel.sel_klist`) as well as file descriptor lookup and vnode type checks. It tries to match Linux errno behavior by validating fds before delegating to kevent.

Reliability notes: only read/write readiness is substantially translated; comments note missing/partial handling for `EPOLLPRI` and `EPOLLHUP`. The watch-tree recovery inspects fd tables and knote lists without a dedicated epoll graph object, so correctness depends on the stored ext metadata and current process fd view.
