# sources/storage-engines/tikv/components/engine_traits/src/flush.rs

Purpose: Tracks memtable flush progress and persists apply-index progress for tablet/raft recovery.

Important APIs and control flow: `SstApplyState` registers applied SST metadata by data CF, returns stale SSTs once a CF is flushed past their apply index, and deletes tracked entries. `FlushState` stores current applied index and per-CF flushed indexes. `PersistenceListener` receives memtable sealed/completed callbacks, records `(cf, apply_index, smallest_seqno)` progress, merges flushed progress by CF when flush completes, persists it through `StateStorage`, and updates `FlushState`. `StateStorage for RaftEngine` writes flushed index records into a Raft log batch and consumes it synchronously.

State, persistence, and dependencies: In-memory state includes linked flush progress, atomics, and registered SSTs. Durable state is persisted to the Raft engine as flushed indexes. Dependencies include `kvproto::SstMeta`, Raft engine traits, data CF mapping, failpoints, and panic marks.

Integration points, risks, and test signals: Used by multi-tablet recovery, WAL-disabled apply replay, and SST cleanup. Risks include assumptions about one DB writer, out-of-order flush callbacks, panics on missing progress, CF index panics, raft persistence failure unwraps, and race ordering around atomics. Tests cover `SstApplyState`; failpoints and backend flush tests are important for listener correctness.
