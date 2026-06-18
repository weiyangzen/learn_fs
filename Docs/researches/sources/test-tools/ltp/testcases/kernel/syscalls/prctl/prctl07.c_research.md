<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl07.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl07.c

Purpose: Test the PR_CAP_AMBIENT of prctl(2). Reads or changes the ambient capability set of the calling thread, according to the value of arg2, which must be one of the following: - PR_CAP_AMBIENT_RAISE: The capability specified in arg3 is added to the ambient set. The specified capability must already be present in both pE and pI. If we set SECBIT_NO_CAP_AMBIENT_RAISE bit, raise option will be rejected and return EPERM. We also raise a CAP twice. - PR_CAP_AMBIENT_LOWER: The capability specified in arg3 is removed from the ambient set. Even though this cap is not in set, it also should return 0. - PR_CAP_AMBIENT_IS_SET:

Important APIs/types/functions: includes `sys/prctl.h`, `stdlib.h`, `config.h`, `lapi/syscalls.h`, `lapi/prctl.h`, `lapi/securebits.h`, `tst_test.h`; exercises `prctl`; defines `check_cap_raise`, `check_cap_is_set`, `check_cap_lower`, `verify_prctl`, `setup`; uses flags/constants `PR_AMBIENT_CLEAR_ALL`, `PR_CAP_AMBIENT`, `PR_CAP_AMBIENT_CLEAR`, `PR_CAP_AMBIENT_CLEAR_ALL`, `PR_CAP_AMBIENT_IS_SET`, `PR_CAP_AMBIENT_LORWER`, `PR_CAP_AMBIENT_LOWER`, `PR_CAP_AMBIENT_RAISE`, `PR_SET_SECUREBITS`.

Control flow centers on `check_cap_raise`, `check_cap_is_set`, `check_cap_lower`, `verify_prctl`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.needs_root` into the LTP runner. Error-path expectations include `EINVAL`, `EPERM`.

State and persistence behavior: Runtime state is process attributes manipulated by `prctl()`, including name strings, dumpability, death signal, timer slack, seccomp, no-new-privs, and speculation/THP controls depending on the case.

Dependencies and integration points: Depends on Linux `prctl()` option availability, LTP capability/namespace/seccomp helpers, child exec helpers, and architecture/kernel feature probes. Direct include dependencies include `sys/prctl.h`, `stdlib.h`, `config.h`, `lapi/syscalls.h`, `lapi/prctl.h`, `lapi/securebits.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_ASSERT_FILE_STR`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`, `EPERM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/prctl/prctl07.c -->
