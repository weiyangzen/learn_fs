<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid02.c

Purpose:  This test spawns multiple threads, then check for each one of them if the parent ID is different AND if the thread ID is different from all the other spwaned threads.

Important APIs/types/functions: includes `tst_test.h`, `lapi/syscalls.h`, `tst_safe_pthread.h`; touches `raw syscall path`; defines `run`; uses LTP safe helpers such as `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`.

Control flow centers on `run`. The `struct tst_test` registration wires `.test_all` into the LTP runner.

State and persistence behavior: Runtime state is Linux task identity, contrasting process IDs with thread IDs in single- and multi-threaded cases.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `tst_test.h`, `lapi/syscalls.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_EXP_EXPR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/gettid/gettid02.c -->
