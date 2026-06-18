<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake03.c

Purpose: Block several processes on a mutex, then wake them up.

Important APIs/types/functions: includes `sys/types.h`, `sys/wait.h`, `futextest.h`, `futex_utils.h`; touches `futex`; defines `do_child`, `do_wake`, `run`, `setup`; uses LTP safe helpers such as `SAFE_FORK`, `SAFE_MMAP`.

Control flow centers on `do_child`, `do_wake`, `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.test_variants`, `.forks_child` into the LTP runner.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `sys/types.h`, `sys/wait.h`, `futextest.h`, `futex_utils.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TFAIL`, `TPASS`, `TST_PROCESS_STATE_WAIT`, `TST_RET`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake03.c -->
