# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/util/ShutdownHookManager.java

## Purpose

`ShutdownHookManager` is Ozone's forked Hadoop-style shutdown coordinator. It registers one JVM shutdown hook and executes registered hooks deterministically by priority, with per-hook timeouts and an Ozone-specific timeout configuration.

## APIs and control flow

A static singleton installs a JVM hook at class load. During JVM shutdown, it atomically marks shutdown in progress, calls `executeShutdown()`, logs timing, and then shuts down the single-thread executor. Hooks are stored as `HookEntry` objects in a synchronized set and sorted highest priority first at execution. `addShutdownHook` overloads reject null hooks and additions during shutdown. `removeShutdownHook` and `hasShutdownHook` compare by runnable identity. `clearShutdownHooks` exists for tests. `shutdownExecutor` waits for configured timeout, then forces shutdown if needed.

## State, dependencies, and integration

Global state includes the singleton manager, static daemon executor, synchronized hook set, and `AtomicBoolean shutdownInProgress`. It depends on Guava thread factories, HDDS config utilities, `OzoneConfiguration`, Hadoop `Time`, and SLF4J. It integrates with every service component registering cleanup hooks.

## Risks and test signals

Because the executor is static and shut down after JVM shutdown, tests using reflective execution need careful cleanup. Same-priority hooks run in nondeterministic order. Timed-out hooks are interrupted but may ignore interruption. Tests should cover priority ordering, timeout cancellation, duplicate runnable identity, removal, shutdown-in-progress guards, configured minimum timeout, and exception logging without stopping later hooks.
