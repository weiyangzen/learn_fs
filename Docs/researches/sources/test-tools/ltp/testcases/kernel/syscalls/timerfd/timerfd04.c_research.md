<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd04.c

Purpose: Test that timerfd adds correctly an offset with absolute expiration time. After a call to unshare(CLONE_NEWTIME) a new timer namespace is created, the process that has called the unshare() can adjust offsets for CLOCK_MONOTONIC and CLOCK_BOOTTIME for its children by writing to the '/proc/self/timens_offsets'.

Important APIs/types/functions: includes `stdlib.h`, `time64_variants.h`, `tst_safe_clocks.h`, `tst_safe_timerfd.h`, `tst_timer.h`, `lapi/sched.h`; exercises `syscall`, `time`, `timerfd_settime`, `unshare`; defines `setup`, `verify_timerfd`; uses constants `CLOCK_BOOTTIME`, `CLOCK_MONOTONIC`, `CLONE_NEWTIME`, `TFD_TIMER_ABSTIME`.

Control flow centers on `setup`, `verify_timerfd`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.test_variants`, `.setup`, `.needs_root`, `.needs_kconfigs` into the runner. Named case hints include `CONFIG_TIME_NS=y`, `syscall with old kernel spec`, `syscall time64 with kernel spec`.

State and persistence behavior: Runtime state is timer file descriptors, expiration counters read from them, clock ids, flags, and `timerfd_settime()`/`gettime()` state.

Dependencies and integration points: Depends on `timerfd_create/gettime/settime`, raw syscall wrappers, clock ids, read semantics for expiration counters, and kernel support for newer flags. Direct include dependencies include `stdlib.h`, `time64_variants.h`, `tst_safe_clocks.h`, `tst_safe_timerfd.h`, `tst_timer.h`, `lapi/sched.h`.

Risks and test signals: Timerfd tests are sensitive to clock availability, blocking reads, and exact expiration counts under scheduler delay. Test signals: reports through `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/timerfd/timerfd04.c -->
