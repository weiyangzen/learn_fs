<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64.c -->
# sources/test-tools/strace/tests/prlimit64.c

## Purpose

`sources/test-tools/strace/tests/prlimit64.c` is a C test program in the strace tests tree. It provides prlimit64 decoder coverage for resource limits, success paths, and pid namespace translation variants. The source was read as a complete 111-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `inttypes.h`, `stdio.h`, `stdint.h`, `stdlib.h`, `sys/resource.h`, `unistd.h`, `pidns.h`, `xlat.h`, `xlat/resources.h`. functions: `sprint_rlim`, `main`. types: `xlat_data`. macros: `RETVAL_INJECTED`, `INJ_STR`, `INJECT_RETVAL`. direct syscall numbers: `__NR_prlimit64`. notable constants/xlats: `RLIMIT_AS`. variant settings: uses success or retval injection path. Source size: 111 lines, 2567 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prlimit64`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations. Tail-allocated or heap objects are used to create valid, invalid, and boundary pointers for decoder coverage.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses tail-allocated buffers and deliberately adjacent invalid pointers to test user-memory decoding boundaries. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `pidns.h` PID namespace setup and translated PID suffix rendering; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; PID namespace tests depend on user namespace permissions, procfs visibility, and stable translated PID suffixes; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prlimit64.c -->
