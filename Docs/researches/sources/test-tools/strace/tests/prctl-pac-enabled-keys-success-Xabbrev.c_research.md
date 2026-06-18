<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xabbrev.c -->
# sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xabbrev.c

## Purpose

`sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xabbrev.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 2-line file for this report.

## Important APIs, Types, and Functions

includes: `prctl-pac-enabled-keys-success.c`. functions: none found in this file. types: none found in this file. macros: `XLAT_ABBREV`. wrapper include: `prctl-pac-enabled-keys-success.c`. variant settings: compiled with abbreviated xlat rendering; uses success or retval injection path. Source size: 2 lines, 66 bytes.

## Control Flow

This file is primarily a compile-time variant wrapper around `prctl-pac-enabled-keys-success.c`. It sets: compiled with abbreviated xlat rendering; uses success or retval injection path. Runtime control flow is supplied by the included base test; this wrapper changes decoder formatting, injected return behavior, pid namespace handling, or fd annotation expectations without duplicating the driver.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

`xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-pac-enabled-keys-success-Xabbrev.c -->
