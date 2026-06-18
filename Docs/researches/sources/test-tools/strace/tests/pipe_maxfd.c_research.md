<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pipe_maxfd.c -->
# sources/test-tools/strace/tests/pipe_maxfd.c

## Purpose

`sources/test-tools/strace/tests/pipe_maxfd.c` is a C test program in the strace tests tree. It provides pipe/pipe2 decoder coverage for returned descriptor arrays, pipe flags, and maximum-fd edge cases. The source was read as a complete 47-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `limits.h`, `unistd.h`, `sys/resource.h`. functions: `move_fd`, `pipe_maxfd`. types: `rlimit`. macros: none found in this file. notable constants/xlats: `RLIMIT_NOFILE`. Source size: 47 lines, 945 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting.

## Risks and Edge Cases

signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pipe_maxfd.c -->
