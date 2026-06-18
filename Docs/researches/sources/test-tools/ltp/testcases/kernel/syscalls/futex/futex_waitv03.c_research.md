<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv03.c

Purpose: Shared-memory futex_waitv wake test, covering wait vectors whose futex words live in IPC shared memory rather than process-private storage.

Important APIs/types/functions: includes `unistd.h`, `time.h`, `sys/shm.h`, `tst_test.h`, `lapi/futex.h`, `lapi/syscalls.h`, `futex2test.h`, `futex_utils.h`; touches `futex`, `futex_waitv`; defines `setup`, `cleanup`, `run`; uses LTP safe helpers such as `SAFE_CLOCK_GETTIME`, `SAFE_PTHREAD_CREATE`, `SAFE_PTHREAD_JOIN`, `SAFE_SHMAT`, `SAFE_SHMCTL`, `SAFE_SHMDT`, `SAFE_SHMGET`.

Control flow centers on `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.test_all`, `.setup`, `.cleanup`, `.test_variants` into the LTP runner.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `unistd.h`, `time.h`, `sys/shm.h`, `tst_test.h`, `lapi/futex.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TFAIL`, `TPASS`, `TST_RET`, `TST_RETRY_FUNC`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futex_waitv03.c -->
