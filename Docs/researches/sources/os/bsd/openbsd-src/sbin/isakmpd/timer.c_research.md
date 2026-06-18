# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/timer.c

This file implements a small monotonic-clock timer queue for isakmpd.

Key APIs:
- `timer_init()`: initializes the global event queue.
- `timer_next_event(struct timespec **timeout)`: computes the timeout until the first event for the main loop.
- `timer_handle_expirations()`: executes and frees all expired events in order.
- `timer_add_event(char *name, void (*func)(void *), void *arg, struct timespec *expiration)`: allocates and inserts an event sorted by expiration time.
- `timer_remove_event(struct event *)`: removes and frees a scheduled event.
- `timer_report()`: logs all scheduled events and remaining seconds.

Behavior and integration:
- Uses `CLOCK_MONOTONIC`, `TAILQ`, and OpenBSD timespec macros.
- Event callbacks run synchronously from `timer_handle_expirations()`.
- Used throughout isakmpd for retransmissions, SA expiration, DPD, NAT-T keepalives, and queued PF_KEY notifications.

Risk notes:
- Callback execution happens before freeing the event structure; callbacks must not assume the event pointer remains registered.
- The queue is single-threaded and not protected by locks, matching isakmpd’s event-loop model.
