<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pkey_free.c -->
# sources/test-tools/strace/tests/pkey_free.c

## Purpose

`sources/test-tools/strace/tests/pkey_free.c` is a C test program in the strace tests tree. It provides memory protection key syscall decoder coverage for pkey allocation, free, and pkey_mprotect argument rendering. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `unistd.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pkey_free`. Source size: 36 lines, 735 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pkey_free`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pkey_free.c -->
