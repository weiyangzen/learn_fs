<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe12.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe12.c

Purpose: Test Description: A pipe has a limited capacity. If the pipe with non block mode is full, then a write(2) will fail and get EAGAIN error. Otherwise, from 1 to PIPE_BUF bytes may be written. For a non-empty(unaligned page size) pipe, the sequent large size write(>page_size)will use new pages. So it may exist a hole in page and we print this value instead of checking it.

Important APIs/types/functions: includes `unistd.h`, `stdlib.h`, `tst_test.h`, `lapi/fcntl.h`; exercises `pipe`, `write`, `fcntl`; defines `verify_pipe`, `cleanup`, `setup`; uses flags/constants `O_NONBLOCK`.

Control flow centers on `verify_pipe`, `cleanup`, `setup`. The `struct tst_test` registration wires `.test`, `.setup`, `.cleanup`, `.tcnt` into the LTP runner. Error-path expectations include `EAGAIN`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `unistd.h`, `stdlib.h`, `tst_test.h`, `lapi/fcntl.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EAGAIN`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe12.c -->
