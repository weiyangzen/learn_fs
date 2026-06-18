# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseManager.java

## Purpose

`LeaseManager<T>` manages timed leases for resources, preventing duplicate leases, monitoring expiration, releasing leases, and executing expiration callbacks. The complete 300-line source was read for this report.

## Important APIs, Types, and Functions

Public APIs are constructor, `start`, overloaded `acquire`, `get`, `release`, and `shutdown`. It owns `activeLeases`, a `Semaphore`, monitor thread, `LeaseMonitor`, default timeout, and running flag. Nested `LeaseMonitor` implements the expiration loop.

## Control Flow

`start` initializes the concurrent map, monitor, daemon thread, uncaught-exception handler, and running flag. `acquire` checks running state, rejects duplicate resources, creates a lease, stores it, and releases the semaphore to wake the monitor. `release` removes and invalidates a lease. `shutdown` disables monitor, wakes/interrupts it, releases all active leases without callbacks, and marks not running. The monitor scans active leases, releases expired leases, submits callbacks, and sleeps until the nearest remaining expiration or until the semaphore wakes it for a new lease.

## State and Persistence Behavior

All state is in-memory. There is no persistence; leases are lost on process restart. Callback side effects are external.

## Dependencies and Integration Points

It depends on lease classes, `ConcurrentHashMap`, `Semaphore`, `ExecutorService`, and SLF4J. Services use it for generic resource lease management.

## Risks and Edge Cases

The uncaught-exception handler calls `leaseMonitorThread.start()` on the same thread object, which cannot be restarted after termination. `isRunning` is not volatile and is set after thread start. `shutdown` calls `checkStatus`, so repeated shutdown throws `LeaseManagerNotRunningException`. The monitor uses `Long.MAX_VALUE` timeout in `tryAcquire`, which can be problematic. Callback executor is not explicitly shut down. Lease expiration state relies on `release` invalidation.

## Test Signals

Tests should cover acquire/get/release lifecycle, duplicate acquire, not-running behavior, expiration and callback execution, renew delaying expiration, shutdown releasing without callbacks, repeated shutdown behavior, monitor wakeup on new leases, and uncaught exception handling.
