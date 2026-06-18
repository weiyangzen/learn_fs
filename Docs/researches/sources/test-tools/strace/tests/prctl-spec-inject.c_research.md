<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-spec-inject.c -->
# sources/test-tools/strace/tests/prctl-spec-inject.c

## Purpose

`sources/test-tools/strace/tests/prctl-spec-inject.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 165-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `errno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `do_prctl`, `main`. types: none found in this file. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_SET_SPECULATION_CTRL`, `PR_GET_SPECULATION_CTRL`, `PR_SPEC_STORE_BYPASS`, `PR_SPEC_INDIRECT_BRANCH`, `PR_SPEC_L1D_FLUSH`, `PR_SPEC_NOT_AFFECTED`, `PR_SPEC_PRCTL`, `PR_SPEC_ENABLE`, `PR_SPEC_FORCE_DISABLE`, `PR_SPEC_DISABLE_NOEXEC`, `PR_SPEC_`. variant settings: uses success or retval injection path. Source size: 165 lines, 4237 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-spec-inject.c -->
