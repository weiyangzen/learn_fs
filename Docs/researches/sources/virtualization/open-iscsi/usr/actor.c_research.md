# File Research: sources/virtualization/open-iscsi/usr/actor.c

Implements open-iscsi’s single-threaded deferred work and timer scheduler. It maintains two global lists: `pend_list` for delayed actors sorted by monotonic due time, and `ready_list` for actors ready to execute.

Core behavior:
- `__actor_init` initializes an `actor_t` callback/data pair.
- `actor_schedule` and `actor_schedule_head` schedule immediate callbacks at tail or head of `ready_list`.
- `__actor_timer` and `actor_timer_mod` schedule delayed callbacks.
- `actor_delete` removes a scheduled/waiting actor and disables `alarm(0)` when no delayed work remains.
- `actor_poll` moves expired actors from `pend_list` to `ready_list`, arms `alarm()` for the next pending item, and executes callbacks sequentially.

Timing uses `CLOCK_MONOTONIC_COARSE` seconds and `SIGALRM`-style alarms. The implementation guards against recursive `actor_poll()` with `poll_in_progress`, but it is otherwise global-state and single-thread oriented. Callback execution happens after marking the actor `ACTOR_NOTSCHEDULED`, allowing callbacks to reschedule themselves.
