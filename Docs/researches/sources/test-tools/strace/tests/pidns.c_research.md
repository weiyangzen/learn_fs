<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidns.c -->
# sources/test-tools/strace/tests/pidns.c

## Purpose

`sources/test-tools/strace/tests/pidns.c` is a C test program in the strace tests tree. It provides pid namespace executable fixture that exercises namespace setup and PID translation helpers used by syscall decoder tests. The source was read as a complete 244-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `pidns.h`, `linux/nsfs.h`, `errno.h`, `stdio.h`, `string.h`, `sys/types.h`, `signal.h`, `stdlib.h`, `sched.h`, `unistd.h`, `sys/wait.h`. functions: `pidns_print_leader`, `pidns_pid2str`, `pidns_fork`, `create_init_process`, `check_ns_ioctl`, `pidns_test_init`. types: `pid_type`. macros: none found in this file. notable constants/xlats: `O_RDONLY`. Source size: 244 lines, 5618 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `pidns.h` PID namespace setup and translated PID suffix rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidns.c -->
