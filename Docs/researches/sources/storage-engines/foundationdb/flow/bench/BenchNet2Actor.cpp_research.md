# sources/storage-engines/foundationdb/flow/bench/BenchNet2Actor.cpp

Purpose: actor-named benchmark file for net2 scheduling, delay, and yield overhead; current implementation uses coroutine syntax while preserving actor benchmark naming/shape.

Important APIs/types/functions: `increment`, `getRandomTaskPriority`, `benchNet2Actor`, `populateTimers`, `benchDelayLoop`, `benchYieldLoop`, template wrapper `bench_delay`.

Control flow: mirrors `BenchNet2.cpp`: spawn delayed increments, wait for all, or populate timers and repeatedly await `delay(0)`/`yield()`. `bench_delay` dispatches between delay and yield via a compile-time boolean.

State/persistence: local vectors hold outstanding timers or increment futures. No durable state is kept.

Dependencies/integration: Flow network and scheduling primitives, deterministic random, `ThreadHelper.actor.h`, and Google Benchmark. It registers `bench_net2` and template `bench_delay` variants.

Risks: the file name and comments imply ACTOR comparison, but the visible implementation is coroutine-based; researchers should confirm whether generated `.actor.g.cpp` or historical versions supply additional actor-only behavior elsewhere. Timer futures are intentionally retained only to keep the queue populated.

Test signals: benchmark ranges exercise `Range(1, 1 << 16)` for net2 and `Range(0, 1 << 16)` for delay/yield.
