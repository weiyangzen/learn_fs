# File Research: sources/os/linux/linux-stable/fs/select.c

## Purpose

Implements Linux `select()`, `pselect6()`, `poll()`, and `ppoll()` syscall machinery, including wait-queue registration, fd-set copying, timeout accounting/restart behavior, busy-poll integration, signal-mask handling, and compat/time32 variants.

## Main Responsibilities

- Provides timeout helpers:
  - `__estimate_accuracy()` and `select_estimate_accuracy()` compute timer slack.
  - `poll_select_set_timeout()` validates relative time values and converts them to absolute `timespec64` deadlines.
  - `poll_select_finish()` restores saved signal masks, optionally writes remaining timeout to userspace, and handles `STICKY_TIMEOUTS`.
- Implements poll wait table lifecycle:
  - `poll_initwait()` initializes `struct poll_wqueues`.
  - `poll_get_entry()` allocates inline or page-backed wait entries.
  - `__pollwait()` attaches file waiters to wait queues.
  - `pollwake()` and `__pollwake()` filter wake events, set `triggered`, and wake the polling task with ordering barriers.
  - `poll_freewait()` removes waiters and drops file references.
- Implements `select()`:
  - Copies input fd bitmaps from userspace, validates open fds with `max_select_fd()`, scans each selected fd with `vfs_poll()`, writes result bitmaps back, and handles `-ERESTARTNOHAND`.
  - Uses stack storage for small fd sets and `kvmalloc()` for larger sets.
- Implements `pselect6()`:
  - Reads optional timespec and packed userspace signal-mask pointer/size.
  - Installs temporary user signal mask using `set_user_sigmask()`.
  - Shares core select execution and finish logic.
- Implements `poll()`/`ppoll()`:
  - Copies user `struct pollfd` arrays into a stack/page-linked `poll_list`.
  - Calls `do_pollfd()` for each fd, storing `revents`.
  - Copies only `revents` back to userspace.
  - Supports syscall restart through `do_restart_poll()` and `current->restart_block`.
- Implements compat syscall variants for 32-bit fd-set word layout and time32/time64 interfaces under `CONFIG_COMPAT`.

## Key Data/Control Flow

- `do_select()` and `do_poll()` share the same wait queue model:
  - First pass registers waiters through `poll_table->_qproc`.
  - Once an event is found, `_qproc` is cleared to avoid registering unnecessary waiters.
  - If no events are ready, the task sleeps with `poll_schedule_timeout()`.
- `select_poll_one()` converts fd-set interest bits into poll keys and returns `EPOLLNVAL` for bad fds.
- `do_pollfd()` demangles user `POLL*` bits into internal `EPOLL*` bits and always includes `EPOLLERR` and `EPOLLHUP`.
- Busy-poll support uses `POLL_BUSY_LOOP`, `net_busy_loop_on()`, `busy_loop_current_time()`, and `busy_loop_timeout()` before sleeping.
- Timeout pointers represent absolute deadlines; zero timeout disables queue registration and makes the call nonblocking.

## Compatibility and ABI Notes

- Legacy `select()` uses `struct __kernel_old_timeval`; `pselect6()` and `ppoll()` use `struct __kernel_timespec`.
- 32-bit time variants use `old_timespec32`/`old_timeval32`.
- Compat select converts between `compat_ulong_t` fd bitmaps and native unsigned-long bitmaps with `compat_get_bitmap()`/`compat_put_bitmap()`.
- `old_select` syscall wrappers unpack architecture-specific argument structs when enabled.

## Correctness and Risk Notes

- `kern_select()` explicitly rejects negative `tv_sec` or `tv_usec` before normalization to prevent crafted negative values from saturating into effectively infinite deadlines.
- Poll wakeup uses paired memory barriers so event data written before wakeup is visible after the polling task wakes and clears `triggered`.
- `nfds` for `poll()` is capped by `RLIMIT_NOFILE`.
- Userspace timeout update failures after a successful wait can change restart behavior to avoid repeated faults on readonly timeout memory.
