<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv01.c

Purpose: Negative and timeout coverage for futex_waitv: invalid flags, unaligned/null addresses, invalid waiter arrays, invalid clocks/counts, value mismatch, and ETIMEDOUT behavior.

Important APIs/types/functions: includes `time.h`, `stdlib.h`, `tst_test.h`, `lapi/futex.h`, `futex2test.h`, `tst_safe_clocks.h`; touches `futex`, `futex_waitv`; defines `setup`, `init_timeout`, `init_waitv`, `test_invalid_flags`, `test_unaligned_address`, `test_null_address`, `test_null_waiters`, `test_invalid_clockid`, `test_invalid_nr_futexes`, `test_mismatch_between_uaddr_and_val`, `test_timeout`, `cleanup`; uses LTP safe helpers such as `SAFE_CLOCK_GETTIME`, `SAFE_MALLOC`.

Control flow centers on `setup`, `init_timeout`, `init_waitv`, `test_invalid_flags`, `test_unaligned_address`, `test_null_address`, `test_null_waiters`, `test_invalid_clockid`, `test_invalid_nr_futexes`, `test_mismatch_between_uaddr_and_val`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup` into the LTP runner. Error-path assertions cover `EAGAIN`, `EFAULT`, `EINVAL`, `ETIMEDOUT`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `time.h`, `stdlib.h`, `tst_test.h`, `lapi/futex.h`, `futex2test.h`, `tst_safe_clocks.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TST_EXP_FAIL`. Expected errno values include `EAGAIN`, `EFAULT`, `EINVAL`, `ETIMEDOUT`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv01.c -->
