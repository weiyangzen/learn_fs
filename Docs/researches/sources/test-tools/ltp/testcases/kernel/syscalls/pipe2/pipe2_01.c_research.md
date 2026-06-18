<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_01.c

Purpose: History: Created - Jan 13 2009 - Ulrich Drepper <drepper@redhat.com> Ported to LTP - Jan 13 2009 - Subrata <subrata@linux.vnet.ibm.com> Converted into new api - Apri 15 2020 - Yang Xu <xuyang2018.jy@cn.fujitsu.com> It may get EINVAL error on older kernel because this flag was introduced since kernel 3.4. We only test flag in write end because this flag was used to make pipe buffer marked with the PIPE_BUF_FLAG_PACKET flag. In read end, kernel also checks buffer flag instead of O_DIRECT. So it make no sense to check this flag in fds[0].

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `lapi/fcntl.h`, `tst_test.h`; exercises `pipe2`, `pipe`, `read`, `write`, `fcntl`; defines `cleanup`, `verify_pipe2`; uses flags/constants `O_CLOEXEC`, `O_DIRECT`, `O_NONBLOCK`.

Control flow centers on `cleanup`, `verify_pipe2`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.cleanup` into the LTP runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is pipe file descriptors returned atomically with requested flags such as `O_CLOEXEC`, `O_NONBLOCK`, and packet/notification modes where available.

Dependencies and integration points: Depends on pipe2 syscall wrappers, helper child binaries for close-on-exec checks, fcntl status flags, and kernel support for newer pipe flags. Direct include dependencies include `stdio.h`, `unistd.h`, `lapi/fcntl.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe2/pipe2_01.c -->
