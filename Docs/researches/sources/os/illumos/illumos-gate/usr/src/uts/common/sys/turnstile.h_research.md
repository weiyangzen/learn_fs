# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/turnstile.h

## Purpose
Kernel priority-inheritance turnstile structure and operation declarations.

## Main Interfaces
- Defines queue indexes `TS_WRITER_Q`, `TS_READER_Q`, and `TS_NUM_Q`.
- Defines opaque `turnstile_t` and `struct turnstile`.
- `struct turnstile` contains sleep queues for reader/writer waiters, inheritor thread, owner sobj, free-list pointer, lock, and block timestamp.
- Declares `turnstile_lookup`, `turnstile_exit`, `turnstile_wakeup`, `turnstile_change_pri`, `turnstile_unsleep`, `turnstile_stay_asleep`, and `turnstile_pi_recalc`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/time.h`, `sys/param.h`, `sys/sleepq.h`, `sys/mutex.h`, and `sys/lwp_timer_impl.h`. Used by synchronization object implementations that need blocking queues and priority inheritance.

## Research Notes
Turnstiles are shared synchronization infrastructure; their reader/writer queue split supports both exclusive and shared synchronization objects.
