<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower06.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_follower06.py

Purpose: tests reading pinned history store content on a standby/follower after checkpoint advancement.

Important APIs/types/functions: uses a separate follower connection, timestamped transactions, `disagg_advance_checkpoint`, precise checkpoint config, and a long-running read transaction on the follower.

Control flow: the leader creates a layered table, writes key `"1"` at ts=2 and key `"2"` at ts=3, sets stable/oldest, checkpoints, and advances the follower. The follower begins a read transaction at ts=2 and reads `"1"`. The leader then writes an update at ts=4, advances oldest to 3, checkpoints, and the follower advances again. The still-open follower read transaction resets its cursor and reads `"1"` at ts=2 again.

State and persistence behavior: the follower read transaction pins the history store dhandle/content needed for an older timestamp even after newer checkpoint pickup and obsolete-version movement.

Dependencies/integration points: integrates history store pinning, checkpoint pickup, oldest timestamp advancement, and follower read transactions. Risks include resource pinning semantics changing. Test signal is successful repeated read of `"value1"` at the old timestamp.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_follower06.py -->
