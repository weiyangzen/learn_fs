<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/personality.c -->
# sources/test-tools/strace/tests/personality.c

## Purpose

`sources/test-tools/strace/tests/personality.c` is a C test program in the strace tests tree. It provides personality syscall decoder coverage for personality flags and xlat output modes. The source was read as a complete 125-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `stdio.h`, `sys/personality.h`. functions: `main`. types: none found in this file. macros: `linux_type_str`, `good_type_str`, `bad_type_str`, `good_flags_str`, `bad_flags_str`, `good_bad_flags_str`. Source size: 125 lines, 4023 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/personality.c -->
