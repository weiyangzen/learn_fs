<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futextest.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futex/futextest.h

Purpose: Header-only futex test library that wraps raw futex syscalls and provides reusable wait, wake, bitset, PI, requeue, and kernel-support probes.

Important APIs/types/functions: includes `unistd.h`, `sys/syscall.h`, `sys/types.h`, `lapi/futex.h`, `tst_timer.h`; touches `futex`, `raw syscall path`; defines `futex_supported_by_kernel`, `futex_syscall`, `futex_wait`, `futex_wake`, `futex_wait_bitset`, `futex_wake_bitset`, `futex_lock_pi`, `futex_unlock_pi`, `futex_wake_op`, `futex_requeue`, `futex_cmp_requeue`, `futex_wait_requeue_pi`.

Control flow centers on `futex_supported_by_kernel`, `futex_syscall`, `futex_wait`, `futex_wake`, `futex_wait_bitset`, `futex_wake_bitset`, `futex_lock_pi`, `futex_unlock_pi`, `futex_wake_op`, `futex_requeue`. Error-path assertions cover `ECHCK`, `ENOSYS`.

State and persistence behavior: Runtime state is the futex word plus thread/process wait queues; tests deliberately use private futexes, shared memory, timeouts, wake counts, or bitsets to expose kernel wait/wake behavior.

Dependencies and integration points: Integrates LTP futex helper headers, lapi futex constants, pthread/fork helpers, timer helpers, and architecture variants for futex/futex_time64 where present. Direct include dependencies include `unistd.h`, `sys/syscall.h`, `sys/types.h`, `lapi/futex.h`, `tst_timer.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`, `TCONF`, `TST_ERR`, `TST_RET`, `TST_RETRY_FUNC`. Expected errno values include `ECHCK`, `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futex/futextest.h -->
