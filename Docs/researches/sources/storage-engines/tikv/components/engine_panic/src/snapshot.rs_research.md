# sources/storage-engines/tikv/components/engine_panic/src/snapshot.rs

Purpose: Panic skeleton for read snapshots and snapshot iterators.

Important APIs and types: `PanicSnapshot` implements `Snapshot`, `Peekable`, `Iterable`, `CfNamesExt`, and `SnapshotMiscExt`. `PanicSnapshotIterator` implements `Iterator`; `PanicSnapshotIterMetricsCollector` implements iterator metrics.

Control flow and state: Point reads, iterator creation, CF names, sequence number, iterator movement/access, and metrics all panic. No read view state exists.

Dependencies and integration: Associated snapshot type for `PanicEngine`; mirrors real snapshot APIs consumed by TiKV read paths.

Risks: Runtime use panics.

Test signals: No tests.
