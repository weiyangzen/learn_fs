# sources/storage-engines/tikv/components/raftstore/src/lib.rs

Purpose: Defines the raftstore crate root, feature gates, public modules, selected re-exports, and a small bytes memory accounting helper.

Important APIs and types: Public modules are `coprocessor`, `errors`, `router`, and `store`; `compacted_event_sender` and `RaftRouterCompactedEventSender` are available only under `engine_rocks`. Re-exports expose `RegionInfo`, `RegionInfoAccessor`, `SeekRegionCallback`, `DiscardReason`, `Error`, and `Result`. `bytes_capacity` reports `bytes::Bytes` memory usage as `len()`.

Control flow: There is no runtime control flow beyond `bytes_capacity`. The crate attributes enable nightly features used by raftstore internals and raise recursion limits for generated or deeply nested types.

State and persistence: No durable state is owned here. The `bytes_capacity` helper is used for metrics and treats deserialized raft-message bytes as having capacity equal to length, avoiding dependence on protobuf-generated `Bytes` internals.

Dependencies and integration points: This is the import surface for other TiKV components. It binds raftstore's error type and coprocessor region-info traits into a stable external API, while module declarations make the store, router, and coprocessor subtrees available.

Risks: Crate-level nightly features (`min_specialization`, `box_patterns`, `type_alias_impl_trait`, `impl_trait_in_assoc_type`) tie compilation to a compatible nightly toolchain. `bytes_capacity` underestimates or abstracts real allocation capacity for non-deserialized `Bytes`, but the comment scopes it to raft message memory metrics.

Test signals: No direct tests are present. Compilation of downstream modules and metric behavior using `bytes_capacity` are the main signals.
