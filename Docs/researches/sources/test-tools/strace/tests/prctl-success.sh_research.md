<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-success.sh -->
# sources/test-tools/strace/tests/prctl-success.sh

## Purpose

`sources/test-tools/strace/tests/prctl-success.sh` is a shell harness in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 67-line file for this report.

## Important APIs, Types, and Functions

includes: none found in this file. functions: none found in this file. types: none found in this file. macros: none found in this file. variant settings: uses success or retval injection path. Source size: 67 lines, 1894 bytes.

## Control Flow

The shell harness sources the strace test framework, configures command-line options or injection parameters, runs the compiled test binary under strace, and compares the trace against generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness. Compile-time macros select the output mode, so the same base control flow can persist as several generated test binaries.

## Dependencies and Integration Points

POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`; the generated strace test matrix (`gen_tests.in`/Makefile rules) that builds wrapper variants from the same base source.

## Risks and Edge Cases

wrapper and base-file macro drift can silently change expected output coverage; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; variant comparison across raw, abbreviated, verbose, `-y`, `-yy`, `-P`, or pid namespace modes; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-success.sh -->
