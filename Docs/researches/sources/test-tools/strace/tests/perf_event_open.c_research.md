<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open.c -->
# sources/test-tools/strace/tests/perf_event_open.c

## Purpose

`sources/test-tools/strace/tests/perf_event_open.c` is a C test program in the strace tests tree. It provides perf_event_open decoder coverage for struct perf_event_attr, perf flags, abbreviated versus verbose attribute printing, and unknown or version-dependent fields. The source was read as a complete 732-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `inttypes.h`, `limits.h`, `stddef.h`, `stdio.h`, `stdlib.h`, `string.h`, `unistd.h`, `linux/perf_event.h`, `xlat.h`, `xlat/perf_event_open_flags.h`. functions: `printaddr`, `print_event_attr`, `main`. types: `pea_flags`, `perf_event_attr`, `strval64`, `strval32`, `strival32`. macros: `LONG_STR_PREFIX`, `PRINT_FLAG`, `ATTR_REC`, `BRANCH_TYPE_ALL`. direct syscall numbers: `__NR_perf_event_open`. notable constants/xlats: `PERF_ATTR_SIZE_VER0`, `PERF_ATTR_SIZE_`, `PERF_TYPE_BREAKPOINT`, `PERF_SAMPLE_BRANCH_STACK`, `PERF_SAMPLE_STACK_USER`, `PERF_SAMPLE_BRANCH_USER`, `PERF_SAMPLE_BRANCH_KERNEL`, `PERF_SAMPLE_BRANCH_HV`, `PERF_SAMPLE_BRANCH_ANY`, `PERF_SAMPLE_BRANCH_ANY_CALL`, `PERF_SAMPLE_BRANCH_ANY_RETURN`, `PERF_SAMPLE_BRANCH_IND_CALL`, `PERF_SAMPLE_BRANCH_ABORT_TX`, `PERF_SAMPLE_BRANCH_IN_TX`, `PERF_SAMPLE_BRANCH_NO_TX`, `PERF_SAMPLE_BRANCH_COND`, `PERF_SAMPLE_BRANCH_CALL_STACK`, `PERF_SAMPLE_BRANCH_IND_JUMP`. Source size: 732 lines, 19583 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_perf_event_open`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; expected xlat rendering for known constants plus unknown numeric fallback cases; resource cleanup checks for children, pipes, fds, and allocated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open.c -->
