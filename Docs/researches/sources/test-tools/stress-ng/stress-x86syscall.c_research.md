# sources/test-tools/stress-ng/stress-x86syscall.c

## Purpose
Implements Linux x86-64 `x86syscall`, directly exercising the `syscall` instruction through inline assembly wrappers for simple syscalls, measuring cost, and verifying selected results against libc.

## Important APIs, types, and functions
`stress_x86syscall()` is the entry point on supported Linux x86-64 builds. `stress_x86syscall_supported()` checks x86 CPU and syscall support. `x86_64_syscall0/1/2/3()` implement register-level syscall wrappers. Wrapped syscalls include `getcpu`, `geteuid`, `getgid`, `getpid`, `gettimeofday`, `getuid`, and `time` when syscall numbers exist. `x86syscall_check_x86syscall_func()` filters by `x86syscall-func`.

## Control flow
The stressor enables all compiled wrappers, applies optional filtering, logs selected names, compacts function pointers, synchronizes, then loops calling all selected wrappers and adding bogo count. It times the real phase, measures dummy wrapper overhead for about 0.1 seconds, restores bogo count, emits adjusted syscall and overhead metrics, then verifies direct syscall results against libc for IDs and time values.

## State and persistence
Static state is the mapping table and selection flags. Runtime state is local function pointer arrays and timing counters. No persistent state is written.

## Dependencies and integration points
Registered as `stress_x86syscall_info` with `CLASS_OS`, `VERIFY_ALWAYS`, `x86syscall-func` option, and `.supported` callback. Depends on Linux syscall numbers, x86-64 ABI registers, CPU feature probes, timing helpers, metrics, and libc verification wrappers.

## Risks and edge cases
The inline wrappers assign negative syscall returns directly to `errno` instead of negating them, which is incorrect for failing syscalls but rarely hit by current successful wrappers. Overhead subtraction can be noisy. The support message says Intel though the probe is generic x86. Direct time calls are only checked not to be earlier than libc-observed values.

## Test signals
Metrics report `nanosecs per call (excluding test overhead)` and `nanosecs for test overhead`. Verification failures compare direct syscall results with libc. Invalid `x86syscall-func` prints valid names and returns failure.
