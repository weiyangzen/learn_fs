<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake02.c

Purpose: Block several threads on a private mutex, then wake them up. We do the real test in a child because with the test -i parameter the loop that checks that all threads are sleeping may fail with ENOENT. That is because some of the threads from previous run may still be there. Which is because the userspace part of pthread_join() sleeps in a futex on a pthread tid which is woken up at the end of the exit_mm(tsk) which is before the process is removed from the parent thread_group list. So there is a small race window wh

Important APIs/types/functions: includes `sys/types.h`, `futextest.h`, `futex_utils.h`, `tst_safe_pthread.h`; touches `futex`, `pthread_join`; defines `threads_awake`, `clear_threads_awake`, `do_child`, `run`, `setup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`.

Control flow centers on `threads_awake`, `clear_threads_awake`, `do_child`, `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.test_variants`, `.forks_child` into the LTP runner. Error-path assertions cover `ENOENT`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `sys/types.h`, `futextest.h`, `futex_utils.h`, `tst_safe_pthread.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_RET`. Expected errno values include `ENOENT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake02.c -->
