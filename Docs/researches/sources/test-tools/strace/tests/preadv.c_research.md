<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/preadv.c -->
# sources/test-tools/strace/tests/preadv.c

## Purpose

`sources/test-tools/strace/tests/preadv.c` is a C test program in the strace tests tree. It provides pread/pwrite and preadv/pwritev decoder coverage for offsets, iovec formatting, and paired read/write syscall variants. The source was read as a complete 140-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `fcntl.h`, `stdio.h`, `sys/uio.h`, `unistd.h`. functions: `print_iov`, `print_iovec`, `main`. types: `iovec`. macros: `LEN`. notable constants/xlats: `O_RDONLY`, `O_RDWR`. Source size: 140 lines, 3280 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/preadv.c -->
