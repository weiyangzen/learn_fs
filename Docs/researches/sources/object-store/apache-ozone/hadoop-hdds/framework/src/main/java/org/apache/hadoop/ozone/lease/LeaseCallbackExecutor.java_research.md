# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/lease/LeaseCallbackExecutor.java

## Purpose

`LeaseCallbackExecutor` runs a lease expiration callback and logs failures without propagating them. The complete 63-line source was read for this report.

## Important APIs, Types, and Functions

It implements `Runnable`, stores `resource` and `Callable<Void> callback`, and defines `run`.

## Control Flow

`run` logs debug information, checks callback for null, calls it, and catches any exception to log a warning.

## State and Persistence Behavior

It is a short-lived in-memory runnable. Callback side effects are external.

## Dependencies and Integration Points

It depends on `Callable` and SLF4J. `LeaseManager.LeaseMonitor` submits it to an executor when a lease times out.

## Risks and Edge Cases

Callback failures are swallowed after logging, so callers cannot observe them directly. Long-running callbacks can consume cached-thread-pool resources.

## Test Signals

Tests should verify callback invocation, null callback no-op, exception logging/no propagation, and resource included in logs.
