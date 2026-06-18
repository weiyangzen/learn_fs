# sources/test-tools/stress-ng/stress-lockmix.c

Purpose: implements `lockmix`, a mixed advisory-lock stressor that exercises `flock`, POSIX record locks, `lockf`, and open-file-description locks when available.

Important APIs/types/functions: compile-time feature macros enable lock families. `stress_lockmix_info_t` records offset, length, pid, and lock type. List helpers allocate/recycle records. `stress_lockmix_unlock()` dispatches the correct unlock operation for the oldest record. Timer helpers use POSIX timers or `setitimer()` to bound blocking operations. `stress_lockmix_contention()` randomly chooses a lock type and byte range.

Control flow: `stress_lockmix()` creates and fills a 1 MiB shared lock file, builds a weighted randomized lock-type table, starts a timeout facility, synchronizes, forks a child, and runs the same contention loop in parent and child. Cleanup deletes timers, kills the child if needed, frees records, closes/unlinks the file, and removes the directory.

State and persistence: in-process state is the held-lock linked list plus timer validity flags. Temporary filesystem state is removed. Lock records are popped before unlock syscalls so an unlock failure does not trap cleanup on one stale record forever.

Dependencies/integration: uses `flock`, `fcntl(F_SETLK/F_OFD_SETLK)`, `lockf`, timers, temp-file helpers, affinity, fork/kill helpers, and stress-ng synchronization. Registration uses `VERIFY_ALWAYS`.

Risks/test signals: mixing lock families can expose filesystem-specific behavior and blocking surprises. Useful signals are startup reporting enabled lock types, bogo progress under contention, timer deletion, temp-file cleanup, and unimplemented registration if no lock family exists.
