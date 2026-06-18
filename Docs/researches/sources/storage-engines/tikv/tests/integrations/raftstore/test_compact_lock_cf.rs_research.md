# sources/storage-engines/tikv/tests/integrations/raftstore/test_compact_lock_cf.rs

Purpose: validates periodic lock CF compaction is triggered only after the configured byte threshold is exceeded.

Important APIs and functions: `flush` flushes `CF_LOCK` for all engines. `flush_then_check` sleeps for two configured intervals and inspects `DBStatisticsTickerType::CompactWriteBytes`. `test_compact_lock_cf` sets `lock_cf_compact_interval`, `lock_cf_compact_bytes_threshold`, disables lock CF auto compaction, writes lock CF keys, and verifies compaction statistics.

Control flow: after cluster startup, the test writes two small batches that remain below threshold and confirms no compact write bytes. A third batch crosses the threshold and the post-flush wait must observe compact write bytes.

State and persistence: data is written into lock CF and flushed into SSTs. The main observed state is RocksDB statistics counters, not final key values.

Dependencies and integration points: integrates raftstore config, RocksDB CF flush, RocksDB statistics, and the server cluster harness.

Risks: statistics counters can be affected by unrelated compactions if isolation breaks. Timing depends on the compaction interval and CI scheduling. The test uses a one-node server cluster, so it does not cover multi-peer coordination.

Test signals: `CompactWriteBytes` remains zero for sub-threshold flushed data and becomes nonzero after threshold-exceeding data is flushed and the periodic worker runs.
