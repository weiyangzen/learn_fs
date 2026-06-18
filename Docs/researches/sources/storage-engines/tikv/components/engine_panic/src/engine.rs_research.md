# sources/storage-engines/tikv/components/engine_panic/src/engine.rs

Purpose: Defines `PanicEngine`, the central panic-based implementation of core key-value engine traits and iterator traits.

Important APIs and types: `PanicEngine` implements `KvEngine`, `Peekable`, `SyncMutable`, and `Iterable`; `PanicEngineIterator` implements `Iterator`; `PanicEngineIterMetricsCollector` implements `IterMetricsCollector`; iterator metrics are exposed through `MetricsExt`.

Control flow and state: Snapshot creation, sync, downcast, point reads, writes, deletes, range deletes, iterator creation, seeking, movement, key/value access, and metrics all panic. There is no storage state.

Dependencies and integration: Imports broad `engine_traits` APIs and uses `PanicSnapshot`, `PanicDbVector`, and `PanicWriteBatch` as associated types in other modules.

Risks: This is a compile-time template only. It intentionally does not provide a safe no-op implementation, so accidental use fails loudly.

Test signals: No local tests; compile-time trait coverage is the intended validation.
