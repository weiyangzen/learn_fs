# sources/storage-engines/tikv/components/snap_recovery/src/region_meta_collector.rs

Purpose: scans local raft metadata and streams region metadata to BR during snapshot recovery.

Important APIs and types: `RegionMetaCollector<EK, ER>` owns engines, an unbounded sender, and a worker handle. `CollectWorker` performs the scan. `LocalRegion` groups optional `RaftLocalState`, `RaftApplyState`, and `RegionLocalState`, and converts to recoverdata `RegionMeta`.

Control flow: `start_report` spawns `collector_region_meta`; `CollectWorker::collect_report` scans KV `CF_RAFT` between `REGION_META_MIN_KEY` and `REGION_META_MAX_KEY`, records keys with `REGION_STATE_SUFFIX`, loads raft/apply/region states for each region, skips tombstones, requires raft and apply state, converts to `RegionMeta`, increments `collect_meta`, and sends to BR. `wait` joins the worker thread.

State and persistence behavior: read-only inspection of KV and raft engine metadata. Sends transient protobufs over mpsc. `to_region_meta` chooses peer id as the max peer id in region peer list and records epoch version, tombstone flag, key range, hard-state term, and last index.

Dependencies and integration points: used by `RecoveryService::read_region_meta`. Depends on engine traits, raft server protobufs, `keys` region metadata encoding, and recovery metrics.

Risks: missing raft/apply state for a non-tombstone region is treated as an error and can fail collection. `to_region_meta` unwraps region state, peers, raft state, and apply state, so prevalidation must remain aligned. Large region counts are buffered in memory before per-region loads.

Test signals: no direct unit tests in this file.
