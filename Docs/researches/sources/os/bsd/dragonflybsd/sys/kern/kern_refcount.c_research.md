# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_refcount.c

This file provides the non-trivial helper for DragonFlyBSD refcount wait/release APIs declared inline in `sys/refcount.h`.

Important function:
- `_refcount_wait(volatile u_int *countp, const char *wstr)` waits until a refcount reaches zero, ignoring the `REFCNTF_WAITING` flag in the zero test.

Behavior:
- Callers using this wait API must release references with `refcount_release_wakeup()`, not plain `refcount_release()`, because only the wakeup variant wakes sleepers.
- The function sets `REFCNTF_WAITING` atomically with `atomic_fcmpset_int()` after `tsleep_interlock()`, then sleeps with a 10-second timeout.
- It prints a warning every roughly 60 seconds of continued waiting.

Filesystem/storage relevance:
- Generic refcount waiting is used throughout kernel subsystems, including VFS, vnode, buffer, and storage objects where teardown must wait for outstanding references.
