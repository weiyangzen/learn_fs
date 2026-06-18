<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_writev.c -->
# sources/test-tools/strace/tests/process_vm_writev.c

## Purpose

`sources/test-tools/strace/tests/process_vm_writev.c` is a C test program in the strace tests tree. It provides process_vm_readv/process_vm_writev decoder coverage for cross-process iovec arguments, PID rendering, string previews, invalid counts, and shared read/write formatting. The source was read as a complete 18-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `process_vm_readv_writev.c`. functions: none found in this file. types: none found in this file. macros: `OP`, `OP_NR`, `OP_STR`, `OP_WR`. direct syscall numbers: `__NR_process_vm_writev`. wrapper include: `process_vm_readv_writev.c`. Source size: 18 lines, 380 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `process_vm_readv_writev.c`. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/process_vm_writev.c -->
