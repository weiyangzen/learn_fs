# sources/storage-engines/tikv/tests/failpoints/cases/test_auto_compaction.rs

Purpose: validates GC worker auto-compaction candidate detection and MVCC-read-aware prioritization.

Important APIs and functions: `test_gc_worker_auto_compaction_with_failpoints` creates multiple split regions with different redundant MVCC/tombstone patterns and observes failpoint callbacks for candidate ranges. `test_mvcc_aware_compaction_prioritization` records reads in `MVCC_READ_TRACKER` and checks `FIRST_COMPACTION_CANDIDATE_REGION`.

Control flow: configures low thresholds, disables RocksDB auto compactions, writes version/delete patterns via KV prewrite/commit, flushes `CF_WRITE`, waits for auto compaction thread failpoints, and asserts expected regions are selected.

State and persistence: persists MVCC histories in write CF and uses PD/cluster GC safe points. Candidate selection is based on flushed table properties and tracker state.

Dependencies and integration: uses `test_raftstore`, `kvproto::kvrpcpb`, `engine_traits::MiscExt`, `ReadableDuration`, GC auto-compaction internals, and failpoint callbacks.

Risks and test signals: one branch tolerates environments where the thread cannot start. The second test contains an apparent duplicate assignment to `mvcc_scan_threshold`, with the latter disabling age factor. Signals candidate scoring and read-aware priority regressions.
