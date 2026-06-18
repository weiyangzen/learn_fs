<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill01.c

Purpose: tgkill() delivers a signal to a specific thread. Test this by installing a SIGUSR1 handler which records the current pthread ID. Start a number of threads in parallel, then one-by-one call tgkill(..., tid, SIGUSR1) and check that the expected pthread ID was recorded. There is no standard way to map pthread -> tid, so we will have the child stash its own tid then notify the parent that the stashed tid is available.

Important APIs/types/functions: includes `pthread.h`, `stdlib.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`; exercises `tgkill`; defines `sigusr1_handler`, `start_thread`, `stop_threads`, `run`, `setup`; uses constants `SIGUSR1`.

Control flow centers on `sigusr1_handler`, `start_thread`, `stop_threads`, `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.cleanup` into the runner. Named case hints include `t:`.

State and persistence behavior: Runtime state is thread-group identity, per-thread signal delivery, and signal handlers used to prove `tgkill()` targets a specific task.

Dependencies and integration points: Depends on raw `tgkill` syscall wrappers, pthread/fork helpers, signal handlers, and current thread-group ids. Direct include dependencies include `pthread.h`, `stdlib.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`.

Risks and test signals: Signal tests are race-prone unless handler setup, target tids, and wait/join ordering are correct. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE2`, `TST_RET`, `TTERRNO`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill01.c -->
