# sources/test-tools/stress-ng/stress-lockbus.c

Purpose: implements the `lockbus` CPU/cache/memory stressor. It repeatedly performs locked atomic memory operations against local and shared mappings, with optional split-lock activity on x86, to create cache-line, bus-lock, and memory-ordering pressure.

Important APIs/types/functions: the stressor is registered through `stress_lockbus_info`; options are `lockbus-bytes` and `lockbus-nosplit`. `stress_lockbus_init()` allocates a shared anonymous mapping and rounds the configured byte count to a two-page boundary; `stress_lockbus_deinit()` unmaps it. `stress_lockbus()` allocates a per-worker local mapping, installs SIGBUS/SIGILL handlers, probes misaligned and x86 split-lock behavior, optionally NUMA-randomizes pages, then loops over `MEM_LOCK`, `__atomic_*`/inline x86 `lock addl`, and optional compare-and-swap operations.

Control flow: initialization creates shared state before worker execution. A worker maps local data, tests whether unsupported misaligned/split locks trap or hang, synchronizes with other workers, then alternates random local/shared pointer selection with bursts of locked increments, locked no-op additions, and compare-and-swap pairs. Cleanup deletes timers and unmaps local memory.

State and persistence: persistent process state is limited to static capability flags (`do_misaligned`, `do_splitlock`, `do_sigill`) and the shared mapping. No filesystem state is created. Metrics report nanoseconds per memory lock operation.

Dependencies/integration: depends on `core-arch`, `core-mmap`, `core-numa`, compiler atomics or x86 inline assembly, `sigsetjmp`, and optional POSIX timers. It integrates with stress-ng options, proc-state synchronization, NUMA helpers, memory accounting, and metrics.

Risks/test signals: unsupported split or misaligned atomics can raise SIGBUS/SIGILL or hang old kernels, so the signal/timer escapes are critical. Useful signals are supported/skip build paths, debug messages for lock capability, no leaked mappings, and nonzero lock-operation metrics.
