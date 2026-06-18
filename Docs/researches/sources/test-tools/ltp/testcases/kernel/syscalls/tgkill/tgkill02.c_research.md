<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill02.c

Purpose: tgkill() should fail with EAGAIN when RLIMIT_SIGPENDING is reached with a real-time signal. Test this by starting a child thread with SIGRTMIN blocked and a limit of 0 pending signals, then attempting to deliver SIGRTMIN from the parent thread.

Important APIs/types/functions: includes `pthread.h`, `signal.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`; exercises `tgkill`, `time`; defines `run`; uses constants `EAGAIN`, `SIGRTMIN`, `SIG_BLOCK`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner. Error-path expectations include `EAGAIN`.

State and persistence behavior: Runtime state is thread-group identity, per-thread signal delivery, and signal handlers used to prove `tgkill()` targets a specific task.

Dependencies and integration points: Depends on raw `tgkill` syscall wrappers, pthread/fork helpers, signal handlers, and current thread-group ids. Direct include dependencies include `pthread.h`, `signal.h`, `tst_safe_pthread.h`, `tst_test.h`, `tgkill.h`.

Risks and test signals: Signal tests are race-prone unless handler setup, target tids, and wait/join ordering are correct. Test signals: reports through `TBROK`, `TFAIL`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EAGAIN`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tgkill/tgkill02.c -->
