# sources/security-integrity/audit-userspace/src/libev/ev_poll.c

Purpose: implements the portable POSIX `poll(2)` backend for libev fd readiness. It is simpler than epoll and serves as a fallback or selected backend on platforms where poll is reliable.

Important APIs/functions: backend hooks are `poll_init`, `poll_modify`, `poll_poll`, and `poll_destroy`; helper `array_needsize_pollidx` initializes fd-to-poll-array indexes to `-1`. State uses `polls`, `pollcnt`, `pollmax`, `pollidxs`, and `pollidxmax`.

Control flow: `poll_init` installs backend callbacks and clears arrays. `poll_modify` ensures an index entry for the fd, allocates or updates a `struct pollfd` when interest is nonzero, and removes entries by swapping the last active pollfd into the removed slot. `poll_poll` calls `poll`, maps `POLLIN`/`POLLOUT` plus `POLLERR`/`POLLHUP` to libev read/write events, kills invalid fds on `POLLNVAL`, and invokes recovery helpers for `EBADF` or `ENOMEM`.

State and persistence: keeps a dense `polls` array for kernel calls and a sparse `pollidxs[fd]` reverse map. State is fully in memory and freed by `poll_destroy`; there is no persistent kernel registration between calls beyond the watched fd numbers.

Dependencies and integration: requires `<poll.h>` and libev core helpers from `ev.c`. It is included under `EV_USE_POLL` and selected by `loop_init` after higher-priority backends fail or are disabled.

Risks: `poll` scales linearly with active fds and platform-specific bugs are called out elsewhere in backend recommendation logic. Correct reverse-index maintenance is critical when removing by swap. `POLLNVAL` leads to watcher kill and `EV_ERROR` delivery through core `fd_kill`.

Test signals: watch multiple fds, add/remove from the middle of the poll array, verify read/write/hup/error mapping, inject closed fds to trigger `POLLNVAL`/`EBADF`, and run with many descriptors to catch index growth issues.
