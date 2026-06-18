# sources/storage-engines/tikv/components/engine_traits/src/options.rs

Purpose: Defines generic read, write, and iterator option structs passed across engine implementations.

Important APIs and control flow: `ReadOptions` controls fill-cache. `WriteOptions` controls sync, no-slowdown, and WAL disabling. `SeekMode` selects total-order or prefix seek. `IterOptions` stores lower/upper key builders, prefix-same-as-start, fill-cache, timestamp hints, key-only mode, seek mode, and max skippable internal keys, with setters for slice/vector bounds and timestamp bound conversion.

State, persistence, and dependencies: Options are transient request state. Write options can affect persistence guarantees through sync and WAL behavior; iterator options affect scan visibility/performance.

Integration points, risks, and test signals: Used by point reads, iterators, write batches, and SST readers. Risks include underflow in excluded max timestamp when ts is zero, reserved-prefix-length mistakes, prefix mutation after bound construction, key-only being backend-specific, and options silently ignored by adapters. Unit tests cover timestamp hint conversion.
