<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open_nonverbose.c -->
# sources/test-tools/strace/tests/perf_event_open_nonverbose.c

## Purpose

`sources/test-tools/strace/tests/perf_event_open_nonverbose.c` is a C test program in the strace tests tree. It provides perf_event_open decoder coverage for struct perf_event_attr, perf flags, abbreviated versus verbose attribute printing, and unknown or version-dependent fields. The source was read as a complete 85-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `limits.h`, `stdio.h`, `unistd.h`, `linux/perf_event.h`, `xlat.h`, `xlat/perf_event_open_flags.h`. functions: `printaddr`, `main`. types: `perf_event_attr`. macros: `LONG_STR_PREFIX`. direct syscall numbers: `__NR_perf_event_open`. notable constants/xlats: `PERF_TYPE_HARDWARE`, `PERF_FLAG_FD_NO_GROUP`, `PERF_FLAG_FD_OUTPUT`, `PERF_FLAG_PID_CGROUP`, `PERF_FLAG_FD_CLOEXEC`. variant settings: uses non-verbose or unabbreviated compile-time mode. Source size: 85 lines, 2026 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_perf_event_open`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/perf_event_open_nonverbose.c -->
