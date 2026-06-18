<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime02.c

Purpose: Ported to new library: 07/2019 Christian Amann <camann@suse.com> This tests basic error handling of the timer_settime(2) syscall: 1) Setting pointer to new settings to NULL -> EINVAL 2) Setting tv_nsec of the itimerspec structure to a negative value -> EINVAL 3) Setting tv_nsec of the itimerspec structure to something larger than NSEC_PER_SEC -> EINVAL 4) Passing an invalid timer -> EINVAL 5) Passing an invalid address for new_value -> EFAULT 6) Passing an invalid address for old_value -> EFAULT This is also regression test for commit: f18ddc13af98 ("alarmtimer: Use EOPNOTSUPP instead of ENOTSUPP") separate description-array to (hopefully) improve readability

Important APIs/types/functions: includes `errno.h`, `time.h`, `time64_variants.h`, `tst_timer.h`; exercises `syscall`, `time`, `timer_create`, `timer_delete`, `timer_settime`, `raw syscall path`; defines `sighandler`, `setup`, `run`; uses constants `EFAULT`, `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`, `SIGALRM`.

Control flow centers on `sighandler`, `setup`, `run`. The `struct tst_test` registration wires `.test`, `.needs_root`, `.tcnt`, `.test_variants`, `.setup`, `.tags` into the runner. Named case hints include `setting new_set pointer to NULL`, `linux-git`, `syscall with old kernel spec`, `syscall time64 with kernel spec`. Error-path expectations include `EFAULT`, `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`.

State and persistence behavior: Runtime state is POSIX timer arming/disarming, absolute versus relative mode, invalid timespec validation, and signal delivery.

Dependencies and integration points: Depends on POSIX timer arming, signal notification, timespec validation, and selected clock support. Direct include dependencies include `errno.h`, `time.h`, `time64_variants.h`, `tst_timer.h`.

Risks and test signals: Timing assertions can be scheduler-sensitive, especially for short intervals or absolute time. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`, `TTERRNO`; checks errno values `EFAULT`, `EINVAL`, `ENOTSUP`, `ENOTSUPP`, `EOPNOTSUPP`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timer_settime/timer_settime02.c -->
