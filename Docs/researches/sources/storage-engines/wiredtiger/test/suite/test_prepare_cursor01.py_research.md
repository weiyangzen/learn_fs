# sources/storage-engines/wiredtiger/test/suite/test_prepare_cursor01.py

Purpose: validates `WT_CURSOR.next` and `WT_CURSOR.prev` behavior when cursor movement encounters prepared inserts, updates, and removes. It runs row-store/table scenarios under read-committed and snapshot isolation, while timestamp hooks are disabled so exact prepare, commit, and durable timestamps are controlled by the test.

Important APIs and types: `wttest.WiredTigerTestCase`, `SimpleDataSet`, `make_scenarios`, `wiredtiger.WT_NOTFOUND`, `wiredtiger.WiredTigerError`, session `begin_transaction`, `prepare_transaction`, `timestamp_transaction`, `commit_transaction`, cursor `search`, `next`, `prev`, `insert`, `update`, `remove`, `get_key`, and `get_value`.

Control flow: the test creates keys 2-50, then cycles through four scenarios: prepared insert at both ends, prepared update at both ends, prepared remove at both ends, and prepared remove inside the key range. For each scenario, it positions four readers: before the prepare timestamp, between prepare and commit, after commit, and non-timestamped. It asserts prepare conflicts while the update is unresolved, then commits the prepared transaction and verifies timestamp visibility and cursor position recovery.

State and persistence behavior: all state is local to one table, but the test stresses update chains with prepared state and timestamp visibility. It verifies that prepared updates block reads at and after the prepare timestamp until resolution, that pre-prepare readers keep seeing older state, and that after commit the resolved insert/update/remove is visible according to commit timestamp.

Dependencies and integration points: this is a cursor-navigation regression test integrated with WiredTiger timestamp semantics, prepare conflict detection, and the Python scenario runner. It deliberately excludes column-store scenarios through `include=keep` because the scenario matrix only keeps non-recno keys.

Risks: cursor state after a prepare conflict is subtle; the test explicitly moves the conflicted cursor in the opposite direction before retrying, guarding against stale positioning and repeated-conflict bugs. Timestamp changes must remain ordered or the assertions become misleading.

Test signals: success is no unexpected `WiredTigerError`, expected prepare conflicts on unresolved prepared records, correct `WT_NOTFOUND` at range boundaries, and exact key/value checks after commit.
