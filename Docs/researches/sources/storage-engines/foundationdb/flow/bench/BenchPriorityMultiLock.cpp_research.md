# sources/storage-engines/foundationdb/flow/bench/BenchPriorityMultiLock.cpp

Purpose: benchmarks `PriorityMultiLock` handoff behavior under active and inactive priority sets.

Important APIs/types/functions: coroutine `benchPriorityMultiLock`, wrapper `bench_priorityMultiLock`, `PriorityMultiLock::Lock`, and `makeReference<PriorityMultiLock>`.

Control flow: builds priority levels at multiples of ten, sets concurrency to ten times priority count, fills a deque with lock waiters for active priorities, waits for all initial locks, then repeatedly replaces one future with a new waiter and awaits the old one. Priority and deque index rotate each iteration.

State/persistence: the benchmark owns one lock and deque of futures for the benchmark state. No external persistence.

Dependencies/integration: depends on Flow `PriorityMultiLock`, futures, `waitForAll`, `ThreadHelper.actor.h`, and Google Benchmark.

Risks: comments contain a typo ("buy" for "by") but behavior is clear. The test assumes initial concurrency saturates but remains serviceable. Inactive priorities are included in lock configuration but not actively requested.

Test signals: benchmark ranges vary active priorities 1-64 and inactive priorities 0-128, with an explicit `{5,0}` argument and aggregate reporting.
