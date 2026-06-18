# sources/distributed-fs/tahoe-lafs/src/allmydata/test/blocking.py

## Purpose
Provides a debugging helper for tests that need to detect event-loop blocking. It uses a fast real-time alarm to print the reactor thread stack when the loop stops cycling for longer than a small threshold.

## Important APIs, Types, And Functions
`print_stacks()` prints a warning and the current reactor-thread stack. `catch_blocking_in_event_loop(test=None)` installs a `SIGALRM` handler, schedules repeated timers with `signal.setitimer()` and `reactor.callLater()`, and optionally registers cleanup on a Trial test case.

## Control Flow
Calling `catch_blocking_in_event_loop()` starts a recurring Twisted callback that cancels and rearms a short real-time timer. If the event loop is blocked and the callback cannot run, the timer expires and the signal handler prints the current thread stack. Cleanup restores the default signal handler, disables the timer, and cancels the scheduled callback.

## State And Persistence
State is process-global signal configuration plus one mutable holder for the active delayed call. It writes only to stdout through `print()`.

## Dependencies And Integration Points
Depends on Unix-like `signal.SIGALRM`, `threading`, `sys._current_frames()`, `traceback`, and Twisted reactor scheduling. It is intended for tests, not normal runtime.

## Risks And Test Signals
The helper is platform-sensitive and process-global; nested users can clobber signal handlers, and very tight 10-15 ms timers can be noisy on slow CI. Useful signals are stack dumps during intentional blocking tests, cleanup restoring `SIG_DFL`, no lingering delayed calls, and skip or guarded usage on platforms without compatible alarm semantics.
