# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/ThrottledAsyncChecker.java

Purpose: Generic asynchronous checker that throttles repeated checks of the same `Checkable` and optionally wraps checks with a timeout.

Important APIs and types: Implements `AsyncChecker<K,V>`. Main methods are `schedule(Checkable<K,V>, K)` and `shutdownAndWait`. Internal maps track in-progress checks and last completed checks; `LastCheckResult` stores completion time and result/exception marker.

Control flow: `schedule` returns empty if the target already has an in-progress check or completed too recently. Otherwise it submits `target.check(context)`, wraps with `Futures.withTimeout` when configured, records the future in `checksInProgress`, and attaches a direct callback to move the target into `completedChecks` on success or failure.

State and persistence: Runtime-only state includes throttling timestamps in a `WeakHashMap` and active futures in a `HashMap`, protected by synchronization. No durable state.

Dependencies and integration points: Used by `StorageVolumeChecker` for volume checks. It relies on Hadoop `Timer`, Guava `ListeningExecutorService`, timeout futures, and a scheduled executor for timeout enforcement.

Risks: The cache uses `Checkable` object identity/equality, so equality changes would break throttling. Timed-out underlying tasks may continue until interrupted by the executor depending on future behavior. Tests should cover duplicate in-progress scheduling, minimum-gap skipping after failures and successes, timeout propagation, weak completed-cache behavior, and shutdown interrupting active work.
