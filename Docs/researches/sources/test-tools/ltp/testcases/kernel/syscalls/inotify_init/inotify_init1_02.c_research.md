<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_02.c

Purpose: Ported to LTP - Jan 13 2009 - Subrata <subrata@linux.vnet.ibm.com> Verify that inotify_init1() returns a file descriptor and sets the O_NONBLOCK file status flag on the open file description referred to by the new file descriptor only when called with IN_NONBLOCK.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`; touches `inotify_init1`, `raw syscall path`; defines `run`; uses LTP safe helpers such as `SAFE_CLOSE`, `SAFE_FCNTL`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is a newly created inotify file descriptor and its close-on-exec/nonblocking flags.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TST_EXP_EQ_LI`, `TST_EXP_FD`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/inotify_init/inotify_init1_02.c -->
