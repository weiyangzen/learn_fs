<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-cap-ambient.c -->
# sources/test-tools/strace/tests/prctl-cap-ambient.c

## Purpose

`sources/test-tools/strace/tests/prctl-cap-ambient.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 80-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`, `linux/prctl.h`, `linux/capability.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_CAP_AMBIENT`, `PR_CAP_AMBIENT_RAISE`, `CAP_NET_RAW`, `CAP_AUDIT_CONTROL`, `PR_CAP_AMBIENT_LOWER`, `CAP_KILL`, `PR_CAP_AMBIENT_IS_SET`, `PR_CAP_AMBIENT_CLEAR_ALL`, `PR_CAP_AMBIENT_`. Source size: 80 lines, 2665 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-cap-ambient.c -->
