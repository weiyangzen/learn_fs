# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/InjectedUpgradeFinalizationExecutor.java

Purpose: Test executor that extends `DefaultUpgradeFinalizationExecutor` with injectable pause/abort points for upgrade finalization tests.

Important APIs/types/functions: `InjectedUpgradeFinalizationExecutor<T>`, enum `UpgradeTestInjectionPoints`, `UpgradeTestInjectionAbort`, `configureTestInjectionFunction`, `injectTestFunctionAtThisPoint`, and overridden `execute`.

Control flow: `execute` calls injected functions before pre-finalize, after pre-finalize, after feature finalization, and after post-finalize. If an injected function returns true, an internal exception aborts the flow. Any exception logs a warning and resets upgrade state to `FINALIZATION_REQUIRED` when finalization is still needed, then always calls `markFinalizationDone`.

State and persistence behavior: Holds a configured `Callable<Boolean>` and injection point. Mutates the finalizer version manager's upgrade state on failed/incomplete finalization.

Dependencies and integration points: Integrates with `BasicUpgradeFinalizer`, `DefaultUpgradeFinalizationExecutor`, `UpgradeFinalization.Status`, and SLF4J logging.

Risks: Catch-all exception handling suppresses injected errors by design, so tests must assert resulting state. Injection point numeric values skip 3, which is harmless but non-obvious.

Test signals: Enables deterministic tests for concurrent, paused, and terminated upgrade finalization paths.
