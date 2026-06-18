<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe15.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe15.c

Purpose: This is a regression test for hangup on pipe operations. See https://www.spinics.net/lists/linux-api/msg49762.html for additional context. It tests that pipe operations do not block indefinitely when going to the soft limit on the total size of all pipes created by a single user.

Important APIs/types/functions: includes `fcntl.h`, `stdlib.h`, `unistd.h`, `tst_test.h`, `tst_safe_stdio.h`, `tst_safe_macros.h`; exercises `pipe`, `fcntl`; defines `run`, `setup`, `cleanup`.

Control flow centers on `run`, `setup`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.cleanup` into the LTP runner. Named case hints include `linux-git`.

State and persistence behavior: Runtime state is anonymous pipe file descriptors, pipe buffer contents/capacity, blocking and nonblocking status flags, EOF behavior, and descriptor inheritance.

Dependencies and integration points: Depends on LTP pipe/fcntl/safe I/O helpers, temporary processes, optional resource-limit changes, and blocking/nonblocking pipe semantics. Direct include dependencies include `fcntl.h`, `stdlib.h`, `unistd.h`, `tst_test.h`, `tst_safe_stdio.h`, `tst_safe_macros.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TCONF`, `TINFO`, `TPASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pipe/pipe15.c -->
