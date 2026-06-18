# sources/storage-engines/foundationdb/flow/bench/BenchNet2.cpp

Purpose: C++20 coroutine benchmark version for Flow net2 scheduling patterns, intended to compare with actor-style equivalents.

Important APIs/types/functions: coroutine `increment`, `getRandomTaskPriority`, `benchNet2Actor`, `benchDelayLoop`, `benchYieldLoop`, and benchmark wrappers `coroutine_net2`, `coroutine_delay_bench`, `coroutine_yield_bench`.

Control flow: net2 benchmark creates `actorCount` delayed increment futures at deterministic priorities, waits for all, and consumes the sum. Delay/yield benchmarks first populate the run-loop priority queue with random future timers, then repeatedly `co_await delay(0)` or `yield()`.

State/persistence: no persistent state. Random seed is captured once per benchmark actor to make priority selection repeatable within the run.

Dependencies/integration: uses Flow `delay`, `yield`, `waitForAll`, network/task priority definitions, deterministic random, platform random seed, and `onMainThread`.

Risks: comments note a GCC coroutine issue that led to separate delay/yield functions. Results are scheduler-sensitive and depend on timer queue population rather than real network I/O.

Test signals: registered ranges cover actor counts or timer counts from 1/0 up to `1 << 16`, with aggregate reporting and items processed counters.
