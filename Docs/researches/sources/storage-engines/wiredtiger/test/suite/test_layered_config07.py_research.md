# sources/storage-engines/wiredtiger/test/suite/test_layered_config07.py

Purpose: directly exercises internal page-log APIs used by disaggregated storage, independent of table operations.

Important APIs/types/functions: class mixes in `DisaggConfigMixin`; uses `conn.get_page_log('palite')`, `PageLogCompleteCheckpointArgs`, `pl_complete_checkpoint`, `pl_open_handle`, `PageLogPutArgs`, `WT_PAGE_LOG_DELTA`, `plh_put`, `PageLogGetArgs`, `plh_get`, `PageLogDiscardArgs`, `plh_discard`, and `terminate`.

Control flow: it completes a synthetic checkpoint, opens a page-log handle, writes full and delta records for page 20 and page 21, then writes a second delta for page 20 chained to the previous delta. It reads page 20 and page 21 at specific LSNs and asserts the returned full+delta lists match expected byte payloads. Finally it discards page 20 with base/backlink LSNs and asserts the discard operation receives a later LSN.

State and persistence behavior: page-log state is identified by file/page IDs, LSNs, base LSNs, backlink LSNs, and delta flags. The test validates chaining and retrieval order plus discard record allocation.

Dependencies/integration points: PALite/page-log extension plumbing, WiredTiger Python page-log bindings, disaggregated helper configuration.

Risks: direct internal API test; application-facing behavior is not covered. Incorrect LSN state would fail assertions or retrieval ordering.

Test signals: pass means basic complete-checkpoint, put/get delta chains, and discard APIs work through Python bindings.
