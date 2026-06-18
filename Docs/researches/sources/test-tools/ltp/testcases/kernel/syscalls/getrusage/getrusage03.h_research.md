<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.h

Purpose: Shared helper header for getrusage03 that forces context switches, allocates/touches memory, reads swap accounting, and checks deltas.

Important APIs/types/functions: includes `sched.h`, `tst_test.h`; defines `force_context_switches`, `consume_mb`, `is_in_delta`; uses LTP safe helpers such as `SAFE_FILE_LINES_SCANF`, `SAFE_MALLOC`.

Control flow centers on `force_context_switches`, `consume_mb`, `is_in_delta`.

State and persistence behavior: Runtime state is resource accounting for the current process, children, threads, and child exec/fork workloads.

Dependencies and integration points: Depends on process control helpers, child binaries, /proc status reads, capability setup, and resource accounting precision. Direct include dependencies include `sched.h`, `tst_test.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Several cases are timing-, race-, mount-, or resource-accounting-sensitive, so the survival/no-regression signal is as important as exact value matching. Test signals are emitted through `TBROK`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrusage/getrusage03.h -->
