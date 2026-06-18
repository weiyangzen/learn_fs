<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat02.c

Purpose: Test whether ustat(2) system call returns appropriate error number for invalid dev_t parameter and for bad address paramater. Find a valid device number

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `unistd.h`, `errno.h`, `sys/stat.h`, `sys/types.h`, `lapi/syscalls.h`, `lapi/ustat.h`; exercises `ustat`, `raw syscall path`; defines `run`, `setup`; uses constants `EFAULT`, `EINVAL`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test`, `.setup`, `.tcnt`, `.skip_filesystems`, `.tags` into the runner. Named case hints include `Invalid parameter`, `Bad address`, `btrfs`, `known-fail`. Error-path expectations include `EFAULT`, `EINVAL`.

State and persistence behavior: Runtime state is filesystem statistics addressed by a device number; the interface is obsolete and filesystem-dependent.

Dependencies and integration points: Depends on obsolete `ustat` syscall availability, `struct ustat` definitions from libc or lapi, and a valid device number from `stat("/")`. Direct include dependencies include `config.h`, `tst_test.h`, `unistd.h`, `errno.h`, `sys/stat.h`, `sys/types.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TST_TEST_TCONF`, `TST_TOTAL`, `TTERRNO`; checks errno values `EFAULT`, `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat02.c -->
