<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat01.c

Purpose: Check that ustat() succeeds given correct parameters. Find a valid device number

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `unistd.h`, `errno.h`, `sys/types.h`, `sys/stat.h`, `lapi/syscalls.h`, `lapi/ustat.h`; exercises `ustat`, `raw syscall path`; defines `run`, `setup`; uses constants `EINVAL`.

Control flow centers on `run`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.skip_filesystems`, `.tags` into the runner. Named case hints include `btrfs`, `known-fail`. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is filesystem statistics addressed by a device number; the interface is obsolete and filesystem-dependent.

Dependencies and integration points: Depends on obsolete `ustat` syscall availability, `struct ustat` definitions from libc or lapi, and a valid device number from `stat("/")`. Direct include dependencies include `config.h`, `tst_test.h`, `unistd.h`, `errno.h`, `sys/types.h`, `sys/stat.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TST_TEST_TCONF`, `TTERRNO`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/ustat/ustat01.c -->
