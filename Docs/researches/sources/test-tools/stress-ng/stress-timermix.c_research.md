# sources/test-tools/stress-ng/stress-timermix.c

## Purpose
Implements the `timermix` stressor, a mixed timer signal workload that combines POSIX timers across available clock ids with interval timers (`setitimer`) where supported. It measures per-timer tick rates while forcing signal delivery through multiple timer mechanisms.

## Important APIs, Types, And Functions
`stress_timer_info_t` records POSIX timer clock id, name, timer id, and signal count. `stress_itimer_info_t` records `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF` ids, signal numbers, names, and counts. `stress_timermix_timer_set()` and `stress_timermix_itimer_set()` create nonzero periodic timers from default rates. `stress_timermix_timer_action()` handles `SIGRTMIN` POSIX timer signals, accounts the specific timer through `siginfo`, increments bogo ops, and adaptively throttles POSIX timer frequency. `stress_timermix_itimer_action()` handles interval timer signals and counts by signal number.

## Control Flow
At startup, the stressor installs `SA_SIGINFO` handlers, creates POSIX timers for every supported clock in `timer_info[]`, and installs handlers for each itimer signal. If no timer path is available it skips. After synchronization, it arms all created POSIX timers and all supported itimers, then the main thread repeatedly nanosleeps for 100 us and yields until stopped. Signal handlers drive almost all bogo activity. On exit or error, `stop_timers` disarms POSIX timers, deletes them, emits per-clock tick/sec metrics, disarms itimers, emits per-itimer tick/sec metrics, and sets deinit state.

## State And Persistence Behavior
State is process-global because asynchronous signal handlers update timer arrays and global rates. Kernel timer objects are deleted, and itimers are zeroed before exit. No files are created. Counts persist only until metrics are emitted.

## Dependencies And Integration Points
The file conditionally enables POSIX timers with librt timer APIs and `SA_SIGINFO`, and interval timers with `getitimer`/`setitimer` and `SA_SIGINFO`. It uses stress-ng timing, bogo accounting, proc-state, metrics, and scheduler yield helpers. It registers as `CLASS_SIGNAL | CLASS_INTERRUPT | CLASS_OS`, `VERIFY_ALWAYS`, and exposes maximum metric items equal to enabled timer plus itimer counts.

## Risks And Test Signals
Signal load can overwhelm a system, so POSIX timer frequency is adaptively increased or decreased based on whether handler checks happen within a one-second window. Some clocks may reject timer creation and are skipped individually. Cygwin-specific `EINVAL` from unsupported virtual/prof itimers is tolerated. Test signals include per-clock and per-itimer tick/sec metrics, bogo progress from signal handlers, clean timer deletion, and no-resource skip when no timers can be created.
