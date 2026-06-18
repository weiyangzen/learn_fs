<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo02.c

Purpose: Verify that :manpage:sysinfo(2) returns EFAULT for an invalid address structure.

Important APIs/types/functions: includes `sys/sysinfo.h`, `tst_test.h`; exercises `sysinfo`; defines `setup`, `run`; uses constants `EFAULT`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.setup`, `.test_all` into the runner. Error-path expectations include `EFAULT`.

State and persistence behavior: Runtime state is global memory, swap, process, load, and uptime counters returned in `struct sysinfo`.

Dependencies and integration points: Depends on `sysinfo(2)`, `/proc`-like global accounting consistency, and architecture-compatible `struct sysinfo` layout. Direct include dependencies include `sys/sysinfo.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo02.c -->
