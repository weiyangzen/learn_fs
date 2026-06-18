<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe11.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe11.c

Purpose: Ported to LTP: Wayne Boyer Check if many children can read what is written to a pipe by the parent. ALGORITHM For a different nchilds number: 1. Open a pipe and write nchilds * (PIPE_BUF/nchilds) bytes into it 2. Fork nchilds children 3. Each child reads PIPE_BUF/nchilds characters and checks that the bytes read are correct

Important APIs/types/functions: includes `stdlib.h`, `tst_test.h`; exercises `pipe`, `read`, `write`; defines `do_child`, `run`.

Control flow centers on `do_child`, `run`. The `struct tst_test` registration wires `.forks_child`, `.test`, `.tcnt` into the LTP runner.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `stdlib.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TINFO`, `TPASS`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe11.c -->
