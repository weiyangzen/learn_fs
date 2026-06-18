<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime01.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> This tests the timer_settime(2) syscall under various conditions: 1) General initialization: No old_value, no flags 2) Setting a pointer to a itimerspec struct as old_set parameter 3) Using a periodic timer 4) Using absolute time All of these tests are supposed to be successful. This is also regression test for commit: f18ddc13af98 ("alarmtimer: Use EOPNOTSUPP instead of ENOTSUPP") e86fea764991 ("alarmtimer: Return relative times in timer_gettime") The busy loop is intentional. The signal is sent after X seconds of CPU time has been accumulated for the process and thread specific clocks.

Important APIs/types/functions: includes `stdlib.h`, `errno.h`, `time.h`, `signal.h`, `time64_variants.h`, `tst_timer.h`; exercises `syscall`, `time`, `timer_create`, `timer_delete`, `timer_gettime`, `timer_settime`, `times`, `raw syscall path`; defines `clear_signal`, `sighandler`, `setup`, `run`; uses constants `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`, `SIGALRM`.

Control flow centers on `clear_signal`, `sighandler`, `setup`, `run`. The `struct tst_test` registration wires `.test`, `.needs_root`, `.tcnt`, `.test_variants`, `.setup`, `.tags` into the runner. Named case hints include `linux-git`, `syscall with old kernel spec`, `syscall time64 with kernel spec`. Error-path expectations include `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is POSIX timer arming/disarming, absolute versus relative mode, invalid timespec validation, and signal delivery.

Dependencies and integration points: Depends on POSIX timer arming, signal notification, timespec validation, and selected clock support. Direct include dependencies include `stdlib.h`, `errno.h`, `time.h`, `signal.h`, `time64_variants.h`, `tst_timer.h`.

Risks and test signals: Timing assertions can be scheduler-sensitive, especially for short intervals or absolute time. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime01.c -->
