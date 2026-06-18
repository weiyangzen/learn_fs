<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-seccomp-filter-v.c -->
# sources/test-tools/strace/tests/prctl-seccomp-filter-v.c

## Purpose

`sources/test-tools/strace/tests/prctl-seccomp-filter-v.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 119-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stddef.h`, `unistd.h`, `stdio.h`, `errno.h`, `sys/prctl.h`, `linux/seccomp.h`, `linux/filter.h`, `scno.h`. functions: `main`. types: `sock_filter`, `seccomp_data`, `sock_fprog`. macros: `SOCK_FILTER_ALLOW_SYSCALL`, `SOCK_FILTER_DENY_SYSCALL`, `SOCK_FILTER_KILL_PROCESS`, `PRINT_ALLOW_SYSCALL`, `PRINT_DENY_SYSCALL`. direct syscall numbers: `__NR_get_thread_area`. notable constants/xlats: `PR_SET_SECCOMP`, `SECCOMP_MODE_FILTER`, `SECCOMP_RET_ALLOW`, `SECCOMP_RET_ERRNO`, `SECCOMP_RET_DATA`, `SECCOMP_RET_KILL`, `PR_SET_NO_NEW_PRIVS`, `SECCOMP_RET_KILL_THREAD`. variant settings: uses verbose structure decoding. Source size: 119 lines, 2933 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_get_thread_area`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-seccomp-filter-v.c -->
