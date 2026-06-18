# sources/test-tools/strace/tests/match.awk

Purpose: `match.awk` is an awk output matcher used by shell-driven tests to compare expected and observed strace lines while preserving controlled regex matching semantics.

Important APIs/types/functions: Complete-read metadata: 33 line(s), 578 byte(s); classification `awk matcher`; functions none visible in this file; syscall markers none visible in this file. Key includes are none visible in this file. Key macros/compile switches are none visible in this file.

Control flow: Input records are processed linearly. Pattern/action rules normalize or match each line and either print transformed records or fail the test when the stream no longer matches expected syscall-output structure.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily none visible in this file. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
