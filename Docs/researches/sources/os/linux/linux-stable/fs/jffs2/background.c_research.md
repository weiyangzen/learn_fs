# File Research: sources/os/linux/linux-stable/fs/jffs2/background.c

## Scope
Implements the JFFS2 background garbage-collection kernel thread lifecycle and wake/stop signaling.

## Primary APIs
Provides `jffs2_garbage_collect_trigger()`, `jffs2_start_garbage_collect_thread()`, and `jffs2_stop_garbage_collect_thread()`. The thread body is `jffs2_garbage_collect_thread()`.

## Behavior
Start initializes completion objects, creates `jffs2_gcd_mtd%d`, waits until the thread publishes `c->gc_task`, and returns the thread pid or error.

Trigger requires `erase_completion_lock` held and sends `SIGHUP` when the GC task exists and `jffs2_thread_should_wake()` says work is needed.

Stop sends `SIGKILL` under `erase_completion_lock` if a GC task is active and waits for thread exit completion.

The GC thread allows `SIGKILL`, `SIGSTOP`, and `SIGHUP`, sets low priority, becomes freezable, sleeps until GC is needed, adds a 50 ms throttle delay to reduce boot-time starvation, handles freezer and signals, blocks SIGHUP while running a pass, and calls `jffs2_garbage_collect_pass()`. `-ENOSPC` terminates the thread.

## State And Data
Uses `c->gc_task`, `gc_thread_start`, `gc_thread_exit`, `erase_completion_lock`, and MTD index for thread naming.

## Dependencies
Depends on JFFS2 GC policy/pass functions, kernel kthreads, signals, freezer, completions, scheduler, and MTD metadata.

## Risks And Invariants
`gc_task` is protected by `erase_completion_lock`. SIGHUP is a wake signal, SIGKILL is teardown, and freezer handling must return to the sleep check after thaw.
