<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/BackgroundSCMService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/BackgroundSCMService.java

## Purpose

`BackgroundSCMService` is a reusable daemon wrapper for SCM background services that should run only when the SCM leader is ready and out of safe mode. It handles start/stop, status transitions, delayed activation, periodic execution, and test-triggered immediate runs.

## Important APIs, Types, and Functions

It implements `SCMService` with `start`, `stop`, `notifyStatusChanged`, `shouldRun`, and `getServiceName`. Testing APIs are `runImmediately` and `getRunning`. The nested `Builder` supplies interval, wait time, service name, periodical task, `SCMContext`, and `Clock`.

## Control Flow

Construction starts the daemon. `notifyStatusChanged` sets status to running only when `SCMContext.isLeaderReady` and not safe mode, recording the ready timestamp; otherwise it pauses. The run loop executes the task if `shouldRun`, catches all task throwables, then waits for the interval unless woken immediately. `stop` flips the running flag and interrupts the thread.

## State and Persistence Behavior

State is in-memory thread/run status, service status, ready timestamp, and wake flag. No persistence occurs. Work performed by the supplied task may persist state elsewhere.

## Dependencies and Integration Points

It integrates with SCM HA leader readiness, safe mode, service managers, and background tasks such as monitors or flushers. Thread names are prefixed by `SCMContext`.

## Risks and Edge Cases

The constructor starts the thread before the caller can further configure the object. `notifyStatusChanged` must be called after context changes or the service can remain paused. Task exceptions are logged and retried rather than stopping the service.

## Test Signals

Tests should cover builder validation, delayed `shouldRun`, safe-mode and leader-ready transitions, task retry after exception, immediate wake, idempotent start/stop, interrupt handling, and daemon thread naming.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/BackgroundSCMService.java -->
