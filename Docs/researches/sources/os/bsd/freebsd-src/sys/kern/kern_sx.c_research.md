# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sx.c

## Purpose

Implements FreeBSD `sx` shared/exclusive sleep locks. These locks support shared readers, exclusive writers, optional recursion, upgrade/downgrade, interruptible waits, sleep queues, adaptive spinning on SMP, WITNESS/lockstat integration, and DDB diagnostics.

## Main Responsibilities

- Defines `lock_class_sx` and lock class operations for generic lock APIs.
- Initializes and destroys locks with `sx_init_flags()`, `sx_sysinit()`, and `sx_destroy()`.
- Implements shared locking:
  - `sx_try_slock_int()`
  - `_sx_slock_int()`
  - `_sx_slock_hard()`
  - `_sx_sunlock_int()`
  - `_sx_sunlock_hard()`
- Implements exclusive locking:
  - `_sx_xlock()`
  - `_sx_xlock_hard()`
  - `sx_try_xlock_int()`
  - `_sx_xunlock()`
  - `_sx_xunlock_hard()`
- Implements lock conversion:
  - `sx_try_upgrade_int()`
  - `sx_downgrade_int()`
- Provides assertion and debug support through `_sx_assert()`, `db_show_sx()`, and `sx_chain()`.

## Important Control Flow

- Fast paths use atomic compare-and-set on `sx_lock` for uncontended acquisition/release.
- Exclusive hard lock path handles recursion, adaptive spinning on a running owner, writer-spinner coordination against readers, setting exclusive waiter bits, and sleeping on the exclusive sleep queue.
- Shared hard lock path tries to enter while shared ownership is allowed, spins adaptively on active exclusive owners or reader state, sets shared waiter bits, and sleeps on the shared sleep queue if needed.
- Exclusive unlock wakes either shared or exclusive waiters depending on waiter bits and sleep queue contents.
- Shared unlock wakes exclusive waiters when the final reader releases and exclusive waiters are present.
- Downgrade converts an unrecursed exclusive hold into one shared hold and may wake shared waiters.
- Upgrade succeeds only when the caller is the sole shared holder, preserving waiter state.

## State, Tunables, and Locking

- `sx_lock` encodes owner/readers plus waiter and spinner bits.
- `sx_recurse` tracks exclusive recursion depth.
- Sleep queues use two queues:
  - queue 0 for exclusive waiters
  - queue 1 for shared waiters
- Giant is dropped before sleeping or adaptive spinning and restored afterward.
- With adaptive sx enabled, backoff parameters come from the global lock delay configuration or `debug.sx.*` custom knobs.
- Integrated with WITNESS, LOCK_PROFILING, KDTRACE lockstat probes, KTR tracing, and optional HWPMC lock-failed hooks.

## Filesystem Relevance

`sx` locks are widely used in FreeBSD VFS and filesystem code for sleepable shared/exclusive protection: mount structures, namecache-related paths, global namespace operations, and long-running operations that cannot use spin mutexes. Correct sx behavior is foundational for filesystem concurrency and deadlock avoidance.

## Cautions

- Shared ownership is not per-thread tracked without WITNESS; non-WITNESS assertions can only prove some reader exists.
- Recursion applies to exclusive locks when the lock is initialized as recursable.
- Interruptible sx waits can return errors and must be handled by callers.
- Waiter bit transitions and sleep queue locking are subtle; correctness depends on preserving flags across atomic state changes.
