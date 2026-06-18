<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_readv_writev.c -->
# sources/test-tools/strace/tests/process_vm_readv_writev.c

## Purpose

`sources/test-tools/strace/tests/process_vm_readv_writev.c` is a C test program in the strace tests tree. It provides process_vm_readv/process_vm_writev decoder coverage for cross-process iovec arguments, PID rendering, string previews, invalid counts, and shared read/write formatting. The source was read as a complete 292-line file for this report.

## Important APIs, Types, and Functions

includes: `inttypes.h`, `stdio.h`, `unistd.h`, `sys/uio.h`, `pidns.h`. functions: `print_iov`, `do_call`, `ptr_cast`, `main`. types: `iovec`, `print_iov_arg`, `pid_type`. macros: `in_iovec`, `out_iovec`, `in_iov`, `out_iov`. Source size: 292 lines, 7345 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

`pidns.h` PID namespace setup and translated PID suffix rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_readv_writev.c -->
