<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pselect6-common.c -->
# sources/test-tools/strace/tests/pselect6-common.c

## Purpose

`sources/test-tools/strace/tests/pselect6-common.c` is a C test program in the strace tests tree. It provides pselect6 decoder coverage for fd sets, timeout structures, signal masks, and time64 or common helper variants. The source was read as a complete 180-line file for this report.

## Important APIs, Types, and Functions

includes: `nsig.h`, `assert.h`, `stdio.h`, `unistd.h`, `sys/select.h`, `sys/time.h`, `kernel_timespec.h`. functions: `pselect6`, `handler`, `main`. types: `sigset_argpack`, `sigaction`, `itimerval`. macros: none found in this file. notable constants/xlats: `FD_SET`, `FD_ZERO`, `FD_SETSIZE`. Source size: 180 lines, 5327 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pselect6-common.c -->
