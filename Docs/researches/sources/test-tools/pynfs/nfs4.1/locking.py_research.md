# sources/test-tools/pynfs/nfs4.1/locking.py

## Purpose
`locking.py` provides small concurrency primitives for the NFSv4.1 test server: a named counter, a switchable debug wrapper around `threading.Lock`, and a simple read/write lock with optional verbose acquisition tracing.

## Important APIs, Types, And Functions
- `DEBUG` selects normal locks or debug/verbose lock wrappers at creation time.
- `Counter(first_value=0, name="counter")` uses a lock to return monotonically increasing values from `next()`.
- `Lock(name="")` returns `_DebugLock` when debugging or a normal `threading.Lock` otherwise.
- `RWLock(name="")` returns `_RWLockVerbose` when debugging or `_RWLock` otherwise.
- `_DebugLock` wraps a normal lock and records/prints thread lock state on acquire/release.
- `_RWLock` implements `acquire` for read, `acquire_write` for write, `release`, `upgrade`, and `downgrade`.
- `_RWLockVerbose` subclasses `_RWLock` and decorates internal read/write operations with debug tracing.

## Control Flow
`Counter.next` locks, returns the current value, increments, and releases. Normal `Lock` is just `threading.Lock`; debug mode records waiting/holding/released states on the current thread.

`_RWLock.acquire` increments read-waiter count and waits while any writer wants or owns the lock. `_RWLock.acquire_write` increments writer count, waits for readers to drain, then waits until it can acquire the write mutex. `release` infers whether to release read or write based on global read-lock count. `upgrade` releases one read lock without notifying, then waits for write access; `downgrade` releases write access and reacquires read access.

## State And Persistence Behavior
All state is in process memory. `_RWLock` keeps condition, write mutex, writer count, reader count, and active-reader count. Debug locks also attach a `locks` dictionary to thread objects for inspection. There is no persistence.

## Dependencies And Integration Points
The module depends on `threading`. `fs.py`, `nfs4lib.SSVContext`, `nfs4proxy`, and other server modules use `Lock`, `RWLock`, or `Counter` for object state, replay/cache state, and ID generation.

## Risks And Edge Cases
- `_RWLock.release` decides release type from aggregate `_read_lock`, not per-thread ownership; a writer calling release while any reader exists can incorrectly release a read lock.
- `upgrade` can deadlock or starve when multiple readers attempt upgrade.
- `threading.Condition.notifyAll()` and `threading.currentThread()` are old names; modern Python prefers `notify_all()` and `current_thread()`.
- `_RWLockVerbose` calls `super(_RWLockVerbose, self)._acquire_read()` instead of `super(...)._acquire_read`, which retrieves an attribute incorrectly in Python.
- Debug mode is selected at lock creation, so toggling `DEBUG` later does not affect existing locks.

## Test Signals
Tests should cover counter uniqueness under concurrency, multiple readers, writer exclusion, read-to-write upgrade, write-to-read downgrade, unmatched releases, and debug-mode tracing compatibility with context-manager usage.
