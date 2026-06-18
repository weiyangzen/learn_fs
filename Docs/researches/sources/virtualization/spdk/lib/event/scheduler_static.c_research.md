# File Research: sources/virtualization/spdk/lib/event/scheduler_static.c

Implements SPDK's static scheduler.

Important behavior:
- First initialization disables periodic scheduling by setting scheduler period to zero.
- On later reloads, sets a short period to restore threads to their saved initial lcores.
- `balance_static()` sets all cores to polling mode, restores each thread's target lcore from `lw_thread->initial_lcore`, then disables further balancing.
- Supports startup JSON options with a `mappings` string that maps thread IDs to core IDs.
- Validates thread existence, core existence, and thread cpumask compatibility before applying mappings.
- Registers as scheduler name `static`.

Role: provides deterministic thread placement and a baseline scheduler that performs no ongoing load balancing.
