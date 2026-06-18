# sources/test-tools/stress-ng/stress-nice.c

## Purpose
`stress-nice.c` implements the `nice` stressor. It repeatedly forks child processes that exercise `nice(2)`, `getpriority(2)`, and `setpriority(2)` across valid and invalid priority operations, stressing scheduler priority management and permission checks.

## Important APIs, Types, and Functions
The exported `stress_nice_info` registers a `CLASS_SCHEDULER | CLASS_OS` stressor with `VERIFY_ALWAYS`. `stress_nice_delay()` busy-yields for a short random duration to give priority changes scheduler-visible time. `stress_nice()` is the entry point. It uses `stress_capabilities_check(SHIM_CAP_SYS_NICE)`, `getrlimit(RLIMIT_NICE)`, `fork`, `shim_nice`, `getpriority`, `setpriority`, `stress_sched_settings_apply`, and `shim_waitpid`.

## Control Flow
The parent detects whether `CAP_SYS_NICE` is available and derives an assumed priority range, adjusted by `RLIMIT_NICE` where present. During the run loop it forks one child at a time. The child sets up failure injection, parent-death alarm, and scheduler settings. It probes whether raising priority is permitted, reads priorities for process/user/group selectors, and intentionally calls `setpriority()` with invalid selectors and IDs. It then either walks the configured setpriority range for its own PID or repeatedly calls `nice(1)` from -19 to 19. When `getpriority()` is available it checks that `nice(1)` does not increase the nice value by more than one step. The parent waits and propagates non-success exit status.

## State and Persistence
Priority changes are confined to the child process that exits at the end of each iteration. The parent keeps only the return code. No durable files or system settings are changed. Bogo counts are incremented by the child before exit; parent-side forced kill paths mark bogo state as force-killed when wait fails.

## Dependencies and Integration Points
The stressor depends on either `nice` or `setpriority`, and optionally `getpriority` and `RLIMIT_NICE`. It integrates with stress-ng capabilities, scheduler setup, kill helpers, parent-death alarm, process states, bogo counters, and stress-ng unimplemented metadata. It uses `core-killpid.h` to clean up children when wait fails.

## Risks
Priority semantics vary by platform, resource limit, user namespace, and capability set. The code assumes an approximate -20 to 20 priority range and adjusts it only when `RLIMIT_NICE` is available. Bogo increments happen in children, so abnormal child termination can make counters less reliable. The stressor intentionally invokes invalid `setpriority()` arguments, which should remain non-fatal but may produce platform-specific errno behavior.

## Test Signals
Run as a normal user and with `CAP_SYS_NICE` to cover both permission paths. Verify short timeout completion, no leaked child processes, and no false failure from valid `nice(1)` increments. Build tests should cover configurations with only `nice`, only `setpriority`, and neither to validate unimplemented fallback.
