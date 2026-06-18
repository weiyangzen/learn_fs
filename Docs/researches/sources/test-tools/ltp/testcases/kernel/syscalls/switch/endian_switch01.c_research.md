<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/switch/endian_switch01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/switch/endian_switch01.c

Purpose: Test little-endian mode switch system call. Requires a 64-bit processor that supports little-endian mode,such as POWER6. Make minimal call to 0x1ebe. If we get ENOSYS then syscall is not available, likely because of: commit 727f13616c45 ("powerpc: Disable the fast-endian switch syscall by default") If we get any other outcome, including crashes with various signals, then we assume syscall is available and carry on with the test. HAVE_GETAUXVAL

Important APIs/types/functions: includes `errno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `elf.h`, `sys/types.h`, `sys/wait.h`, `tst_test.h`; exercises `syscall`, `raw syscall path`; defines `check_le_switch_supported`, `test_le_switch`, `endian_test`; uses constants `AT_HWCAP`, `ENOSYS`.

Control flow centers on `check_le_switch_supported`, `test_le_switch`, `endian_test`. The `struct tst_test` registration wires `.test_all` into the runner. Error-path expectations include `ENOSYS`.

State and persistence behavior: Runtime state is PowerPC endian execution mode in a forked child and whether the kernel/CPU supports little-endian switching.

Dependencies and integration points: Depends on PowerPC-specific `syscall(__NR_switch_endian)`, fork/wait helpers, and architecture guards that skip unsupported platforms. Direct include dependencies include `errno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `elf.h`, `sys/types.h`.

Risks and test signals: Architecture guards are essential because the syscall is PowerPC-specific and child crashes are an expected way to isolate unsupported mode changes. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_TEST_TCONF`; checks errno values `ENOSYS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/switch/endian_switch01.c -->
