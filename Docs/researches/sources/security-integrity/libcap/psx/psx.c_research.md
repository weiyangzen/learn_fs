# sources/security-integrity/libcap/psx/psx.c

Purpose: C implementation of process-wide syscall synchronization for Linux threads, used to preserve POSIX-like privilege semantics.

Important APIs/functions: exports `psx_load_syscalls()`, `psx_syscall3()`, `psx_syscall6()`, `__psx_syscall()`, and `psx_set_sensitivity()`. Internal helpers initialize tracker state, allocate the thread map, manage state transitions, run immediate syscalls, scan `/proc/<pid>/task` with raw `getdents64`, and clean up at exit.

Control flow: `__psx_syscall()` validates argument count, enters setup, confirms the signal handler, runs the syscall on the caller, aborts fan-out if it fails, then enters syscall state, signals every other thread with hidden signal 33, waits for two complete no-pending sweeps, blocks until handlers finish, handles mismatched return values by sensitivity, restores errno, and returns the caller result.

State and dependencies: global `psx_tracker` stores PID, state, active command, handler actions, thread map, and incomplete count. It depends on raw syscalls, `/proc`, signals, atomics, and libpsx private headers.

Risks and test signals: signal 33 interposition, thread creation races, map collisions, fork inheritance, errno preservation, and deadlocks are main risks. Go and C tests cover thread sharing, churn, forks, cgo errno, and exploit prevention.
