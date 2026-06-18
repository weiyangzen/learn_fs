<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon02.c

Purpose: This test case checks whether swapon(2) system call returns: - ENOENT when the path does not exist - EINVAL when the path exists but is invalid - EPERM when user is not a superuser - EBUSY when the specified path is already being used as a swap area

Important APIs/types/functions: includes `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`; exercises `swapoff`, `swapon`, `raw syscall path`; defines `setup`, `cleanup`, `verify_swapon`; uses constants `EBUSY`, `EINVAL`, `ENOENT`, `EPERM`.

Control flow centers on `setup`, `cleanup`, `verify_swapon`. The `struct tst_test` registration wires `.mntpoint`, `.mount_device`, `.all_filesystems`, `.needs_root`, `.test`, `.tcnt`, `.setup`, `.cleanup` into the runner. Named case hints include `Path does not exist`, `Invalid path`, `Permission denied`, `File already used`. Error-path expectations include `EBUSY`, `EINVAL`, `ENOENT`, `EPERM`.

State and persistence behavior: Runtime state is active swap areas, `/proc/meminfo` accounting, cgroup memory limits where present, temporary swapfile contents, and the kernel-wide maximum number of swapfiles.

Dependencies and integration points: Depends on swapfile helpers, cgroup/meminfo helpers for memory-pressure checks, root privileges, mounted filesystem support, and reliable cleanup through `swapoff()`. Direct include dependencies include `pwd.h`, `tst_test.h`, `lapi/syscalls.h`, `tse_swap.h`.

Risks and test signals: Swap tests can perturb host memory behavior and hit kernel-global swap limits; cleanup failures leave persistent system state. Test signals: reports through `TERRNO`, `TFAIL`, `TST_EXP_FAIL`, `TST_RET`; checks errno values `EBUSY`, `EINVAL`, `ENOENT`, `EPERM`; runs against mounted filesystem fixtures; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/swapon/swapon02.c -->
