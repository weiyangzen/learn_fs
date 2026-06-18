# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable18.py

Purpose: tests RTS over an evicted page containing a stable update followed by an unstable remove. It covers row/column key formats, prepared/non-prepared updates, and worker counts.

Important APIs/types/functions: extends the shared RTS base; uses `SimpleDataSet`, `large_updates`, `large_removes`, `check`, an eviction cursor opened with `debug=(release_evict)`, `conn.rollback_to_stable`, and stats for calls and aborted updates.

Control flow: creates a logged-disabled table, pins oldest/stable to 10, writes value at 20, removes all rows at 30, verifies both states, opens a debug eviction cursor and resets it to force reconciliation, sets stable to include only the update (30 for prepared or 20 for non-prepared), runs RTS, then checks the value is visible again.

State and persistence behavior: eviction forces the update/remove chain to disk or reconciled state before RTS. The stable state is the pre-remove value, so RTS must abort the remove and restore visibility.

Dependencies and integration points: depends on WiredTiger debug eviction cursor support and the shared helper's prepared transaction handling.

Risks: eviction may be fragile if page layout changes or if the cursor does not actually trigger reconciliation. The test uses 10,000 rows to improve eviction/reconciliation likelihood.

Test signals: after RTS all rows read as the original value at timestamp 30, one RTS call, and `upd_aborted == nrows`.
