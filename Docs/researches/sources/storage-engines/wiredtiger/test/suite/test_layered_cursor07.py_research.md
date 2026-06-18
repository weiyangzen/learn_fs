# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor07.py

Purpose: basic test for `cursor.modify` on layered tables.

Important APIs/types/functions: uses `wiredtiger.Modify`, `cursor.modify`, transactions, direct cursor reads, and disaggregated leader scenario setup.

Control flow: creates a layered table, inserts a long base value for key `1`, then in a transaction applies a modify that appends `A` at offset 130 and asserts `get_value()` returns base plus `A`. It commits and verifies direct read. It then applies a second modify appending `B` at offset 131 and verifies base plus `AB` both before and after commit.

State and persistence behavior: state is an update chain containing a full value followed by modify records. No explicit checkpoint/restart is used, so this targets current-session modify semantics.

Dependencies/integration points: layered update/modify support, value reconstruction, transaction commit, and Python `wiredtiger.Modify` binding.

Risks: only one key and append-style modifications are tested. No timestamp, checkpoint, follower, or eviction behavior is covered.

Test signals: pass means layered cursors can apply sequential modifies and reconstruct the expected value.
