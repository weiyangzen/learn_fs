<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe14.c

Purpose: Verify that, if the write end of a pipe is closed, then a process reading from the pipe will see end-of-file (i.e., read() returns 0) once it has read all remaining data in the pipe.

Important APIs/types/functions: includes `tst_test.h`; exercises `pipe`, `read`, `write`; defines `run`, `cleanup`.

Control flow centers on `run`, `cleanup`. The `struct tst_test` registration wires `.test_all`, `.cleanup` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TST_EXP_VAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe14.c -->
