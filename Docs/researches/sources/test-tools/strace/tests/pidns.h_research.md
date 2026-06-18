<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidns.h -->
# sources/test-tools/strace/tests/pidns.h

## Purpose

`sources/test-tools/strace/tests/pidns.h` is a shared header in the strace tests tree. It provides shared pid namespace support header used by strace tests that need stable printing of translated PIDs, pid types, and pid namespace leaders. The source was read as a complete 57-line file for this report.

## Important APIs, Types, and Functions

includes: `sys/types.h`. functions: `pidns_print_leader`, `pidns_pid2str`, `check_ns_ioctl`, `pidns_test_init`. types: `pid_type`. macros: `STRACE_PIDNS_H`, `PIDNS_TEST_INIT`. variant settings: enables pid namespace translation output. Source size: 57 lines, 1321 bytes.

## Control Flow

There is no standalone runtime flow in this header. It declares macros, helpers, or shared types that the compiled C tests use to normalize PID namespace setup and expected output rendering.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It manipulates live kernel objects such as file descriptors, pipes, pidfds, process IDs, signal info, or child exit status. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

The file integrates with the strace test build and comparison harness through local includes and generated expected-output rules.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; signal, child-process, and job-control paths have ordering and cleanup risks if wait/close/exit synchronization changes.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidns.h -->
