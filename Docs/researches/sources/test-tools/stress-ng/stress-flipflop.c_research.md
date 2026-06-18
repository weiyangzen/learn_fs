# sources/test-tools/stress-ng/stress-flipflop.c

Purpose: implements `flipflop`, a scheduler/cacheline contention stressor where paired pthread groups repeatedly clear and set individual bits in shared words using compare-and-swap, optionally pinned to separate CPU sets.

Important APIs/types/functions: `stress_flipflop_info_t` describes one bit worker, including target word, masks, loop counters, CPU set, thread, parent pid, and shared hold/exit flags. `stress_flipflop_worker_t` pads each worker to a 64-byte boundary. `stress_flipflop_worker()` applies `sched_setaffinity()`, waits for release, repeatedly computes the target bit state, performs `__sync_val_compare_and_swap`, and records loops/tries/successes. `stress_flipflop_create_workers()` initializes one clear or set worker per bit.

Control flow: `stress_flipflop()` chooses bit count and optional tasksets, allocates distribution, bit, and worker arrays, synchronizes, creates clear workers on CPU set A and set workers on CPU set B, releases the hold flag, and pauses until SIGUSR1/SIGALRM wakes it. It aggregates worker loop counts into stress-ng bogo operations, exits when max ops or stop condition is reached, joins threads, and prints loop/try/success and percentile QPS summaries for instance zero.

State and persistence behavior: state is in anonymous memory: shared bit words, per-worker counters, and boolean control flags. No filesystem or durable state is created.

Dependencies and integration points: requires pthreads, `cpu_set_t`, `sched_setaffinity()`, and GCC-style `__sync_val_compare_and_swap`; otherwise registers unimplemented. Uses stress-ng affinity parsing, mmap population, sort, signal ignore handling, timing, and bogo APIs. Registered as `CLASS_SCHEDULER | CLASS_OS | CLASS_HOT`, `VERIFY_NONE`.

Risks: `stress_flipflop_uint64_cmp()` returns `-1` for both less-than and greater-than, which does not implement a correct total order for qsort and can skew percentile reporting. Division in informational percentages assumes nonzero loops/tries. Very high bit counts create two threads per bit, up to 131072 threads at the configured maximum, which may exceed system limits.

Test signals: run small bit counts, CPU-pinned tasksets, and maximize mode. Verify thread creation failures are handled, bogo counts progress, SIGUSR1 wakeups occur, and percentile output remains sane after fixing or testing the comparator behavior.
