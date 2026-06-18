# File Research: sources/virtualization/spdk/lib/init/subsystem.c

`subsystem.c` implements SPDK subsystem registration, dependency ordering, initialization, finalization, and config dumping.

Subsystems and dependency records are stored in global TAILQs populated by constructor-style registration elsewhere. Helpers expose lookup and iteration over subsystems and dependencies. `spdk_subsystem_exists()` asserts app-thread execution and checks by name.

Before initialization, dependency records are validated to ensure both the dependent subsystem and dependency target are registered. `subsystem_sort()` then performs a simple topological ordering by repeatedly moving subsystems whose dependencies are already in a temporary sorted list. The sorted list replaces the original initialization order.

`spdk_subsystem_init()` records the completion callback and starts `spdk_subsystem_init_next()`. The init-next routine advances through the sorted list, invokes each subsystem’s `init()` callback if present, and expects subsystems to call back into `spdk_subsystem_init_next(rc)` when done. On success after the final subsystem, it marks subsystems initialized and calls the original completion callback.

Finalization runs in reverse sorted order through `spdk_subsystem_fini_next()`, invoking each subsystem’s `fini()` if present. It handles the case where finalization interrupts initialization by setting `g_subsystems_init_interrupted` and backing up from the current subsystem. Completion calls the stop callback registered by `spdk_subsystem_fini()`.

`subsystem_config_json()` delegates to a subsystem’s `write_config_json()` hook or writes JSON null if no hook is present.

Research notes: dependency sorting assumes the dependency graph can make progress; a cycle would leave the while loop unable to drain `g_subsystems`. Lifecycle state is global and app-thread oriented.
