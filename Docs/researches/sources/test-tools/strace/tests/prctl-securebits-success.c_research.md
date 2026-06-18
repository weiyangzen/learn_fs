<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success.c -->
# sources/test-tools/strace/tests/prctl-securebits-success.c

## Purpose

`sources/test-tools/strace/tests/prctl-securebits-success.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-securebits.c`. functions: none found in this file. types: none found in this file. macros: `INJECT_RETVAL`. wrapper include: `prctl-securebits.c`. variant settings: uses success or retval injection path. Source size: 2 lines, 52 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-securebits.c`. It sets: uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-securebits-success.c -->
