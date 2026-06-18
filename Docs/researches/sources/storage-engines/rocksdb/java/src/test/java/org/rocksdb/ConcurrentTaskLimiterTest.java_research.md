# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/ConcurrentTaskLimiterTest.java

## Purpose

Tests basic Java wrapper behavior for a native `ConcurrentTaskLimiter`.

## Important APIs, control flow, and dependencies

`beforeTest` creates `ConcurrentTaskLimiterImpl` with a name and max outstanding task count. Tests read `name`, `outstandingTask`, `setMaxOutstandingTask`, and `resetMaxOutstandingTask`; `afterTest` closes the limiter.

## State, persistence, risks, and test signals

No DB state is persisted. The native limiter tracks outstanding task state, but no tasks are scheduled, so the expected count remains zero. Risks include ownership/lifetime bugs and broken fluent return identity. Signals are name equality, zero outstanding tasks, and setter methods returning the same wrapper.
