<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime01.c

Purpose: Test Description: Verify that the system call stime() successfully sets the system's idea of date and time if invoked by "root" user. Expected Result: stime() should succeed to set the system data/time to the specified time. 07/2001 John George -Ported

Important APIs/types/functions: includes `time.h`, `sys/time.h`, `tst_test.h`, `stime_var.h`; exercises `stime`, `time`; defines `run`, `setup`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test_all`, `.needs_root`, `.setup`, `.test_variants` into the runner.

State and persistence behavior: Runtime state is the system wall clock. The tests deliberately change or attempt to change global system time and rely on privilege transitions plus libc/raw syscall dispatch.

Dependencies and integration points: Depends on `stime_var.h`, libc `stime()` when available, raw `__NR_stime` fallback, root privileges for success paths, and nobody-user credential switching for EPERM paths. Direct include dependencies include `time.h`, `sys/time.h`, `tst_test.h`, `stime_var.h`.

Risks and test signals: Changing system time is globally disruptive; success tests require root and failure tests rely on clean credential transitions and platform support for obsolete `stime()`. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/stime/stime01.c -->
