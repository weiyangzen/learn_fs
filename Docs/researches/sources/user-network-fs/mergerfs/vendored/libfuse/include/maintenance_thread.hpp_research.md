<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/maintenance_thread.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/maintenance_thread.hpp

Purpose: `MaintenanceThread` declares a process-wide background maintenance facility for periodic or queued cleanup tasks.

Important APIs: `setup()` starts or initializes the facility, `stop()` shuts it down, and `push_job(const std::function<void(u64)> &)` queues work that receives a `u64` argument, likely a tick/count/time value.

State and integration: implementation state is external to this header and likely includes a worker thread and job list. It integrates with libfuse cache cleanup, message buffer GC, or other runtime maintenance tasks.

Risks and test signals: lifecycle ordering matters; jobs pushed before setup or after stop need defined behavior. Tests should cover start/stop idempotency, job execution, shutdown while jobs are queued, and exception handling inside jobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/maintenance_thread.hpp -->
