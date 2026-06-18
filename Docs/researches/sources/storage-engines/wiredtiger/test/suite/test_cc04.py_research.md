# sources/storage-engines/wiredtiger/test/suite/test_cc04.py

Purpose: negative checkpoint-cleanup test ensuring pages that are not obsolete are visited but not cleaned.

Important APIs/types/functions: inherits `test_cc_base`, `SimpleDataSet`, `large_updates`, `wait_for_cc_to_run`, and connection stats `checkpoint_cleanup_pages_evict`, `checkpoint_cleanup_pages_removed`, and `checkpoint_cleanup_pages_visited`.

Control flow: create `table:cc04`, pin oldest/stable to 1, perform several rounds of 10,000-row timestamped large updates at timestamps 10 through 70, forcing checkpoint cleanup after selected rounds. After every cleanup, assert no pages were evicted or removed by cleanup while pages were visited.

State/persistence behavior: updates create history-store candidates, but oldest timestamp stays pinned so older versions are still required and must not be removed.

Dependencies/integration: timestamp visibility, history-store retention, checkpoint cleanup selection logic, and stats.

Risks/test signals: if cleanup becomes over-aggressive, removal/eviction stats become nonzero. The test is workload-heavy but straightforward.
