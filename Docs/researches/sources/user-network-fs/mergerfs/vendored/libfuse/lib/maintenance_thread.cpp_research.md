# sources/user-network-fs/mergerfs/vendored/libfuse/lib/maintenance_thread.cpp

## Purpose
`maintenance_thread.cpp` implements a small periodic job runner used by libfuse for GC and optional metrics.

## Important APIs, Types, and Functions
`MaintenanceThread::setup` starts the thread, `push_job` appends a `std::function<void(u64)>`, and `stop` cancels and joins it. `_thread_loop` names the thread `fuse.maint`, increments a minute counter, and runs all registered functions under a mutex.

## Control Flow
Setup creates one pthread. The loop disables cancellation while holding the job mutex and invoking functions, enables cancellation before sleeping, increments the count each minute, and repeats forever. Stop cancels the sleeping thread and joins it.

## State and Persistence
Global state includes the pthread id, vector of job functions, and mutex. Jobs persist until process exit; this file does not clear `g_funcs` on stop.

## Dependencies and Integration Points
It depends on `fatal.hpp`, `mutex.hpp`, pthreads, and sleep. `fuse_loop.cpp` starts/stops it and `fuse.cpp` registers GC/metrics callbacks through `fuse_populate_maintenance_thread`.

## Risks
Callbacks execute under the maintenance mutex, so slow callbacks block registration and each other. Since jobs are not cleared, repeated setup/stop cycles in one process can duplicate callbacks. Cancellation safety depends on only enabling cancellation outside the critical section.

## Test Signals
Test setup/stop lifecycle, callback execution count, duplicate setup behavior, cancellation during sleep, callback exceptions/abort policy, and long-running callbacks delaying stop.
