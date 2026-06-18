# sources/test-tools/strace/tests/caps.awk

Purpose: `caps.awk` post-processes strace test output for capability-related expected lines, normalizing symbolic capability sets for the matching `.c` test variant.

Important APIs/types/functions: this is AWK program text rather than C. It uses pattern/action rules, regular-expression matching, field variables, and `print`/substitution operations to reshape test output. Representative regex/action fragments include `bin`, `\\* _LINUX_CAPABILITY_VERSION_\\?\\?\\? \\*`.

Control flow: AWK scans strace output line by line, applies the first matching capability-format rules, emits normalized lines, and leaves non-target input unchanged or filtered according to the script body. State is limited to AWK variables for the current record; there is no persistent filesystem state.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 37 lines, 1893 bytes, sha256 prefix `7f1083f025f9`.
