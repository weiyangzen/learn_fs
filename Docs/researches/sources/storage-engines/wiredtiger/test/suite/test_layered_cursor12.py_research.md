# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor12.py

Purpose: verifies follower cursors see correct data after checkpoint advances, including existing unpositioned cursors, updated/deleted keys, interleaved stable/ingest data, search_near changes, read timestamp visibility, bounds, tombstone persistence, and leader behavior.

Important APIs/types/functions: helpers format keys/values, insert/remove on leader and follower, `do_checkpoint`, `scan_keys`, `scan_kv`; uses `disagg_advance_checkpoint`, cursor `search`, `search_near`, `bound`, `reset`, timestamped transactions, and leader/follower connections.

Control flow: setup creates paired leader/follower layered tables. Tests cover: an existing reset cursor seeing all data after a checkpoint adds odd keys; updated values becoming visible after checkpoint; removed leader keys disappearing; positioned local-key cursor finding newly checkpointed data; interleaved even stable keys plus odd local/checkpointed keys; search_near becoming exact after a key is added in a later checkpoint; read timestamps seeing checkpoint 1 vs checkpoint 2 contents; bounds preserved/reapplied after reset and checkpoint; new data inside bounds appearing; local follower tombstones hiding keys across later checkpoint advances; and leader cursors seeing leader writes across checkpoints.

State and persistence behavior: stable checkpoint data, follower ingest writes, follower tombstones, bounds state, and read-timestamp visibility all interact. Several tests model production replication by applying leader operations to the follower ingest table before checkpoint pickup.

Dependencies/integration points: follower checkpoint pickup, layered cursor merge/reopen behavior, timestamp visibility, search/search_near, bounds, tombstones, and leader/follower role semantics.

Risks: some bounds tests reset and reapply bounds because reset clears bounds, so preservation is partly manual. `scan_kv` is defined but unused.

Test signals: pass means checkpoint advances update follower cursor visibility correctly without losing local deletes, bounds expectations, timestamp isolation, or leader current-state visibility.
