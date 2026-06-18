<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff01.c

Purpose: Check that swapoff() succeeds.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapoff`, `raw syscall path`; defines `verify_swapoff`, `setup`.

Control flow centers on `verify_swapoff`, `setup`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.test_all`, `.timeout`, `.setup` into the runner.

State and persistence behavior: Runtime state is swap activation state for temporary swapfiles, user credentials, mounted filesystem support for swapfiles, and cleanup that must leave no active swap area behind.

Dependencies and integration points: Depends on swapfile creation helpers, raw `swapoff` syscall wrappers when libc lacks the call, root privileges, mounted filesystem support, and credential switching for permission failures. Direct include dependencies include `unistd.h`, `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`.

Risks and test signals: Leaking active swapfiles or running on filesystems that cannot host swapfiles can affect the host, so setup/cleanup ordering is critical. Test signals: reports through `TERRNO`, `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapoff/swapoff01.c -->
