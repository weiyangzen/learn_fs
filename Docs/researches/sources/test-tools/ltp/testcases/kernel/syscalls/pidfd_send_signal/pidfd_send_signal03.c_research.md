<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal03.c

Purpose: This test checks if the pidfd_send_signal syscall wrongfully sends a signal to a new process which inherited the PID of the actual target process. In order to do so it is necessary to start a process with a pre- determined PID. This is accomplished by writing to the /proc/sys/kernel/ns_last_pid file. By utilizing this, this test forks two children with the same PID. It is then checked, if the syscall will send a signal to the second child using the pidfd of the first one.

Important APIs/types/functions: includes `signal.h`, `stdio.h`, `unistd.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`; exercises `pidfd_send_signal`; defines `get_inode_number`, `verify_pidfd_send_signal`, `setup`, `cleanup`; uses flags/constants `O_CLOEXEC`, `O_DIRECTORY`.

Control flow centers on `get_inode_number`, `verify_pidfd_send_signal`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.needs_root`, `.forks_child` into the LTP runner. Error-path expectations include `ESRCH`.

State and persistence behavior: Runtime state is pidfd-backed signal delivery to forked children and permission checks for signal numbers, info pointers, and pidfd validity.

Dependencies and integration points: Depends on pidfd_send_signal syscall wrappers, forked children, signal handlers, and permission/error-path helpers. Direct include dependencies include `signal.h`, `stdio.h`, `unistd.h`, `tst_test.h`, `lapi/pidfd.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TCONF`, `TFAIL`, `TINFO`, `TPASS`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `ESRCH`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_send_signal/pidfd_send_signal03.c -->
