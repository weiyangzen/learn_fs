# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/lock/ReadWriteLockable.java

## Purpose

`ReadWriteLockable` is a minimal interface for objects that expose explicit read and write lock/unlock methods.

## APIs and control flow

The API consists of `readLock`, `readUnlock`, `writeLock`, and `writeUnlock`. It does not define ownership, reentrancy, interruption, or closeable guard semantics.

## State, dependencies, and integration

The interface has no state or dependencies. Implementations integrate with Ozone components that want to expose locking without leaking their concrete lock type.

## Risks and test signals

The API is easy to misuse because lock and unlock are separate calls rather than scoped resources. Tests should focus on implementations: balanced unlocks, writer exclusion, reader concurrency, and behavior when exceptions occur inside protected sections.
