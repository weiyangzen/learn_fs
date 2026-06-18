# sources/test-tools/strace/tests/lsm_list_modules-success.c

Purpose: `lsm_list_modules-success.c` is a thin compile-time variant that includes `lsm_list_modules.c` after setting `INJECT_RETVAL`. It exists so the same base test body can be built under a different strace mode, path-decoding mode, pid-namespace mode, injected-return mode, or descriptor-decode mode without duplicating the base test source.

Important APIs/types/functions: Complete-read metadata: 2 line(s), 52 byte(s); classification `compile-time variant wrapper`; functions none visible in this file; syscall markers none visible in this file. Key includes are `lsm_list_modules.c`. Key macros/compile switches are `INJECT_RETVAL`.

Control flow: Preprocessor control flow is the whole file: define mode macros, include the base `.c` file, and let that base file compile with altered constants/branches. Runtime control flow is inherited entirely from the included source.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. state is intentionally transient and limited to local variables plus kernel return values. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `lsm_list_modules.c`. Important compile-time knobs are `INJECT_RETVAL`. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: standard testsuite helper APIs.

Risks: injected success paths must not be confused with real kernel support.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 0 explicit print call(s). Strong signals: successful compilation of the included base source with variant macros. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
