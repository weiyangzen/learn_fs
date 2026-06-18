# sources/storage-engines/wiredtiger/test/suite/test_hs30.py

Purpose: verifies history-store behavior for non-timestamped tables, both logged and unlogged, especially when long-running snapshot transactions require older non-timestamped values after eviction.

Important APIs and functions: `test_hs30` sets `session_config='isolation=snapshot'`. Scenario axes cover recno/integer key formats, logging on/off, early checkpoint, middle checkpoint, and eviction on/off. Helpers `large_updates` write full-table batches without commit timestamps; `evict` uses `debug=(release_evict)`.

Control flow: the test creates a table with chosen logging, writes `value_a`, optionally checkpoints, opens a snapshot reader that sees `value_a`, writes `value_b` and `value_c`, optionally checkpoints, opens a second reader seeing `value_c`, writes `value_d` and `value_e`, optionally evicts pages, then scans both pinned readers and checks the history-store read statistic.

State and persistence behavior: the key state is transaction-ID-based visibility rather than timestamp visibility. Eviction is expected to move old non-timestamped updates to history only when open snapshots need them.

Dependencies and integration points: depends on connection statistics (`stat.conn.cache_hs_read`), logging configuration, snapshot isolation, and debug eviction. It exercises non-timestamped history-store read paths distinct from timestamped tests.

Risks and edge cases: there is a cleanup bug in the source: `evict_cursor.close()` is called at the end even though `evict_cursor` is local to `evict`; when the path reaches that line it can raise `NameError`. The helper also indexes `evict_cursor[1]` in a loop instead of key `i`, making eviction coverage weaker than intended.

Test signals: reader scans must see `value_a` and `value_c`; with eviction, `cache_hs_read` should be at least `nrows * 2`, and without eviction it should be zero.
