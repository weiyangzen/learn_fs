<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl_marker.c -->
# sources/test-tools/strace/tests/prctl_marker.c

## Purpose

`sources/test-tools/strace/tests/prctl_marker.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 22-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `unistd.h`. functions: `prctl_marker`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. Source size: 22 lines, 445 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl_marker.c -->
