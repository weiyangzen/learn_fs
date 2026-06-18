# sources/storage-engines/wiredtiger/test/suite/test_cc10.py

Purpose: verifies the obsolete checkpoint-cleanup background thread can be configured with different wait intervals and still performs cleanup.

Important APIs/types/functions: inherits `test_cc_base`, uses `make_scenarios`, config `checkpoint_cleanup=[wait=...,file_wait_ms=...]`, verbose checkpoint cleanup output filtering, `time.sleep`, and stats `checkpoint_cleanup_pages_visited`, `checkpoint_cleanup_pages_evict`, `checkpoint_cleanup_pages_removed`.

Control flow: create and populate 1,000 rows at timestamp 1, set oldest/stable to 1, update all rows at timestamp 10, set stable to 10 and checkpoint to create HS content, advance oldest to 10 making it obsolete, sleep 5 seconds so the background thread can run, force/wait for cleanup progress, and assert pages were visited and either evicted or removed.

State/persistence behavior: creates obsolete history-store entries and expects background cleanup scheduling to act on them under varied interval configs.

Dependencies/integration: background checkpoint cleanup thread, timing config, history store, stats, and verbose output handling.

Risks/test signals: timing-sensitive because it relies on sleep plus stat progress. Failure means cleanup did not run or did not remove obsolete content.
