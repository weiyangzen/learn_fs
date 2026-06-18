<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog12.c

Purpose: Verify that syslog(2) system call fails with appropriate error number: 1. EINVAL -- invalid type/command 2. EFAULT -- buffer outside program's accessible address space 3. EINVAL -- NULL buffer argument 4. EINVAL -- length argument set to negative value 5. EINVAL -- console level less than 0 6. EINVAL -- console level greater than 8 7. EPERM -- non-root user

Important APIs/types/functions: includes `errno.h`, `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tst_safe_macros.h`; exercises `syslog`, `raw syscall path`; defines `setup`, `setup_nonroot`, `cleanup_nonroot`, `run`; uses constants `EFAULT`, `EINVAL`, `EPERM`.

Control flow centers on `setup`, `setup_nonroot`, `cleanup_nonroot`, `run`. The `struct tst_test` registration wires `.test`, `.setup`, `.needs_root`, `.tcnt` into the runner. Error-path expectations include `EFAULT`, `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is the kernel log buffer and console log level, requiring privileged reads or size queries depending on the command.

Dependencies and integration points: Depends on privileged kernel log access, `klogctl`/syslog command semantics, and kernel log buffer availability. Direct include dependencies include `errno.h`, `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tst_safe_macros.h`.

Risks and test signals: Kernel log access is security-policy-sensitive; tests may fail or skip under restricted dmesg settings. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EFAULT`, `EINVAL`, `EPERM`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/syslog/syslog12.c -->
