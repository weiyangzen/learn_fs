# File Research: sources/os/bsd/freebsd-src/sys/sys/epoch.h

## Purpose
Declares FreeBSD epoch-based synchronization interfaces and global epoch helpers, especially for network stack read-side critical sections.

## Main Interfaces
- Public context type: `struct epoch_context`, `epoch_context_t`, `epoch_callback_t`.
- Kernel-only opaque `epoch_t`.
- Flags: `EPOCH_PREEMPT`, `EPOCH_LOCKED`.
- Global epochs: `global_epoch`, `global_epoch_preempt`, `net_epoch_preempt`.
- Tracker: `struct epoch_tracker`, with optional `EPOCH_TRACE` metadata.
- Kernel APIs: `epoch_alloc`, `epoch_free`, `epoch_wait`, `epoch_wait_preempt`, `epoch_drain_callbacks`, `epoch_call`, `in_epoch`, `in_epoch_verbose`.
- Preemptible enter/exit wrappers with optional file/line tracing.
- Network macros: `NET_EPOCH_ENTER`, `NET_EPOCH_EXIT`, `NET_EPOCH_WAIT`, `NET_EPOCH_CALL`, `NET_EPOCH_ASSERT`, task initialization helpers.

## Dependencies And Integration
Kernel section includes locks, per-CPU declarations, and Concurrency Kit `ck_epoch`. It integrates with `grouptask` scheduling for network tasks.

## Risk Notes
Correct pairing of enter/exit and proper tracker lifetime are critical. Trace mode changes function signatures through macros, so implementations must stay synchronized with this header.
