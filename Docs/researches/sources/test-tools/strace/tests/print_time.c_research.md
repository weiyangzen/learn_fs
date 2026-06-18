<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/print_time.c -->
# sources/test-tools/strace/tests/print_time.c

## Purpose

`sources/test-tools/strace/tests/print_time.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 54-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `time.h`. functions: `print_time_t_ex`, `print_time_t_nsec`, `print_time_t_usec`. types: `tm`. macros: none found in this file. Source size: 54 lines, 1134 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

Main risks are expected-output drift, architecture-specific formatting differences, and missing skip coverage when the target syscall is unavailable.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/print_time.c -->
