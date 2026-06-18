# File Research: sources/os/bsd/netbsd-src/sys/kern/sys_select.c

Implements synchronous I/O multiplexing for `select`, `pselect`, `poll`, `pollts`, plus the shared `selinfo` wait/wakeup machinery used by file, socket, device, pipe, and timerfd objects.

Key syscall paths:
- `sys___pselect50`: copies optional `timespec` and signal mask, then calls `selcommon`.
- `sys___select50`: copies optional `timeval`, validates microseconds, converts to `timespec`, then calls `selcommon`.
- `sys_poll`: converts millisecond timeout to `timespec` and calls `pollcommon`.
- `sys___pollts50`: copies optional `timespec` and signal mask, then calls `pollcommon`.

Core scan/wait logic:
- `sel_do_scan`: common loop for select/poll. It sets temporary signal masks, assigns the current LWP to a per-CPU `selcluster`, scans descriptors, handles timeout, sleeps on a sleepq, retries on collisions, and maps restart/blocking errors to select/poll semantics.
- `selcommon`: imports fd sets, rejects absurd descriptor ranges, checks excess fd bits for `EBADF`, allocates stack or heap buffers, scans, and copies result sets back.
- `selscan`: walks input fd masks, calls each file’s `fo_poll`, marks ready descriptors, and supports direct event setting.
- `pollcommon`: imports a `pollfd` array with allocation guardrails, calls common scan, and copies results back.
- `pollscan`: calls `fo_poll` for each fd and sets `revents`, including `POLLNVAL` for bad descriptors.

Selectable-object API:
- `selrecord`: records the current LWP as a named waiter on a `selinfo`, or records a collision if another waiter already exists.
- `selnotify`: posts kqueue notes, wakes the named waiter if present, and wakes collision clusters.
- `sel_setevents`: directly updates select fd sets or poll `revents` when `direct_select` is enabled.
- `selclear`: removes the current LWP from all `selinfo` records after a scan/wait cycle.
- `selrecord_knote` / `selremove_knote`: kqueue integration.
- `selinit` / `seldestroy`: lifecycle for `selinfo`.
- `selsysinit`: initializes per-CPU select clusters.
- `seltrue`: trivial poll helper for always-readable/writable devices.

Concurrency/locking:
- The documented lock order is object lock before `selcluster_t::sc_lock`.
- `selcluster` distributes wait queues across up to 64 clusters to reduce contention.
- Collision wakeups use a bitmask of affected clusters and `sc_ncoll` generation checks to force rescans.
- Memory barriers guard races between `selrecord`, `selnotify`, and `selclear`.

Research notes:
- This file is central to filesystem-adjacent behavior because VFS files, sockets, devices, pipes, and pseudo-files expose readiness through `fo_poll` and `selinfo`.
