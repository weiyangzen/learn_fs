# sources/storage-engines/tikv/src/import/sst_service.rs

## Purpose
Implements the gRPC `ImportSst` service that powers TiDB Lightning/BR physical import: upload/download/apply/ingest SST or KV files, compact ranges, detect duplicates, suspend imports, and manage force-partition ranges.

## Important APIs, Types, and Functions
`ImportSstService<E>` stores config manager, local tablets, engine, resizable import runtime, `SstImporter`, download limiter, ingest latches, raft-entry limits, region info accessor, throttled raft writer, optional raftstore-v2 store meta/resource manager, suspend deadline, memory limit, and force partition range manager. `RequestCollector` batches `Modify` operations into `WriteData` while deduplicating write-CF keys by latest commit ts and default-CF exact encoded keys. Helper functions include `check_import_resources`, `transfer_error`, `convert_join_error`, `check_local_region_stale`, `prepare_write`, and `download_request_dispatcher`. The `impl_write!` macro implements streaming transactional and raw write RPCs.

## Control Flow
`new` builds a runtime with TLS engine hooks, starts importer mode checks, writer GC, config tick, and adjusts worker count. Upload streams require a meta first chunk, create an importer file, resource-check, append data chunks, then finish. Download variants validate request shape, resource-check, locate tablet, build encryption/resource limiting options, and call importer download functions. Apply downloads KV files, rewrites them, feeds `RequestCollector`, drains batches through `ThrottledTlsEngineWriter`, and joins in-flight write tasks. Ingest/multi-ingest delegate to `ingest.rs`. Duplicate detect obtains a snapshot then streams detector responses. Switch mode handles singleton RocksDB config changes or range-scoped v2 import-mode markers. Force partition add/remove updates manager state and add triggers targeted compactions around range boundaries.

## State and Persistence Behavior
The service owns long-lived runtime/config/importer/throttle/suspend/latch state. Persistent effects include uploaded local files, downloaded/re-written SST files, raft-applied KV writes, ingested SST files, compactions, mode/range markers in importer state, and force-partition ranges with TTL. Metrics record RPC counts/durations, upload chunks, apply/download queueing, errors, and RocksDB config gauges.

## Dependencies and Integration Points
Integrates `grpcio`, kvproto `import_sstpb`, local tablets, raftstore region access, raftstore-v2 store meta, resource control, encryption metadata, external storage through `sst_importer`, RocksDB compaction traits, and TiKV storage error translation. It is the central service boundary for physical import clients.

## Risks and Edge Cases
Resource gating rejects on abnormal disk status or high memory pressure after a jittered sleep to avoid retry storms. `RequestCollector` must prevent duplicated write-CF keys in a raft request because resolved-ts observer can panic; it sets `avoid_batch` UUID behavior. Apply chunks are split at half the raft-entry size with extra wire-size accounting, but huge individual modifies can still produce larger single requests by design for liveness. `prepare_write` filters non-put/delete write records and tags Lightning physical import writes for CDC ignore behavior. Several RPCs spawn background tasks, so cancellation semantics depend on stream/task behavior. Batch download validation is strict about region/epoch/cf/end-key consistency, with special allowance for write+default mix only on latest-MVCC path. `duplicate_detect` unwraps `DuplicateDetector::new`, so construction errors could panic in the task.

## Test Signals
Unit tests cover `RequestCollector` dedup/filter/batching behavior, raft request size limits, huge-write liveness, write/default CF semantics, and `check_local_region_stale` epoch cases. Other behavior is covered indirectly in importer/integration tests. Direct gaps include resource-pressure paths, suspend RPC bounds, download variants, force partition compaction side effects, and duplicate detector construction failures.
