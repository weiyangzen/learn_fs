<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/overflowuid.c -->
# sources/test-tools/strace/tests/overflowuid.c

## Purpose

`sources/test-tools/strace/tests/overflowuid.c` is a C test program in the strace tests tree. It provides UID/GID overflow value decoder coverage that checks how strace prints kernel overflow IDs and related proc/sysctl state. The source was read as a complete 76-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `errno.h`, `fcntl.h`, `limits.h`, `stdlib.h`, `unistd.h`. functions: `read_int_from_file`, `check_overflow_id`, `check_overflowuid`, `check_overflowgid`. types: none found in this file. macros: none found in this file. notable constants/xlats: `O_RDONLY`. Source size: 76 lines, 1370 bytes.

## Control Flow

Control flow is provided through helper functions in this file and by the strace test harness that compiles or includes it into concrete test binaries.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/overflowuid.c -->
