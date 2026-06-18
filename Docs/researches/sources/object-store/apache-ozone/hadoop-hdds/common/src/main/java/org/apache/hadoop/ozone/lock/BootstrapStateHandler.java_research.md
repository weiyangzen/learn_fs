# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/BootstrapStateHandler.java

## Purpose

`BootstrapStateHandler` defines a component interface for exposing a bootstrap-state lock. The nested `Lock` wrapper standardizes read/write acquisition through `UncheckedAutoCloseable` resources.

## APIs and control flow

Implementers return a `Lock` from `getBootstrapStateLock()`. `Lock` is constructed with a `Function<Boolean, UncheckedAutoCloseable>` where `true` means read lock and `false` means write lock. `acquireWriteLock()` and `acquireReadLock()` delegate to the supplier. The comment notes the bootstrap lock should be acquired before opening snapshots to avoid deadlocks.

## State, dependencies, and integration

State is the lock supplier function. It depends on Java `Function` and Ratis `UncheckedAutoCloseable`. Integration points are bootstrap/snapshot workflows that need consistent lock ordering.

## Risks and test signals

The methods declare `InterruptedException`, but the supplier signature cannot throw checked exceptions; implementations must encode interruption in the supplier or wrap it. Tests should verify read/write boolean mapping, close-based unlock behavior, and lock ordering in snapshot-open paths.
