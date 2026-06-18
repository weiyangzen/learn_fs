# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable08.py

Purpose: validates that RTS is a no-op when the stable timestamp is advanced to include all updates. It covers large tables across row/column formats, in-memory/disk modes, prepared/non-prepared updates, and RTS worker counts.

Important APIs/types/functions: uses the shared RTS base class, `SimpleDataSet`, `conn.set_timestamp`, `large_updates`, `check`, optional `session.checkpoint`, `conn.rollback_to_stable`, and RTS statistics including calls, history-store removal, update aborts, key removal/restoration, and pages visited.

Control flow: creates `table:rollback_to_stable08` with 10,000 rows, pins oldest/stable to 10, writes four full-table versions at 20/30/40/50, verifies all versions, advances stable to include the last write (60 for prepared, 50 for non-prepared), checkpoints disk-backed content, runs RTS, then verifies all historical versions remain readable.

State and persistence behavior: checkpointing persists the newest value, but because stable includes it, RTS should not discard data or history. In-memory cases avoid checkpointing and should report zero pages visited for some counters while still exercising the API path.

Dependencies and integration points: uses WiredTiger statistics and shared helper timestamp rules. It complements tests that delete unstable data by proving RTS does not over-prune stable histories.

Risks: off-by-one timestamp errors in prepared mode would make the stable update appear unstable. Large row count makes the test useful for traversal but can be slow in stressed environments.

Test signals: one RTS call, zero `hs_removed`, zero `upd_aborted`, zero key removal/restoration, and mode-dependent pages-visited expectations. Visibility checks confirm all values survive.
