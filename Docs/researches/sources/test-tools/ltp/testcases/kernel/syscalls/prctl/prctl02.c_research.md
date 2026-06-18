<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl02.c

Purpose: - EINVAL when an invalid value is given for option - EINVAL when option is PR_SET_PDEATHSIG & arg2 is not zero or a valid signal number - EINVAL when option is PR_SET_DUMPABLE & arg2 is neither SUID_DUMP_DISABLE nor SUID_DUMP_USER - EFAULT when arg2 is an invalid address - EFAULT when option is PR_SET_SECCOMP & arg2 is SECCOMP_MODE_FILTER & arg3 is an invalid address - EACCES when option is PR_SET_SECCOMP & arg2 is SECCOMP_MODE_FILTER & the process does not have the CAP_SYS_ADMIN capability - EINVAL when option is PR_SET_TIMING & arg2 is not PR_TIMING_STATISTICAL - EINVAL when option is PR_SET_NO_NEW_PRIVS & arg2

Important APIs/types/functions: includes `errno.h`, `signal.h`, `sys/prctl.h`, `linux/filter.h`, `linux/capability.h`, `unistd.h`, `stdlib.h`, `stddef.h`; exercises `prctl`; defines `verify_prctl`, `setup`; uses flags/constants `PR_CAPBSET_DROP`, `PR_CAP_AMBIENT`, `PR_CAP_AMBIENT_CLEAR_ALL`, `PR_CAP_AMBIENT_IS_SET`, `PR_CAP_AMBIENT_LOWER`, `PR_CAP_AMBIENT_RAISE`, `PR_GET_NO_NEW_PRIVS`, `PR_GET_SECCOMP`, `PR_GET_SPECULATION_CTRL`, `PR_GET_THP_DISABLE`, `PR_SET_DUMPABLE`, `PR_SET_NAME`, `PR_SET_NO_NEW_PRIVS`, `PR_SET_PDEATHSIG`.

Control flow centers on `verify_prctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test`, `.caps` into the LTP runner. Error-path expectations include `EACCES`, `EFAULT`, `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `errno.h`, `signal.h`, `sys/prctl.h`, `linux/filter.h`, `linux/capability.h`, `unistd.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_CAP`, `TST_CAP_DROP`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EACCES`, `EFAULT`, `EINVAL`, `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl02.c -->
