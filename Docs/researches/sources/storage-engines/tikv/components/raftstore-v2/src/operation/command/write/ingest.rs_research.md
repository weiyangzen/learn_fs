# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/write/ingest.rs

## Purpose
Handles raftstore-v2 ingest-SST write application and periodic cleanup of stale imported SST files.

## Important APIs, Types, And Functions
`StoreFsmDelegate::on_cleanup_import_sst` schedules periodic cleanup ticks. `Store::on_cleanup_import_sst` scans importer state and routes stale SSTs by region. `Peer::on_cleanup_import_sst` filters SSTs whose epochs are stale relative to the peer flushed epoch and schedules tablet cleanup. `Apply::apply_ingest` validates, ingests, tracks, and accounts SST files during apply.

## Control Flow
The store cleanup tick measures importer total size, lists API v2 SSTs, groups them by region id, and sends `PeerMsg::CleanupImportSst` to live peers. If a peer mailbox is disconnected and the router is not shutting down, it filters out SSTs overlapping current import ranges and schedules direct tablet cleanup. A peer receiving cleanup compares SST region epochs with its flushed epoch and deletes/schedules only stale files. During apply, each SST is checked against region bounds, validated by importer metadata, skipped if log recovery already applied that CF/index, flushed before ingest, ingested into the local tablet, registered in `SstApplyState`, bucket stats and metrics are updated, and per-CF SST applied indexes are recorded.

## State And Persistence Behavior
Ingest modifies tablet data by external SST ingestion after flushing pending writes. Applied SST metadata is registered in `SstApplyState` so later cleanup can reason about imported files. `push_sst_applied_index` records per-CF apply trace information. Cleanup removes stale importer files and updates importer-size metrics but does not alter raft region state.

## Dependencies And Integration Points
Depends on `sst_importer`, `check_sst_for_ingestion`, region epoch utilities, tablet cleanup scheduler, importer range overlap checks, store ticks, `ApplyRes` SST applied index propagation, bucket statistics, and PD store-size metrics.

## Risks And Edge Cases
Importer validation failure for a corrupt SST panics, while region-bound check failure deletes the offending SST and returns an apply error. Cleanup must not remove files still in an active import range. Ingest cannot batch across regions in v2, so apply flushes before ingest. Log recovery can skip already applied CF indexes.

## Test Signals
No local tests are defined here. Signals include `ingest_sst` counters, importer size gauge, logs for stale cleanup, `SstApplyState` registrations/deletions, bucket ingest stats, and failpoints around cleanup scheduling and apply ingest.
