<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff02.c

Purpose: This test case checks whether swapoff(2) system call returns 1. EINVAL when the path does not exist 2. ENOENT when the path exists but is invalid 3. EPERM when user is not a superuser

Important APIs/types/functions: includes `errno.h`, `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapoff`, `raw syscall path`; defines `setup01`, `cleanup01`, `verify_swapoff`, `setup`; uses constants `EINVAL`, `ENOENT`, `EPERM`.

Control flow centers on `setup01`, `cleanup01`, `verify_swapoff`, `setup`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.test`, `.tcnt`, `.setup` into the runner. Named case hints include `path does not exist`, `Invalid file`, `Permission denied`. Error-path expectations include `EINVAL`, `ENOENT`, `EPERM`.

State and persistence behavior: Runtime state is swap activation state for temporary swapfiles, user credentials, mounted filesystem support for swapfiles, and cleanup that must leave no active swap area behind.

Dependencies and integration points: Depends on swapfile creation helpers, raw `swapoff` syscall wrappers when libc lacks the call, root privileges, mounted filesystem support, and credential switching for permission failures. Direct include dependencies include `errno.h`, `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`.

Risks and test signals: Leaking active swapfiles or running on filesystems that cannot host swapfiles can affect the host, so setup/cleanup ordering is critical. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`; checks errno values `EINVAL`, `ENOENT`, `EPERM`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff02.c -->
