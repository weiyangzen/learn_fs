<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open.c -->
# sources/test-tools/strace/tests/pidfd_open.c

## Purpose

`sources/test-tools/strace/tests/pidfd_open.c` is a C test program in the strace tests tree. It provides pidfd_open decoder coverage for PID arguments, PIDFD flag xlat output, pid namespace translation, path tracing, and pidfd-specific fd annotations. The source was read as a complete 130-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `kernel_fcntl.h`, `pidns.h`. functions: `k_pidfd_open`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_pidfd_open`. notable constants/xlats: `O_WRONLY`, `O_NONBLOCK`, `PIDFD_NONBLOCK`, `O_EXCL`, `PIDFD_THREAD`, `PIDFD_AUTOKILL`, `O_TRUNC`. variant settings: enables path tracing or decoded path output; enables pidfd fd annotation output. Source size: 130 lines, 2943 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_pidfd_open`.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_open.c -->
