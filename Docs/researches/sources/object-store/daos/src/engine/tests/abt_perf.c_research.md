# sources/object-store/daos/src/engine/tests/abt_perf.c

Purpose: standalone Argobots microbenchmark for DAOS developers. It measures ULT creation rate, ULT scheduling/yield rate, and creation/free rates for ABT mutexes, rwlocks, condition variables, and eventuals.

Important APIs and functions: `main()` parses `-t`, `-n`, `-s`, and `-S`, initializes DAOS logging and Argobots, obtains the current xstream main pool, and dispatches by test id. `abt_ult_create_rate()` keeps at most `opt_concur` ULTs in flight and measures recursive ULT creation through `abt_thread_1()`. `abt_sched_rate()` creates `opt_concur` workers using `abt_thread_2()` and counts lock/yield cycles. `abt_lock_create_rate()` repeatedly creates and frees the ABT synchronization primitive selected by `opt_cr_type`. `abt_current_ms()` wraps `CLOCK_MONOTONIC`.

Control flow: setup creates one global ABT pool, condition, mutex, and optional thread attribute with a stack size in KiB. Creation tests drive a loop until `opt_secs` elapses, then wait for outstanding ULTs to drain. Scheduling tests start all ULTs before timing. Primitive creation tests run one worker ULT and wait on `abt_cond` for completion.

State and persistence: all state is process-local globals: counters, concurrency, `abt_exiting`, `abt_waiting`, ABT handles, and selected options. There is no persisted state. The synchronization contract depends on `abt_lock` protecting `abt_cntr`, `abt_ults`, and exit/wait flags.

Dependencies and integration: depends on Argobots, DAOS/GURT logging, and `daos_srv/daos_engine.h` for error formatting. It is a test executable rather than library code.

Risks: `opt_secs` is required for creation/scheduling but not explicitly validated for primitive creation paths, so a zero duration can reach division by zero. Some paths use `assert()` rather than DAOS error unwinding. Recursive ULT creation can stress scheduler and stack behavior by design. Timing is coarse millisecond wall-clock and suitable for relative perf checks, not exact benchmarking.

Test signals: the file is itself a manual/perf test. Useful signals are successful ABT init/finalize, no deadlock in the wait/broadcast loop, printed per-second creation progress, and final rates for selected test ids `c`, `s`, `m`, `w`, `e`, and `d`.
