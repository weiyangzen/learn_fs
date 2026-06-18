# File Research: sources/os/linux/linux/fs/jffs2/background.c

## Role

`background.c` implements the optional per-filesystem JFFS2 background garbage-collection kernel thread. The thread wakes when flash-space conditions require GC, performs GC passes, handles freezer and signal events, and exits cleanly on unmount or fatal GC-space failure.

## Public Entry Points

- `jffs2_garbage_collect_trigger()`: called with `erase_completion_lock` held; sends `SIGHUP` to the GC task if it exists and `jffs2_thread_should_wake()` says work is needed.
- `jffs2_start_garbage_collect_thread()`: initializes start/exit completions, starts `jffs2_garbage_collect_thread()` with an MTD-indexed thread name, waits until the thread records itself, and returns the PID or error.
- `jffs2_stop_garbage_collect_thread()`: sends `SIGKILL` to the GC task under `erase_completion_lock` and waits for the exit completion.

## Thread Loop

`jffs2_garbage_collect_thread()`:
- Allows `SIGKILL`, `SIGSTOP`, and `SIGHUP`.
- Stores `current` in `c->gc_task` and completes startup.
- Lowers priority with `set_user_nice(current, 10)`.
- Marks itself freezable.
- Sleeps when `jffs2_thread_should_wake()` is false.
- Adds a 50 ms interruptible delay each cycle to avoid starving userspace during mount-time or heavy GC work.
- Handles freezer events and pending signals.
- Blocks `SIGHUP` while running a GC pass so wakeup signals do not interrupt the pass.
- Calls `jffs2_garbage_collect_pass(c)` until killed or until `-ENOSPC` aborts the thread.

## Signal Semantics

- `SIGHUP`: wake/request another GC check.
- `SIGSTOP`: enter kernel signal stop.
- `SIGKILL`: exit thread, used by unmount.
- Freezer: calls `try_to_freeze()` and restarts wake checks after thaw.

## Important Invariants

- `c->gc_task` is protected by `erase_completion_lock`.
- `jffs2_start_garbage_collect_thread()` must only run when no GC thread exists.
- Thread startup and shutdown are synchronized with completions.
- `jffs2_garbage_collect_trigger()` assumes the caller already holds `erase_completion_lock`.

## Research Notes

This file is operational glue around JFFS2 garbage collection rather than the GC algorithm itself. Its main concerns are avoiding mount-time/user-visible starvation, cooperating with suspend/freezer, and making unmount shutdown deterministic.
