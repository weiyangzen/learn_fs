<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_getfd-yy.c -->
# sources/test-tools/strace/tests/pidfd_getfd-yy.c

## Purpose

`sources/test-tools/strace/tests/pidfd_getfd-yy.c` is a C test program in the strace tests tree. It provides pidfd_getfd decoder coverage for pidfd arguments, target file descriptors, optional fd path and pidfd annotations, and invalid flag handling. The source was read as a complete 5-line file for this report.

## Important APIs, Types, and Functions

includes: `pidfd_getfd.c`. functions: none found in this file. types: none found in this file. macros: `PRINT_PIDFD_PID`, `FD0_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`. wrapper include: `pidfd_getfd.c`. variant settings: enables pidfd fd annotation output. Source size: 5 lines, 167 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `pidfd_getfd.c`. It sets: enables pidfd fd annotation output. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. It uses procfs or `/proc/self/fd` observations for fd path or process metadata decoding. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; fd path tests depend on `/proc/self/fd` and can differ when descriptors are reused or unavailable.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/pidfd_getfd-yy.c -->
