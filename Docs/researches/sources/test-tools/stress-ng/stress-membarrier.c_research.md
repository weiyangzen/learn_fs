# sources/test-tools/stress-ng/stress-membarrier.c

Purpose: implements `membarrier`, a memory-barrier syscall stressor. It repeatedly queries supported membarrier commands and invokes each supported command from the main thread and helper threads.

Important APIs/types/functions: `membarrier_info_t` stores thread handle, return status, duration, and count. Fallback enums define command constants if headers are absent. `stress_membarrier_exercise()` calls `MEMBARRIER_CMD_QUERY`, iterates command bits, invokes supported commands with normal flags and optional `MEMBARRIER_CMD_FLAG_CPU`, and exercises illegal flags, illegal CPU ids, and one unsupported command. `stress_membarrier_thread()` loops the exercise function.

Control flow: the stressor verifies the syscall exists and shared/global command support is present. It initializes per-thread info, starts four worker pthreads, synchronizes, runs the same exercise loop in the main thread, stops workers, aggregates timing/count fields, emits calls-per-second metrics, and joins threads.

State and persistence: static state is only the keep-running flag and blocked-signal set. Per-thread metrics live on the stack. No external state persists.

Dependencies/integration: requires pthreads and `__NR_membarrier`; optionally uses `linux/membarrier.h`. Integrates with stress-ng shim syscall wrapper, proc-state synchronization, metrics, and unimplemented registration.

Risks/test signals: metric aggregation is intentionally racy to avoid lock overhead, so rates are approximate. Useful signals are skip on `ENOSYS` or missing shared command, failure if query later fails, bogo increments, joined helper threads, and nonzero call-rate metrics.
