# File Research: sources/os/bsd/openbsd-src/sbin/iked/timer.c

This small file wraps libevent one-shot timers for OpenIKED’s `struct iked_timer`.

Key responsibilities:
- `timer_set` initializes or resets a timer object, cancels a pending event if necessary, stores the environment/callback/argument, and binds `timer_callback`.
- `timer_add` schedules the event after a timeout in seconds.
- `timer_del` cancels a timer if it belongs to the given environment and has an initialized callback/event.
- `timer_callback` invokes the stored OpenIKED callback with the stored environment and argument.

Important dependencies:
- Uses libevent `evtimer_*` APIs.
- Used by code such as RADIUS retry/failover handling.

Security and correctness notes:
- Ownership is guarded by comparing `tmr->tmr_env` to the supplied environment in `timer_del`.
- The helper does not clear callback pointers after firing; reuse is managed by callers.
