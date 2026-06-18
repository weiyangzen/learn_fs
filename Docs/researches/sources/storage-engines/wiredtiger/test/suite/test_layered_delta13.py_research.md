# sources/storage-engines/wiredtiger/test/suite/test_layered_delta13.py

Purpose: verifies eviction with uncommitted updates in a disaggregated file table and checks that writes still reach cache/write statistics without committing unstable data.

Important APIs and functions: `test_layered_delta13` uses `WiredTigerCursor` and `statistic_uri` imports from `helper`, `stat.dsrc.cache_write`, `debug=(release_evict_page)` eviction cursor behavior, timestamped base writes, and normal transaction control.

Control flow: the test creates a disaggregated file table, writes base rows with timestamps, sets a stable timestamp, opens another session with uncommitted work, and uses a debug eviction session to evict/search a key. It then reads data-source cache write statistics and asserts writes occurred.

State and persistence behavior: base rows are stable, while the concurrent transaction remains uncommitted. The eviction path must handle dirty/uncommitted state without persisting it incorrectly, while still exercising cache write behavior.

Dependencies and integration: integrates disaggregated file tables, debug eviction hooks, transaction isolation, timestamp state, and data-source statistics. Risks include evicting uncommitted updates into durable page state, failing eviction under dirty pages, or statistics not reflecting writes. Test signals are a positive `cache_write` statistic after the eviction exercise.
