<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TaskPriority.h -->
# sources/storage-engines/foundationdb/flow/include/flow/TaskPriority.h

Purpose: This header defines the numeric priority ladder used by the Flow task queue and actor scheduler. It gives named priority values for networking, cluster coordination, transaction processing, data distribution, disk IO, restore, blob workers, and low-priority work.

Important APIs and types: `enum class TaskPriority` contains ordered values from `Zero` and `Min` through `Max`. Helper functions are `incrementPriority`, `decrementPriority`, `incrementPriorityIfEven`, and `getTaskPriorityFromInt`.

Control flow: The scheduler treats larger numeric priorities as higher priority through `TaskQueue`'s shifted FIFO priority. The helpers intentionally expose small arithmetic adjustments while using long names to discourage casual manipulation. `getTaskPriorityFromInt` asserts the integer is between `Min` and `Max`.

State and persistence behavior: There is no runtime state or persistence. The numeric values are a cross-component scheduling contract and should be treated as compatibility-sensitive for performance behavior.

Dependencies and integration points: It depends on `flow/Error.h` for `ASSERT`. It is consumed by `TaskQueue`, `g_network->onMainThread`, actor scheduling, network IO paths, cluster-controller roles, data distribution, storage, restore, and blob worker code.

Risks: Changing numeric values can introduce starvation or latency regressions. Some values intentionally share the same priority, such as `LoadBalancedEndpoint` and `ReadSocket`, so uniqueness is not guaranteed. Arithmetic helpers can produce priorities outside intended named ranges if misused.

Test signals: Scheduler tests should verify ordering, FIFO behavior among equal priorities through `TaskQueue`, boundary assertions for integer conversion, and performance/regression tests for latency-sensitive task classes.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TaskPriority.h -->
