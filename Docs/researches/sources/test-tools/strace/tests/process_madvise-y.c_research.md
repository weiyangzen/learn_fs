<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise-y.c -->
# sources/test-tools/strace/tests/process_madvise-y.c

## Purpose

`sources/test-tools/strace/tests/process_madvise-y.c` is a C test program in the strace tests tree. It provides strace test-suite coverage for `process_madvise` syscall or printer behavior. The source was read as a complete 5-line file for this report.

## Important APIs, Types, and Functions

includes: `process_madvise.c`. functions: none found in this file. types: none found in this file. macros: `PRINT_PATHS`, `FD0_PATH`. wrapper include: `process_madvise.c`. variant settings: enables path tracing or decoded path output; enables pidfd fd annotation output. Source size: 5 lines, 105 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_madvise.c`. It sets: enables path tracing or decoded path output; enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_madvise-y.c -->
