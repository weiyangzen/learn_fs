<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pread64-pwrite64.c -->
# sources/test-tools/strace/tests/pread64-pwrite64.c

## Purpose

`sources/test-tools/strace/tests/pread64-pwrite64.c` is a C test program in the strace tests tree. It provides pread/pwrite and preadv/pwritev decoder coverage for offsets, iovec formatting, and paired read/write syscall variants. The source was read as a complete 203-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `unistd.h`. functions: `dump_str`, `print_hex`, `test_dump`, `main`. types: none found in this file. macros: none found in this file. notable constants/xlats: `O_CREAT`, `O_RDONLY`, `O_TRUNC`, `O_WRONLY`. Source size: 203 lines, 4936 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pread64-pwrite64.c -->
