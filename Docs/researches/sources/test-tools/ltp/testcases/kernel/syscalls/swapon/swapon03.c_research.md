<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon03.c

Purpose: Created by <rsalveti@linux.vnet.ibm.com> Test checks whether :manpage:`swapon(2)` system call returns EPERM when the maximum number of swap files are already in use. NOTE: test does not try to calculate MAX_SWAPFILES from the internal kernel implementation, instead make sure at least 15 swaps were created before the maximum of swaps was reached. MAX_SWAPFILES from the internal kernel implementation is currently <23, 29>, depending on kernel configuration (see man swapon(2)). Chose small enough value for future changes. Create the swapfile

Important APIs/types/functions: includes `stdio.h`, `errno.h`, `stdlib.h`, `sys/wait.h`, `sys/swap.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapoff`, `swapon`; defines `setup_swap`, `check_and_swapoff`, `clean_swap`, `verify_swapon`, `setup`, `cleanup`; uses constants `EPERM`.

Control flow centers on `setup_swap`, `check_and_swapoff`, `clean_swap`, `verify_swapon`, `setup`, `cleanup`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.test_all`, `.setup`, `.cleanup` into the runner. Error-path expectations include `EPERM`.

State and persistence behavior: Runtime state is active swap areas, `/proc/meminfo` accounting, cgroup memory limits where present, temporary swapfile contents, and the kernel-wide maximum number of swapfiles.

Dependencies and integration points: Depends on swapfile helpers, cgroup/meminfo helpers for memory-pressure checks, root privileges, mounted filesystem support, and reliable cleanup through `swapoff()`. Direct include dependencies include `stdio.h`, `errno.h`, `stdlib.h`, `sys/wait.h`, `sys/swap.h`, `tst_test.h`.

Risks and test signals: Swap tests can perturb host memory behavior and hit kernel-global swap limits; cleanup failures leave persistent system state. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TST_EXP_FAIL`; checks errno values `EPERM`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon03.c -->
