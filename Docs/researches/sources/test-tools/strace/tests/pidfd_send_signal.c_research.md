<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_send_signal.c -->
# sources/test-tools/strace/tests/pidfd_send_signal.c

## Purpose

`sources/test-tools/strace/tests/pidfd_send_signal.c` is a C test program in the strace tests tree. It provides pidfd_send_signal decoder coverage for pidfd arguments, signal names, siginfo_t decoding, PID translation, and PIDFD signal flag masks. The source was read as a complete 73-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `unistd.h`, `scno.h`, `pidns.h`, `fcntl.h`, `stdio.h`, `signal.h`. functions: `sys_pidfd_send_signal`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pidfd_send_signal`. notable constants/xlats: `O_RDONLY`, `PIDFD_SIGNAL_THREAD`, `PIDFD_SIGNAL_THREAD_GROUP`, `PIDFD_SIGNAL_PROCESS_GROUP`. Source size: 73 lines, 1842 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pidfd_send_signal`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_send_signal.c -->
