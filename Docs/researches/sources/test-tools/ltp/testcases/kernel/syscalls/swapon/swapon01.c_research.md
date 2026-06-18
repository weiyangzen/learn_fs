<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon01.c

Purpose: Checks that swapon() succeds with swapfile. Testing on all filesystems which support swap file.

Important APIs/types/functions: includes `unistd.h`, `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapon`, `raw syscall path`; defines `verify_swapon`, `setup`.

Control flow centers on `verify_swapon`, `setup`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.needs_root`, `.all_filesystems`, `.test_all`, `.timeout`, `.setup` into the runner. Named case hints include `memory`.

State and persistence behavior: Runtime state is active swap areas, `/proc/meminfo` accounting, cgroup memory limits where present, temporary swapfile contents, and the kernel-wide maximum number of swapfiles.

Dependencies and integration points: Depends on swapfile helpers, cgroup/meminfo helpers for memory-pressure checks, root privileges, mounted filesystem support, and reliable cleanup through `swapoff()`. Direct include dependencies include `unistd.h`, `errno.h`, `stdlib.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`.

Risks and test signals: Swap tests can perturb host memory behavior and hit kernel-global swap limits; cleanup failures leave persistent system state. Test signals: reports through `TBROK`, `TERRNO`, `TINFO`, `TST_EXP_PASS`, `TST_PASS`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon01.c -->
