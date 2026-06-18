# sources/test-tools/strace/tests/kill-on-exit.sh

Purpose: `kill-on-exit.sh` is an executable shell test harness for strace process-kill behavior at tracee exit. It orchestrates helper processes, invokes the test suite shell utilities, and checks that strace tears down or reports processes with the expected status rather than leaving children running.

Important APIs/types/functions: Complete-read metadata: 94 line(s), 2208 byte(s); classification `shell harness`; functions none visible in this file; syscall markers none visible in this file. Key includes are none visible in this file. Key macros/compile switches are none visible in this file.

Control flow: The shell script sources the common init logic, prepares a child/tracee scenario, runs strace with the requested exit/kill options, waits for process completion, and compares observed behavior with expected status/output. Its branches mainly handle unsupported features and cleanup.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. process or thread state is intentionally created and then synchronized with waits, joins, or signal handlers. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily none visible in this file. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: main risk is expected-output drift when shared testsuite helpers or kernel headers change.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful syscall execution and exact expected-output matching. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
