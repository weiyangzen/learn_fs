# sources/storage-engines/wiredtiger/test/suite/test_hs25.py

Purpose: verifies that reconciliation/eviction handles a prepared update chain correctly when adjacent keys have different history-store requirements. The test focuses on the update structure for each key when prepared updates are present but ignored by an eviction reader.

Important APIs and functions: `test_hs25` extends `wttest.WiredTigerTestCase`; `make_scenarios` runs column-store recno (`r`) and integer row-store (`i`) variants. The main API calls are `set_timestamp`, `session.create`, `begin_transaction`, `commit_transaction`, `prepare_transaction`, `rollback_transaction`, and a debug cursor opened with `debug=(release_evict)`.

Control flow: the test pins oldest and stable timestamps to 1, creates `table:test_hs25`, writes key 1 and key 2 at timestamp 2, advances key 2 to timestamp 3, then starts a prepared transaction on key 1 containing two in-memory updates. A second session begins `ignore_prepare=true`, opens the eviction cursor, reads key 1 as the committed old value and key 2 as the newer committed value, then rolls back both sessions.

State and persistence behavior: the prepared transaction is deliberately not committed; its updates must not be surfaced to the ignore-prepare eviction path as committed history. Eviction is the persistence signal because it drives reconciliation and update-chain processing without requiring an explicit checkpoint.

Dependencies and integration points: uses the WiredTiger Python test harness, timestamp helpers from `wttest`, and the debug eviction cursor path. It integrates with history-store reconciliation and prepared transaction visibility.

Risks and edge cases: failures would suggest prepared updates can corrupt per-key update-chain state or leak into eviction reads. The test is narrow: only two key formats are covered, and it relies on debug eviction behavior rather than verifying on-disk history-store records directly.

Test signals: passing assertions are exact value reads through the eviction cursor: key 1 remains `a`, key 2 is `b`; no statistics are checked.
