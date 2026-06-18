<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll.c -->
# sources/test-tools/strace/tests/ppoll.c

## Purpose

`sources/test-tools/strace/tests/ppoll.c` is a C test program in the strace tests tree. It provides poll/ppoll decoder coverage for pollfd arrays, fd filtering/path rendering, timeouts, signal masks, and trace-fds option interactions. The source was read as a complete 294-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `errno.h`, `poll.h`, `signal.h`, `stdio.h`, `string.h`, `unistd.h`. functions: `sys_ppoll`, `main`. types: `pollfd`. macros: `PATH_TRACING_FD`, `TRACING_FDS`, `TRACING_FD1`, `TRACING_FD2`, `TRACE_FD1`, `TRACE_FD2`, `TRACE_OTHER_FDS`. direct syscall numbers: `__NR_ppoll`. variant settings: enables path tracing or decoded path output. Source size: 294 lines, 9141 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_ppoll`. It may create children, pipes, pidfds, or wait points so strace observes realistic process and descriptor state. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ppoll.c -->
