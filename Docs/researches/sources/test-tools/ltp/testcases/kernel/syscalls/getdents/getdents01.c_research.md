<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents01.c

Purpose: written by Wayne Boyer Basic getdents() test that checks if directory listing is correct and complete.

Important APIs/types/functions: includes `tst_test.h`, `getdents.h`, `stdlib.h`; touches `getdents`; defines `reset_flags`, `check_flags`, `set_flag`, `run`, `setup`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_SYMLINK`.

Control flow centers on `reset_flags`, `check_flags`, `set_flag`, `run`, `setup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.test_variants`, `.needs_root`, `.mount_device` into the LTP runner. Error-path assertions cover `ENOSYS`.

State and persistence behavior: Runtime state is a directory file descriptor and the kernel getdents buffer containing linux_dirent records.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `getdents.h`, `stdlib.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`. Expected errno values include `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents01.c -->
