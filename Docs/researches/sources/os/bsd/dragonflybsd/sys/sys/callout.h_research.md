# File Research: sources/os/bsd/dragonflybsd/sys/sys/callout.h

Read completely: 149 lines.

This header defines DragonFlyBSD callout/timer structures and API declarations.

Key contents:
- Internal `_callout` with spinlock, existential lock state, queue entry, verifier, flags, debug line/identifier, optional lock, requested callback state, queued callback state, tick values, and waiter count.
- Public `struct callout` containing an opaque internal pointer plus initialization-copied lock/flags.
- Legacy macros to read/set callback argument and function.
- Optional debug arguments for callout initialization.
- Kernel prototypes for active/pending/deactivate, softclock tick, init variants, quick setup/cancel, reset, reset-by-CPU, stop, async stop, terminate, cancel, and drain.
- Public init macros inject file/line metadata when `CALLOUT_DEBUG` is enabled.

Security/reliability notes:
- Callout lifecycle is concurrency-sensitive; callers must choose stop/cancel/drain semantics according to whether callbacks may be running.
- Legacy direct argument/function macros are explicitly marked for old code only.
