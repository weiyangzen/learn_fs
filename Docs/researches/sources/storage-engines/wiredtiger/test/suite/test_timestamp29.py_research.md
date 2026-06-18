<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp29.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp29.py

Purpose: Tests setting, querying, and statistics for the stable disaggregated schema epoch timestamp.

Important APIs/types/functions: `test_timestamp29` uses `conn.set_timestamp('stable_disaggregated_schema_epoch=...')`, `conn.query_timestamp('get=stable_disaggregated_schema_epoch')`, statistics cursor reads for `stat.conn.txn_set_ts_stable_disagg_epoch` and `_upd`, and retry-aware `assertStatEqual`.

Control flow: The test verifies the default epoch is 0, sets it to 10 and 20, repeats 20 as a no-op, rejects a backward move to 10, rejects zero, sets epoch together with oldest/stable timestamps, and then advances it independently to 50 and 100. It checks call and update counters after each stage.

State and persistence behavior: State is connection-level timestamp metadata for a disaggregated schema epoch plus asynchronous statistics counters. The epoch is monotonic and independent of oldest/stable ordering except that it can be set in the same config string.

Dependencies and integration points: Integrates timestamp parser support for a newer timestamp field, query path, stats publication, and disaggregated storage metadata semantics.

Risks: Stats are asynchronous, so the helper retries. Incorrect monotonicity, zero handling, or counter increments would indicate API contract drift.

Test signals: Exact epoch comparisons, expected errors for backward/zero transitions, and call/update stat counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp29.py -->
