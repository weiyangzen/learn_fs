<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo01.c

Purpose: Verify that :manpage:`sysinfo(2)` succeeds to get the system information and fills the structure passed. We do sanity checks on the returned values, either comparing it againts values from /proc/ files or by checking that the values are in sane e.g. free RAM <= total RAM. Compare loads with tolerance

Important APIs/types/functions: includes `stdlib.h`, `math.h`, `sys/sysinfo.h`, `tst_test.h`; exercises `sysinfo`; defines `run`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the runner.

State and persistence behavior: Runtime state is global memory, swap, process, load, and uptime counters returned in `struct sysinfo`.

Dependencies and integration points: Depends on `sysinfo(2)`, `/proc`-like global accounting consistency, and architecture-compatible `struct sysinfo` layout. Direct include dependencies include `stdlib.h`, `math.h`, `sys/sysinfo.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_EXP_EQ_LU`, `TST_EXP_LE_LU`, `TST_EXP_PASS`, `TST_KB`, `TST_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo01.c -->
