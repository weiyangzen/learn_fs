<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tsc.c -->
# sources/test-tools/strace/tests/prctl-tsc.c

## Purpose

`sources/test-tools/strace/tests/prctl-tsc.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 54-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_GET_TSC`, `PR_SET_TSC`, `PR_TSC_`, `PR_TSC_SIGSEGV`. Source size: 54 lines, 1447 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-tsc.c -->
