# sources/test-tools/strace/tests/clock.in

Purpose: `clock.in` is a test generator input table. It enumerates clock-related syscall test instances that the strace test build expands into concrete tests.

Important APIs/types/functions: this file is consumed by the strace test generator rather than compiled directly. It has 5 non-comment input rows; representative rows are `clock_adjtime	-a37`, `clock_adjtime64	-a39`, `clock_nanosleep`, `clock_xettime	-a36`, `clock_xettime64	-a39`.

Control flow: the build/test generator reads each row, expands it into a concrete clock test target, and wires that target to the relevant common C implementation. State is static source metadata only; persistence is the generated test list in the build tree.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 5 lines, 96 bytes, sha256 prefix `f5a86691d0ad`.
