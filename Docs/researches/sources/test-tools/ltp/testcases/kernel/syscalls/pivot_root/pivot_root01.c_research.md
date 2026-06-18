<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/pivot_root01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/pivot_root01.c

Purpose: Test consists of a series of steps that allow pivot_root to succeed, which is run when param is NORMAL. All other values tweak one of the steps to induce a failure, and check the errno is as expected. EBUSY new_root or put_old are on the current root file system EINVAL put_old is not underneath new_root Note: if put_old and new_root are on the same fs, pivot_root fails with EBUSY before testing reachability

Important APIs/types/functions: includes `config.h`, `errno.h`, `lapi/syscalls.h`, `sched.h`, `stdlib.h`, `tst_test.h`, `lapi/mount.h`, `sys/capability.h`; exercises `pivot_root`, `mount`, `raw syscall path`; defines `drop_cap_sys_admin`, `run`, `setup`.

Control flow centers on `drop_cap_sys_admin`, `run`, `setup`. The `struct tst_test` registration wires `.test`, `.tcnt`, `.needs_tmpdir`, `.needs_root`, `.forks_child`, `.setup` into the LTP runner. Error-path expectations include `EBUSY`, `EINVAL`, `ENOTDIR`, `EPERM`.

State and persistence behavior: Runtime state is the process mount namespace root/cwd plus old-root and new-root mountpoints that must be bind-mounted and later unwound.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `config.h`, `errno.h`, `lapi/syscalls.h`, `sched.h`, `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_RET`, `TST_TEST_TCONF`, `TTERRNO`; checks errno values `EBUSY`, `EINVAL`, `ENOTDIR`, `EPERM`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pivot_root/pivot_root01.c -->
