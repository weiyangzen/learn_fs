# File Research: sources/os/linux/linux/fs/select.c

Implements Linux `select(2)`, `pselect(2)`, `poll(2)`, and `ppoll(2)`, including native, old-time32, and compat syscall variants.

The shared wait machinery is `poll_wqueues`: `poll_initwait()`, `__pollwait()`, `pollwake()`, `poll_schedule_timeout()`, and `poll_freewait()`. Wait entries are stored inline first, then in page-sized `poll_table_page` allocations, with wakeup memory barriers pairing `pollwake()` and `poll_schedule_timeout()`.

The `select` path copies three fd bitmaps from userspace, validates selected descriptors with `max_select_fd()`, loops through ready masks in `do_select()`, writes result bitmaps back, and uses `poll_select_finish()` to restore signal masks and optionally update remaining timeout.

The `poll` path chunks userspace `struct pollfd` arrays into a stack-first `poll_list` plus page allocations, calls `do_pollfd()`/`vfs_poll()` for each entry, writes only `revents` back, and supports restart through `do_restart_poll()`.

Timeout logic converts relative timeval/timespec inputs into absolute `timespec64`, estimates scheduling slack from task niceness and `current->timer_slack_ns`, rejects invalid negative/unnormalized values, and preserves `STICKY_TIMEOUTS` behavior. Network busy-poll support is integrated through `POLL_BUSY_LOOP`.
