# File Research: sources/os/linux/linux-stable/fs/eventpoll.c

This file implements Linux `epoll`: scalable event-interest sets, readiness collection, wakeup callbacks, nested epoll handling, and the epoll syscalls.

Major responsibilities:
- Defines core objects:
  - `struct eventpoll`: one epoll instance with mutex, waitqueues, ready list, overflow list, rb-tree interest set, owning user, refcount, wakeup source, nesting metadata, and optional busy-poll state.
  - `struct epitem`: one watched target file/fd and event mask, linked into the epoll rb-tree, ready list, target file list, waitqueue list, and optional wakeup source.
  - `struct eppoll_entry`: one installed waitqueue callback on a target file.
- Implements epoll file operations: release, poll, fdinfo, ioctl, and llseek.
- Implements creation through `epoll_create()` / `epoll_create1()`.
- Implements control operations through `do_epoll_ctl()` and `epoll_ctl()`.
- Implements event delivery through `epoll_wait()`, `epoll_pwait()`, `epoll_pwait2()`, compat wrappers, and `epoll_sendevents()`.
- Maintains per-user watch accounting and `/proc/sys/fs/epoll/max_user_watches`.
- Supports optional network busy-poll parameters through `EPIOCSPARAMS` / `EPIOCGPARAMS`.

Locking model:
- The documented lock order is `epnested_mutex` first, then `ep->mtx`, then `ep->lock`.
- `epnested_mutex` serializes nested epoll insertion checks and prevents racing cycle creation.
- `ep->mtx` protects the rb-tree interest set, pollwait registration/removal, event transfer, ctl operations, and release cleanup.
- `ep->lock` protects ready-list and overflow-list manipulation from wakeup callbacks, including IRQ-context wakeups.
- Nested epoll polling uses lockdep nesting depth to annotate multiple `ep->mtx` acquisitions.

Ready-event flow:
- `ep_ptable_queue_proc()` installs `ep_poll_callback()` into target waitqueues during add.
- `ep_poll_callback()` filters disabled masks, requested event masks, and `EPOLLEXCLUSIVE`, then appends the item to `rdllist` or `ovflist` and wakes epoll waiters.
- `ep_start_scan()` steals `rdllist` into a private transfer list and enables `ovflist` so callbacks can queue events while userspace copies are in progress.
- `ep_send_events()` re-polls each ready item, copies events to userspace, applies `EPOLLONESHOT`, and requeues level-triggered items.
- `ep_done_scan()` merges overflow events back into `rdllist`, restores overflow-list inactive state, and wakes waiters if readiness remains.
- `ep_poll()` handles timeout conversion, waitqueue sleeps, signals, busy polling, and final locked readiness checks to avoid missed events.

Nested epoll and path limits:
- `ep_loop_check()` prevents cycles and chains deeper than `EP_MAX_NESTS`.
- `ep_loop_check_proc()` walks downward through nested epoll rb-trees and records reachable non-epoll files for reverse path checks.
- `ep_get_upwards_depth_proc()` walks upward through target-file backreferences under RCU.
- `reverse_path_check()` limits fanout paths from watched files to avoid wakeup storms.
- `attach_epitem()` links an epitem into `file->f_ep`; ordinary files get an allocated `epitems_head`, while epoll files reuse their `refs` list.

Lifetime and cleanup:
- `eventpoll_release_file()` removes all epoll watches that reference a file being closed.
- `ep_clear_and_put()` unregisters poll callbacks, removes all epitems, wakes poll waiters, and drops the epoll reference.
- Epitems are RCU-freed after removal; eventpoll structs are RCU-freed because upward-depth checks can still observe them.
- File references in `epi_fget()` are safe under `ep->mtx` because file teardown blocks in `eventpoll_release_file()`.

User-visible semantics:
- `EPOLLWAKEUP` requires `CAP_BLOCK_SUSPEND` when power management sleep is enabled.
- `EPOLLEXCLUSIVE` is allowed only on add, not modify, and not for nested epoll targets.
- `EPOLLERR` and `EPOLLHUP` are always added for add/modify interest masks.
- `epoll_wait` validates maxevents, userspace writeability, and that the fd is an epoll file before polling.
