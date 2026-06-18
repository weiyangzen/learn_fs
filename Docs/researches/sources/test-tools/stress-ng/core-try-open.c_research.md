# sources/test-tools/stress-ng/core-try-open.c

## Purpose
`core-try-open.c` safely probes whether a potentially blocking file or device can be opened without hanging the main stressor.

## Important APIs, Types, And Functions
`stress_try_open` forks a child to perform `open(path, flags)`, polls it with `waitpid(..., WNOHANG)`, and kills it if the timeout is exceeded. `stress_try_open_timeout` either uses POSIX timers and `SIGRTMIN` to interrupt a direct `open`, or falls back to plain `open` when timer support is unavailable. The internal `stress_try_kill` repeatedly signals and waits for a stuck child, then logs process info.

## Control Flow
`stress_try_open` first stats the path, forks, lets the child arm a short alarm and attempt open, then maps child exit status to `STRESS_TRY_OPEN_*` codes. The parent polls for a bounded number of retries based on the requested timeout, forcibly kills on wait errors or timeout, and handles vanished children. The timer-based variant installs a signal handler, creates a realtime timer for the timeout, calls open, deletes the timer, and restores errno.

## State And Persistence
No persistent project state is written. The code creates temporary child processes and a process-local POSIX timer. It may leave system-level traces only through logs and process info when a child cannot be killed.

## Dependencies And Integration Points
It depends on fork/wait/kill, `core-killpid`, `core-signal`, `stress_process_info`, stat/open shims, and stress-ng continue flags. Device and filesystem stressors can use it before touching risky paths.

## Risks
The helper deliberately handles broken drivers that may block in open forever, but an unkillable D-state child can still remain until the kernel releases it. `stress_try_open_timeout` uses `SIGRTMIN`, so signal-handler conflicts must be avoided. Returning `-1` for pre-stat failure differs from the defined positive status codes.

## Test Signals
Coverage comes from stressors that probe devices or special files and from error paths on busy/missing devices. Hangs, unreaped children, or lost errno after timeout are key failure signals.
