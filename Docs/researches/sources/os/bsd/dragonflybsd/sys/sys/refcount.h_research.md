# File Research: sources/os/bsd/dragonflybsd/sys/sys/refcount.h

Atomic reference-count helper API with optional waiter wakeup support.

Key responsibilities:
- Defines `REFCNTF_WAITING` high-bit flag.
- Declares `_refcount_wait()`.
- Provides inline helpers to initialize, acquire one or many refs, release one or many refs, release with wakeup handling, and wait for refs to drain.
- Uses acquire atomic increments and fetch-add decrements.

Important behavior:
- Release helpers return true when the release drops the count to zero, ignoring the waiting flag.
- Wakeup releases clear `REFCNTF_WAITING` and wake waiters when the last ref is released with waiters present.
- `refcount_wait()` delegates only if the count is non-zero.

Dependencies:
- Includes `sys/systm.h` for `wakeup()` and machine atomics.

Notable risks:
- If `refcount_wait()` is used, all releases on that count must use wakeup-capable release helpers; the header warns this explicitly.
- The waiting flag shares the count word, so maximum practical refcount excludes that bit.
