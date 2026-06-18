<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait403.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait403.c

Purpose: regression test that `wait4(INT_MIN, ...)` is rejected safely with `ESRCH` rather than triggering signed negation undefined behavior in process-group lookup.

Important APIs/types/functions: `run()` calls `wait4(INT_MIN, &status, 0, &rusage)` and expects `ESRCH`. Metadata enables kernel taint checks and tags Linux commit `dd83c161fbcc`.

Control flow/state: single negative syscall call with no children. The special value exercises the pid-negation edge case.

Dependencies/integration: relies on LTP taint detection for warning/oops side effects and standard `wait4` ABI.

Risks/test signals: wrong errno or kernel taint indicates the regression path. On kernels without the fix but without UBSAN, behavior may still be `ECHILD`, which this test treats as failure.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait4/wait403.c -->
