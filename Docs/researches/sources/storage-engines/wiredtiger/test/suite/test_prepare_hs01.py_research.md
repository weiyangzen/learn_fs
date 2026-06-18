# sources/storage-engines/wiredtiger/test/suite/test_prepare_hs01.py

Purpose: verifies history-store eviction works correctly when many prepared updates are present and older committed versions must remain readable.

Important APIs and types: `SimpleDataSet`, `make_scenarios`, `conn_config` with small cache and eviction update thresholds, helper methods `check` and `prepare_updates`, timestamped reads, and multiple independent sessions with prepared transactions.

Control flow: the test populates a large table, checkpoints, commits many large values at timestamp 2, then opens three sessions and prepares ranges of updates at timestamp 3. It reads at timestamp 2 to ensure committed values come from history store rather than prepared values, closes prepared sessions to roll them back, and reads again at timestamp 3.

State and persistence behavior: stable timestamp 1 pins history, committed updates are evicted into history store, and prepared updates are present but unresolved. Closing sessions aborts the prepared transactions, returning the latest visible state to the committed values.

Dependencies and integration points: cache pressure, eviction, history store, prepared updates, timestamp visibility, and row/column formats.

Risks: large loops can be time-sensitive under slow eviction. The test ignores known long eviction stdout warnings.

Test signals: every checked key returns the committed byte value and never the prepared byte value before and after aborting prepared sessions.
