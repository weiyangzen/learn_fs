<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_04.c

Purpose: Test Description: This Program tests getting and setting the pipe size. It also tests what happen when you write to a full pipe depending on whether O_NONBLOCK is set or not. This ensures parent process is still in non-block mode when using -i parameter. Subquent writes hould return -1 and errno set to either EAGAIN or EWOULDBLOCK because pipe is already full. A pipe has two file descriptors. But in the kernel these two file descriptors point to the same pipe. So setting size from first file handle set size for the pipe.

Important APIs/types/functions: includes `stdlib.h`, `features.h`, `unistd.h`, `stdio.h`, `lapi/fcntl.h`, `tst_test.h`; exercises `pipe`, `write`, `fcntl`; defines `test_pipe2`, `setup`, `cleanup`; uses flags/constants `O_NONBLOCK`.

Control flow centers on `test_pipe2`, `setup`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.forks_child` into the LTP runner. Error-path expectations include `EAGAIN`, `EWOULDBLOCK`.

State and persistence behavior: Runtime state is pipe file descriptors returned atomically with requested flags such as `O_CLOEXEC`, `O_NONBLOCK`, and packet/notification modes where available.

Dependencies and integration points: Depends on pipe2 syscall wrappers, helper child binaries for close-on-exec checks, fcntl status flags, and kernel support for newer pipe flags. Direct include dependencies include `stdlib.h`, `features.h`, `unistd.h`, `stdio.h`, `lapi/fcntl.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TERRNO`, `TFAIL`, `TPASS`, `TST_PROCESS_STATE_WAIT`; checks errno values `EAGAIN`, `EWOULDBLOCK`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_04.c -->
