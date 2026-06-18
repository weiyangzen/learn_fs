<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidns-cache.c -->
# sources/test-tools/strace/tests/pidns-cache.c

## Purpose

`sources/test-tools/strace/tests/pidns-cache.c` is a C test program in the strace tests tree. It provides pid namespace cache test that stresses reuse and invalidation of strace pid translation state. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `pidns.h`, `stdio.h`, `unistd.h`, `sys/time.h`. functions: `execute_syscalls`, `main`. types: `timeval`. macros: `SYSCALL_COUNT`, `MAX_TIME_RATIO`. direct syscall numbers: `__NR_getpid`, `__NR_getxpid`. Source size: 68 lines, 1304 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_getpid`, `__NR_getxpid`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidns-cache.c -->
