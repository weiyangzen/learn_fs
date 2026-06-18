<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pipe.c -->
# sources/test-tools/strace/tests/pipe.c

## Purpose

`sources/test-tools/strace/tests/pipe.c` is a C test program in the strace tests tree. It provides pipe/pipe2 decoder coverage for returned descriptor arrays, pipe flags, and maximum-fd edge cases. The source was read as a complete 36-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `fcntl.h`, `unistd.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pipe`. Source size: 36 lines, 551 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pipe`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pipe.c -->
