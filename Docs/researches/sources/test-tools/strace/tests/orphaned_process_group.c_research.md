<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/orphaned_process_group.c -->
# sources/test-tools/strace/tests/orphaned_process_group.c

## Purpose

`sources/test-tools/strace/tests/orphaned_process_group.c` is a C test program in the strace tests tree. It provides terminal/job-control fixture that creates an orphaned process group and checks strace behavior around stopped or signalled children. The source was read as a complete 155-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `signal.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `sys/wait.h`. functions: `alarm_handler`, `main`. types: `sigaction`. macros: `TIMEOUT`. notable constants/xlats: `SIG_SETMASK`, `SIG_DFL`. Source size: 155 lines, 3502 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/orphaned_process_group.c -->
