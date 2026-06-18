<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise.c -->
# sources/test-tools/strace/tests/process_madvise.c

## Purpose

`sources/test-tools/strace/tests/process_madvise.c` is a C test program in the strace tests tree. It provides strace test-suite coverage for `process_madvise` syscall or printer behavior. The source was read as a complete 86-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/mman.h`, `sys/uio.h`. functions: `k_process_madvise`, `main`. types: `iovec`. macros: `FD0_PATH`. direct syscall numbers: `__NR_process_madvise`. notable constants/xlats: `O_WRONLY`. variant settings: enables path tracing or decoded path output. Source size: 86 lines, 2431 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_process_madvise`. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise.c -->
