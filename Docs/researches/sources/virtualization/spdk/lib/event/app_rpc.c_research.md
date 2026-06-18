# File Research: sources/virtualization/spdk/lib/event/app_rpc.c

Implements JSON-RPC methods for SPDK application/framework introspection and runtime control.

Important RPCs:
- `spdk_kill_instance`: sends a decoded signal to the current process.
- `framework_monitor_context_switch`: gets/sets context-switch monitoring.
- `thread_get_stats`: returns per-SPDK-thread busy/idle ticks, cpumask, and poller counts.
- `thread_get_pollers`: lists active, timed, and paused pollers per thread.
- `thread_get_io_channels`: lists IO channels per thread.
- `framework_get_reactors`: returns per-reactor lcore, NUMA, TID, busy/idle, interrupt state, OS CPU stats, optional governor frequency, and lightweight threads.
- `framework_set_scheduler` / `framework_get_scheduler`: controls and reports scheduler name, period, isolated core mask, scheduling core, governor, and scheduler-specific options.
- `framework_get_governor`: reports governor-specific data and per-core frequency data.
- `scheduler_set_options`: startup-only scheduler core and isolated-core-mask configuration.
- `thread_set_cpumask`: updates a thread cpumask asynchronously on the target SPDK thread.

Integration details:
- Uses `spdk_for_each_thread()` and `spdk_for_each_reactor()` to gather distributed runtime state.
- Uses generated RPC decoder/free helpers from `spdk_internal/rpc_autogen.h`.
- Validates cpumasks against the active reactor mask and interrupt-mode scheduling constraints.
