<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pc.c -->
# sources/test-tools/strace/tests/pc.c

## Purpose

`sources/test-tools/strace/tests/pc.c` is a C test program in the strace tests tree. It provides program-counter reporting test that checks strace instruction pointer / PC annotation output around a controlled syscall. The source was read as a complete 83-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `assert.h`, `dlfcn.h`, `fcntl.h`, `unistd.h`, `sys/mman.h`, `sys/wait.h`, `sys/sendfile.h`, `sys/prctl.h`. functions: `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_write`. notable constants/xlats: `PR_SET_DUMPABLE`, `O_RDONLY`. Source size: 83 lines, 1821 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_write`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pc.c -->
