# File Research: sources/os/bsd/freebsd-src/sys/sys/lock_profile.h

Defines lock profiling declarations and no-op fallbacks.

Key content:
- Declares `struct lock_profile_object` and `LIST_HEAD(lpohead, lock_profile_object)`.
- Under `_KERNEL && LOCK_PROFILING`, includes CPU timing and lock definitions.
- Declares `lock_prof_enable` and profiling hooks for successful lock obtain, release, and thread exit.
- Inline `lock_profile_obtain_lock_failed()` records wait start time with `nanoseconds()` when profiling is enabled, the lock is profileable, and contention has not already been recorded.
- Without `LOCK_PROFILING`, all profiling macros compile to no-ops.

Research relevance:
- Used with `lockstat.h` and lock implementations to record contention timing and hold behavior.
- Important for diagnosing filesystem/VFS lock contention under load.
- `LO_NOPROFILE` from `lock.h` suppresses profiling for specific locks.

Cautions:
- Profiling code exists only in kernel builds with `LOCK_PROFILING`.
- The failed-obtain helper only records first contention per attempt through the caller-provided `contested` flag.
