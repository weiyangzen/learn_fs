# sources/storage-engines/tikv/tests/failpoints/cases/test_gc_metrics.rs

Purpose: validates GC compaction-filter metrics and scheduling for transactional and raw key modes.

Important APIs and functions: tests cover creating txn compaction filters, filtering MVCC versions, handling txn GC keys, filtering raw MVCC versions, and handling raw GC keys. Metrics include `GC_COMPACTION_FILTER_PERFORM`, `SKIP`, `FILTERED`, `GC_COMPACTION_FILTER_MVCC_DELETION_MET`, `HANDLED`, and `MVCC_VERSIONS_HISTOGRAM`.

Control flow: builds test engines with compaction settings, writes MVCC/raw version data, runs `TestGcRunner` or starts `GcWorker` auto GC with mock safe point/region info providers, flushes CFs, compacts ranges, sleeps for async scheduling, then asserts metric counters.

State and persistence: RocksDB write/default CFs hold encoded MVCC or API v2 raw versions. Region metadata is synthesized for auto GC.

Dependencies and integration: uses GC worker internals, Rocks flush/compact APIs, API v2 raw encoding, coprocessor region info accessors, and transaction test helpers.

Risks and test signals: metric resets are required to avoid cross-test contamination. Signals enforce both filtering behavior and observability counters.
