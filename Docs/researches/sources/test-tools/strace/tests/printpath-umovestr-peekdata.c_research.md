<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/printpath-umovestr-peekdata.c -->
# sources/test-tools/strace/tests/printpath-umovestr-peekdata.c

## Purpose

`sources/test-tools/strace/tests/printpath-umovestr-peekdata.c` is a C test program in the strace tests tree. It provides low-level strace printer helper test coverage for path, string, signal, xlat, fd, time, flag, or user descriptor formatting. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `test_ucopy.h`, `stdio.h`. functions: `main`. types: none found in this file. macros: none found in this file. notable constants/xlats: `PTRACE_PEEKDATA`. Source size: 27 lines, 535 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/printpath-umovestr-peekdata.c -->
