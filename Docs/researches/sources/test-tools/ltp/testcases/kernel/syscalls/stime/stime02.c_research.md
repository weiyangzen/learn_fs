<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime02.c

Purpose: Test Description: Verify that the system call stime() fails to set the system's idea of data and time if invoked by "non-root" user. Expected Result: stime() should fail with return value -1 and set errno to EPERM. 07/2001 John George -Ported

Important APIs/types/functions: includes `sys/types.h`, `errno.h`, `time.h`, `pwd.h`, `tst_test.h`, `stime_var.h`; exercises `stime`, `time`; defines `run`, `setup`; uses constants `EPERM`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.needs_root`, `.test_variants` into the runner. Error-path expectations include `EPERM`.

State and persistence behavior: Runtime state is the system wall clock. The tests deliberately change or attempt to change global system time and rely on privilege transitions plus libc/raw syscall dispatch.

Dependencies and integration points: Depends on `stime_var.h`, libc `stime()` when available, raw `__NR_stime` fallback, root privileges for success paths, and nobody-user credential switching for EPERM paths. Direct include dependencies include `sys/types.h`, `errno.h`, `time.h`, `pwd.h`, `tst_test.h`, `stime_var.h`.

Risks and test signals: Changing system time is globally disruptive; success tests require root and failure tests rely on clean credential transitions and platform support for obsolete `stime()`. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EPERM`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime02.c -->
