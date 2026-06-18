# sources/test-tools/stress-ng/stress-wait.c

## Purpose
Implements `wait`, a scheduler/OS stressor for wait-family APIs. It creates a runner child that is repeatedly stopped/continued by a killer child while the parent exercises wait calls.

## Important APIs, types, and functions
`stress_wait()` is the entry point except on GNU/Hurd. `spawn()` forks children. `runner()` pauses until termination. `killer()` sends `SIGSTOP`/`SIGCONT` and wakes the parent if waits stall. `stress_wait_continued()` counts continued events. `syscall_shim_waitpid()` uses raw `waitpid` syscall when available.

## Control flow
After installing a `SIGUSR1` ignore handler and synchronizing, the parent spawns runner and killer. The loop calls `waitpid`, `wait`, optional `wait3`, optional `wait4` with several PID forms and invalid arguments, and optional `waitid`. Expected races such as `EINTR` and `ECHILD` are tolerated; unexpected errors or invalid `waitid()` fields fail the run. Cleanup kills/reaps both children.

## State and persistence
State is runner/killer PIDs, status values, optional `rusage`, and bogo count. No persistent files or shared memory are used.

## Dependencies and integration points
Registered as `stress_wait_info` with `CLASS_SCHEDULER | CLASS_OS` and `VERIFY_ALWAYS`. Depends on stress-ng fork retry, kill/wait, signal, pause, yield, and parent-death helpers. Disabled on GNU/Hurd because of a documented kernel assertion.

## Risks and edge cases
The same child state is observed through multiple APIs, so `ECHILD` and interruptions are expected. The killer sends `SIGUSR1` after `ABORT_TIMEOUT` to prevent indefinite parent blocking. Heavy load can produce `waitid()` with `si_pid == 0`, which is tolerated.

## Test signals
Bogo increments indicate continued events. Failures are unexpected wait errors or inconsistent `waitid()` PID/signo/status/code.
