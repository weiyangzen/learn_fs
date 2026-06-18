<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake04.c

Purpose: Regression coverage for unique futex keys on shared huge pages so unrelated futex words do not wake the wrong waiter.

Important APIs/types/functions: includes `stdio.h`, `fcntl.h`, `sys/time.h`, `string.h`, `futextest.h`, `futex_utils.h`, `lapi/mmap.h`, `tst_safe_stdio.h`; touches `futex`, `getpagesize`, `mmap`; defines `setup`, `wakeup_thread2`; uses LTP safe helpers such as `SAFE_MUNMAP`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`.

Control flow centers on `setup`, `wakeup_thread2`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.test_variants`, `.needs_root`, `.needs_tmpdir` into the LTP runner. Error-path assertions cover `ENOMEM`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `stdio.h`, `fcntl.h`, `sys/time.h`, `string.h`, `futextest.h`, `futex_utils.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`, `TFAIL`, `TPASS`, `TST_KERN_OLD_TIMESPEC`, `TST_KERN_TIMESPEC`, `TST_NEEDS`. Expected errno values include `ENOMEM`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_wake04.c -->
