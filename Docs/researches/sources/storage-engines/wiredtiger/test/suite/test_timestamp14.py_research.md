<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp14.py

Purpose: Exercises WiredTiger global timestamp queries for `all_durable`, `oldest_reader`, `oldest_timestamp`, and `pinned`, across row-store integer keys and column-store recno keys. It verifies that running transactions, prepared transactions, read timestamps, and no-timestamp transactions affect global timestamp state as documented.

Important APIs/types/functions: `test_timestamp14` extends `wttest.WiredTigerTestCase` and `suite_subprocess`; scenarios are built with `make_scenarios`. The tests use `conn.query_timestamp()`, `conn.set_timestamp()`, `session.begin_transaction()`, `session.timestamp_transaction()`, `session.prepare_transaction()`, `session.commit_transaction()`, cursors, and `assertTimestampsEqual`.

Control flow: `test_all_durable_old` walks historical all-committed/all-durable cases: no timestamp, single timestamped commit, lower in-flight commit timestamp, out-of-order pending timestamp, and no-timestamp work. `test_oldest_reader` opens multiple sessions to prove only timestamped readers pin `oldest_reader`. `test_pinned_oldest` moves oldest past an active reader and checks `pinned`. `test_all_durable` adds prepared-transaction durable timestamp cases and repeated `commit_timestamp` setting. `test_all` combines oldest, reader, pinned, and all-durable movement in one scenario.

State and persistence behavior: State is in connection-wide timestamp metadata plus transactional updates to temporary tables. The file does not restart WiredTiger, but it depends on precise live transaction accounting and prepared transaction durable timestamp tracking.

Dependencies and integration points: Integrates with the Python WiredTiger test harness, timestamp string helpers, scenario expansion, and transaction manager internals surfaced through `query_timestamp`. It is a direct regression surface for timestamp visibility, checkpoint safety, and oldest/pinned timestamp advancement.

Risks: The tests are sensitive to subtle timestamp ordering semantics; changes in prepared transaction accounting can make apparently unrelated assertions fail. Multiple sessions share the same table, so leaked transactions or cursors would poison later timestamp queries.

Test signals: Strong signal comes from exact timestamp equality checks after each transition, including all-durable moving backward for lower in-flight timestamps and pinned falling back to oldest after readers close.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp14.py -->
