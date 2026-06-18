<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents02.c

Purpose: written by Wayne Boyer Verify that: - getdents() fails with EBADF if file descriptor fd is invalid - getdents() fails with EINVAL if result buffer is too small - getdents() fails with ENOTDIR if file descriptor does not refer to a directory - getdents() fails with ENOENT if directory was unlinked() - getdents() fails with EFAULT if argument points outside the calling process's address space

Important APIs/types/functions: includes `errno.h`, `tst_test.h`, `getdents.h`; touches `getdents`; defines `setup`, `run`; uses LTP safe helpers such as `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_RMDIR`.

Control flow centers on `setup`, `run`. The `struct tst_test` registration wires `.test`, `.setup`, `.tcnt`, `.test_variants`, `.needs_root`, `.mount_device` into the LTP runner. Error-path assertions cover `EBADF`, `EFAULT`, `EINVAL`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is a directory file descriptor and the kernel getdents buffer containing linux_dirent records.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `errno.h`, `tst_test.h`, `getdents.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_FAIL2`. Expected errno values include `EBADF`, `EFAULT`, `EINVAL`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getdents/getdents02.c -->
