<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid_common.h

Purpose: shared harness for the older multi-child `waitpid` tests. It centralizes child pid storage, coordinator process setup, cleanup, checkpoint-based child release, and verification of returned pids/status.

Important APIs/types/functions: `MAXKIDS` is 8. `waitpid_setup()` maps shared pid storage. `waitpid_cleanup()` kills recorded children and the coordinator then unmaps. `waitpid_test()` forks the coordinator and reaps it. `do_exit(stop)` waits on a checkpoint, optionally sends itself `SIGSTOP`, and exits with status 3. `waitpid_ret_test()` checks return value and errno. `reap_children()` loops on `waitpid()`, handles `EINTR`, expects final `ECHILD`, continues stopped children, validates returned pids against the expected array, and checks exit status 3.

Control flow/state: the including C file supplies `do_child_1()`, which creates the concrete child topology. Shared mmap lets the parent cleanup path know child pids created by the coordinator process.

Dependencies/integration: depends on LTP safe mmap/fork/checkpoint wrappers and standard wait status macros. It is header-included into multiple standalone tests, so all globals are `static` except `waitpid_ret_test()`.

Risks/test signals: because cleanup kills all nonzero recorded pids, stale pid reuse would be dangerous if tests ran long after children exit; the reaper zeros pids when consumed to reduce that risk. Failures are reported at the exact invariant: errno, unexpected pid, abnormal exit, wrong exit code, or unreaped child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid_common.h -->
