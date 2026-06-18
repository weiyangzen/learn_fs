<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait_bitset01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait_bitset01.c

Purpose: 1. Block on a bitset futex and wait for timeout, the difference between normal futex and bitset futex is that that the later have absolute timeout. 2. Check that the futex waited for expected time.

Important APIs/types/functions: includes `tst_test.h`, `tst_timer.h`, `futextest.h`; touches `futex`; defines `verify_futex_wait_bitset`, `run`, `setup`.

Control flow centers on `verify_futex_wait_bitset`, `run`, `setup`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt`, `.test_variants` into the LTP runner. Error-path assertions cover `ENOSYS`, `ETIMEDOUT`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `tst_test.h`, `tst_timer.h`, `futextest.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`, `TST_ERR`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_RET`. Expected errno values include `ENOSYS`, `ETIMEDOUT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wait_bitset01.c -->
