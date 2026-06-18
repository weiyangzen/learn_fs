<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/osf_utimes.c -->
# sources/test-tools/strace/tests/osf_utimes.c

## Purpose

`sources/test-tools/strace/tests/osf_utimes.c` is a C test program in the strace tests tree. It provides Alpha OSF utimes compatibility decoder coverage for legacy utimes argument formatting. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `xutimes.c`. functions: none found in this file. types: `timeval32`. macros: `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `TEST_STRUCT`. direct syscall numbers: `__NR_osf_utimes`. wrapper include: `xutimes.c`. Source size: 26 lines, 534 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `xutimes.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; skip-path coverage for unavailable syscalls, procfs, namespace features, or architecture-specific headers; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/osf_utimes.c -->
