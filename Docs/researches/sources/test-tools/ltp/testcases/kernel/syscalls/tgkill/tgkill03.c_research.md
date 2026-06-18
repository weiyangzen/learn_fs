<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill03.c

Purpose: Test simple tgkill() error cases.

Important APIs/types/functions: includes `pthread.h`, `pwd.h`, `stdio.h`, `sys/types.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`; exercises `tgkill`; defines `setup`, `cleanup`, `run`; uses constants `EINVAL`, `ENOENT`, `ESRCH`, `SIGUSR1`, `SIG_BLOCK`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.cleanup`, `.test` into the runner. Named case hints include `Invalid tgid`, `Invalid tid`, `Invalid signal`, `Defunct tid`, `Defunct tgid`, `Valid tgkill call`. Error-path expectations include `EINVAL`, `ENOENT`, `ESRCH`.

State and persistence behavior: Runtime state is thread-group identity, per-thread signal delivery, and signal handlers used to prove `tgkill()` targets a specific task.

Dependencies and integration points: Depends on raw `tgkill` syscall wrappers, pthread/fork helpers, signal handlers, and current thread-group ids. Direct include dependencies include `pthread.h`, `pwd.h`, `stdio.h`, `sys/types.h`, `tst_safe_pthread.h`, `tst_test.h`.

Risks and test signals: Signal tests are race-prone unless handler setup, target tids, and wait/join ordering are correct. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_ERR`, `TST_RET`, `TST_RETRY_FN_EXP_BACKOFF`, `TTERRNO`; checks errno values `EINVAL`, `ENOENT`, `ESRCH`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill03.c -->
